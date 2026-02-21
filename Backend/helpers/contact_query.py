from fastapi import HTTPException, status
from sqlalchemy import select, insert, or_, func
from ..config.database import Contact, async_session, User, Message
from sqlalchemy import or_, select, func, desc, case
from ..config.redis import redis
import json
async def get_contact(sender, reciever):
    async with async_session() as session:
        result = await session.execute(select(Contact).where(Contact.user_id == sender, Contact.contact_id == reciever))
        res1 = result.scalar_one_or_none()
    return res1


async def insert_contact(sender_id, reciever_id):
    res = await get_contact(sender=sender_id, reciever=reciever_id)
    if res is not None:
        return False

    try:
        async with async_session() as session:
            await session.execute(insert(Contact).values(user_id=sender_id, contact_id=reciever_id))
            await session.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to insert contact")



async def get_all_contacts(user_id):
    async with async_session() as session:
        subquery = select(Contact.contact_id).where(Contact.user_id == user_id).subquery()
        result = await session.execute(select(User).where(User.id.in_(select(subquery.c.contact_id))))
        contacts = result.scalars().all()
    return contacts

async def get_contact_python_list(user_id):
    contacts = await get_all_contacts(user_id)
    res = []
    for contact in contacts:
        res.append(contact.username)
    return res


async def get_all_last_msgs(user_id):
    async with async_session() as session:
        latest_msg = (
            select(
            Message,
            func.row_number().over(
                partition_by=func.least(Message.sender_id, Message.receiver_id) + 
                                func.greatest(Message.sender_id, Message.receiver_id),
                order_by=desc(Message.created_at)
            ).label("rn"),
            case(
                (Message.sender_id == user_id, Message.receiver_id),
                else_=Message.sender_id).label("contact_id"),
            case (
                (Message.sender_id == user_id, 1),
                else_ = 0).label("sent"))
            .where(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
            )
            .subquery()
        )

        result = await session.execute(
            select(
                latest_msg.c.content.label("content"),
                latest_msg.c.created_at.label("created_at"),
                latest_msg.c.contact_id,
                latest_msg.c.sent.label("sent"),
                User.username.label("username"),
                User.name.label("name")
            )
            .join(User, User.id == latest_msg.c.contact_id)
            .where(latest_msg.c.rn == 1)
        )
        return result.all()



# The sqlalchemy code query was written by this PostgresSQL command Structure i wrote


# SELECT 
#     m.id, 
#     m.content,
#     ROW_NUMBER() OVER (
#         PARTITION BY LEAST(m.sender_id, m.receiver_id), 
#                      GREATEST(m.sender_id, m.receiver_id)
#         ORDER BY m.created_at DESC
#     ) AS rn,
# 	CASE 
# 	WHEN m.sender_id = 31 THEN m.receiver_id
# 	ELSE m.sender_id 
# 	END
# 	AS contact,
# 	CASE 
# 	WHEN m.sender_id = 31 THEN 1
# 	ELSE 0
# 	END
# 	AS sent
# FROM messages m
# WHERE  (m.sender_id = 31 OR m.receiver_id = 31)
# )
# SELECT u.username, l.content, is_deleted, created_at  from users u
# JOIN last_msg l
# ON u.id = l.contact


async def get_cached_contacts(user_id: int):
    key = f"contacts:{user_id}"
    
    cached = await redis.get(key)
    if cached:
        print(f"cached")
        return json.loads(cached)
    contacts = await get_all_contacts(user_id)
    contacts_data = [{"id": c.id, "username": c.username, "name": c.name} for c in contacts]
    await redis.setex(key, time = 5000, value = json.dumps(contacts_data),)
    return contacts_data


async def invalidate_contacts(user_id: int):
    await redis.delete(f"contacts:{user_id}")
    print(f"deleted")