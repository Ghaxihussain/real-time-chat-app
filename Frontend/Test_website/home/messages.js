const WS_BASE = "ws://localhost:7000";
let socket = null;
let msgOffset = 0;
const MSG_LIMIT = 20;
let isLoadingMsgs = false;
let hasMoreMsgs = true;


function connectWebSocket() {
    socket = new WebSocket(`${WS_BASE}/ws/`);

    socket.onopen = () => {
        console.log("[WS] Connected");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === "new_message") {
            console.log("[WS RAW]", event.data);
            if (activeChat && data.from === activeChat.username) {
                appendMessage({ content: data.content, sended: false, created_at: new Date().toISOString() });
            } else {
                highlightConversation(data.from);
            }

            if (typeof loadConversations === "function") loadConversations();
        }
        else if (data.type === "status_change") {
            setContactStatus(data.contact_id, data.status);
        }
    };

    socket.onclose = (e) => {
        console.warn("[WS] Disconnected, reconnecting in 3s...", e.code);
        setTimeout(connectWebSocket, 3000);
    };

    socket.onerror = (err) => {
        console.error("[WS] Error:", err);
        socket.close();
    };
}

const onlineUsers = new Set();

function setContactStatus(username, status) {
    if (status === "online") {
        onlineUsers.add(username);
    } else {
        onlineUsers.delete(username);
    }
    updateStatusDot(username, status);
}

function updateStatusDot(username, status) {
    document.querySelectorAll(`[data-username="${username}"]`).forEach(el => {
        el.classList.toggle("is-online", status === "online");
    });
}

async function loadMessages(username, prepend = false) {
    if (isLoadingMsgs || !hasMoreMsgs) return;
    isLoadingMsgs = true;

    const messagesDiv = document.getElementById("messages");

    let loader = document.getElementById("msg-loader");
    if (!loader) {
        loader = document.createElement("div");
        loader.id = "msg-loader";
        loader.className = "msg-loader";
        loader.textContent = "Loading...";
        messagesDiv.prepend(loader);
    }

    try {
        const res = await fetch(
            `${API_BASE}/messages/${username}/conversation?offset=${msgOffset}&limit=${MSG_LIMIT}`,
            { credentials: "include" }
        );

        if (!res.ok) {
            console.error("Failed to load messages:", res.status);
            return;
        }

        const msgs = await res.json();

        loader.remove();

        if (msgs.length === 0) {
            hasMoreMsgs = false;
            if (msgOffset === 0) {
                messagesDiv.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">◯</div>
                        <p>No messages yet. Say hello!</p>
                    </div>`;
            }
            return;
        }

        if (msgs.length < MSG_LIMIT) hasMoreMsgs = false;

        const prevHeight = messagesDiv.scrollHeight;

        if (prepend) {
            msgs.forEach(msg => prependMessage(msg));
            messagesDiv.scrollTop = messagesDiv.scrollHeight - prevHeight;
        } else {
            const emptyState = messagesDiv.querySelector(".empty-state");
            if (emptyState) emptyState.remove();

            msgs.forEach(msg => appendMessage(msg));
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        msgOffset += msgs.length;

    } catch (err) {
        console.error("Error loading messages:", err);
        if (loader) loader.remove();
    } finally {
        isLoadingMsgs = false;
    }
}


function openChat(username, name) {
    activeChat = {username, name};

    msgOffset = 0;
    hasMoreMsgs = true;

    document.querySelector(".chat-username").textContent = username;
    document.querySelector(".chat-header .contact-avatar").textContent = getInitials(name);

    const messagesDiv = document.getElementById("messages");
    messagesDiv.innerHTML = "";

    messagesDiv.removeEventListener("scroll", onMessagesScroll);
    messagesDiv.addEventListener("scroll", onMessagesScroll);

    loadMessages(username, false);

    if (typeof renderConversations === "function") {
        renderConversations(document.getElementById("search-contacts").value);
    }

    document.getElementById("msg-input").focus();
}


function onMessagesScroll() {
    const messagesDiv = document.getElementById("messages");
    if (messagesDiv.scrollTop < 80 && hasMoreMsgs && activeChat) {
        loadMessages(activeChat.username, true);
    }
}


function appendMessage(msg) {
    const messagesDiv = document.getElementById("messages");

    const emptyState = messagesDiv.querySelector(".empty-state");
    if (emptyState) emptyState.remove();

    const el = createMsgEl(msg);
    messagesDiv.appendChild(el);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function prependMessage(msg) {
    const messagesDiv = document.getElementById("messages");
    const el = createMsgEl(msg);
    const loader = document.getElementById("msg-loader");
    if (loader) {
        loader.insertAdjacentElement("afterend", el);
    } else {
        messagesDiv.prepend(el);
    }
}

function createMsgEl(msg) {
    const el = document.createElement("div");
    el.className = `msg ${msg.sended ? "sent" : "received"}`;

    const time = new Date(msg.created_at).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

    el.innerHTML = `<p>${escapeHtml(msg.content)}</p><span class="msg-time">${time}</span>`;
    return el;
}

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function highlightConversation(username) {
    const items = document.querySelectorAll(".contact-item");
    items.forEach(item => {
        if (item.dataset.username === username) {
            item.classList.add("unread");
        }
    });
}


async function sendMessage() {
    const input = document.getElementById("msg-input");
    const content = input.value.trim();

    if (!content || !activeChat) return;

    appendMessage({ content, sended: true, created_at: new Date().toISOString() });
    input.value = "";
    input.style.height = "auto";

    try {
        const res = await fetch(`${API_BASE}/messages/${activeChat.username}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ content })
        });

        if (!res.ok) {
            const data = await res.json();
            console.error("Send failed:", data.detail);
        } else {
            if (typeof loadConversations === "function") loadConversations();
        }
    } catch (err) {
        console.error("Connection error:", err);
    }
}


document.getElementById("send-btn").addEventListener("click", sendMessage);

document.getElementById("msg-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});


connectWebSocket();