const API_BASE = "http://localhost:8000";

let contacts = [];
let conversations = [];
let activeChat = null;


function getInitials(name) {
    return name
        .split(" ")
        .map(w => w[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
}

function timeAgo(dateStr) {
    const now = new Date();
    const date = new Date(dateStr);
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return "now";
    if (diff < 3600) return Math.floor(diff / 60) + "m";
    if (diff < 86400) return Math.floor(diff / 3600) + "h";
    return Math.floor(diff / 86400) + "d";
}


async function loadConversations() {
    try {
        const res = await fetch(`${API_BASE}/messages/`, {
            credentials: "include"
        });

        if (!res.ok) {
            if (res.status === 401) {
                window.location.href = "/static/login/login.html";
                return;
            }
            return;
        }

        conversations = await res.json();
        renderConversations();
    } catch (err) {
        console.error("Failed to load conversations:", err);
    }
}

function renderConversations(filter = "") {
    const list = document.getElementById("contact-list");
    const filtered = conversations.filter(c =>
        c.username.toLowerCase().includes(filter.toLowerCase()) ||
        c.name.toLowerCase().includes(filter.toLowerCase())
    );

    if (filtered.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">◯</div>
                <p>No conversations yet</p>
            </div>`;
        return;
    }

    list.innerHTML = filtered.map(c => `
        <li class="contact-item ${activeChat === c.username ? 'active' : ''}" 
            onclick="openChat('${c.username}', '${c.name}')">
            <div class="contact-avatar">${getInitials(c.name)}</div>
            <div class="contact-info">
                <div class="contact-row">
                    <span class="contact-name">${c.username}</span>
                    <span class="contact-time">${timeAgo(c.created_at)}</span>
                </div>
                <p class="contact-last-msg">${c.sent ? "You: " : ""}${c.last_message || ""}</p>
            </div>
        </li>
    `).join("");
}


async function loadContacts() {
    try {
        const res = await fetch(`${API_BASE}/contacts/`, {
            credentials: "include"
        });

        if (!res.ok) return;

        contacts = await res.json();
        renderContacts();
    } catch (err) {
        console.error("Failed to load contacts:", err);
    }
}

function renderContacts() {
    const list = document.getElementById("right-contact-list");

    if (contacts.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">◯</div>
                <p>No contacts yet</p>
            </div>`;
        return;
    }

    list.innerHTML = contacts.map(c => `
        <li class="contact-item-mini" onclick="openChat('${c.username}', '${c.name}')">
            <div class="contact-avatar tiny">${getInitials(c.name)}</div>
            <span>${c.username}</span>
        </li>
    `).join("");
}


function openChat(username, name) {
    activeChat = username;

    document.querySelector(".chat-username").textContent = username;
    document.querySelector(".chat-header .contact-avatar").textContent = getInitials(name);

    renderConversations(document.getElementById("search-contacts").value);

    document.getElementById("messages").innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">◯</div>
            <p>Start a conversation with ${username}</p>
        </div>`;

    document.getElementById("msg-input").focus();
}


async function sendMessage() {
    const input = document.getElementById("msg-input");
    const content = input.value.trim();

    if (!content || !activeChat) return;

    try {
        const res = await fetch(`${API_BASE}/messages/${activeChat}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ content })
        });

        if (res.ok) {
            const messagesDiv = document.getElementById("messages");

            const emptyState = messagesDiv.querySelector(".empty-state");
            if (emptyState) emptyState.remove();

            const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const msgEl = document.createElement("div");
            msgEl.className = "msg sent";
            msgEl.innerHTML = `<p>${content}</p><span class="msg-time">${now}</span>`;
            messagesDiv.appendChild(msgEl);

            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            input.value = "";
            input.style.height = "auto";

            loadConversations();
        } else {
            const data = await res.json();
            console.error("Send failed:", data.detail);
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


async function followUser() {
    const input = document.getElementById("add-username");
    const status = document.getElementById("follow-status");
    const username = input.value.trim();

    if (!username) return;

    try {
        const res = await fetch(`${API_BASE}/contacts/${username}/follow`, {
            method: "POST",
            credentials: "include"
        });

        if (res.ok) {
            status.textContent = `Followed ${username}!`;
            status.className = "status-msg success";
            input.value = "";
            loadContacts(); 
        } else {
            const data = await res.json();
            status.textContent = data.detail || "Follow failed";
            status.className = "status-msg error";
        }
    } catch (err) {
        status.textContent = "Connection error";
        status.className = "status-msg error";
    }
}


async function logout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method: "POST",
            credentials: "include"
        });
    } catch (err) {}
    window.location.href = "/static/login/login.html";
}


document.getElementById("search-contacts").addEventListener("input", function () {
    renderConversations(this.value);
});


document.getElementById("follow-btn").addEventListener("click", followUser);
document.getElementById("logout-btn").addEventListener("click", logout);


async function init() {
    await Promise.all([loadConversations(), loadContacts()]);

    if (conversations.length === 0) {
        document.getElementById("messages").innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">◯</div>
                <p>Select a chat to start messaging</p>
            </div>`;
    }
}

init();