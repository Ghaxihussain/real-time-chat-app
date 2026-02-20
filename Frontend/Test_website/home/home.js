const API_BASE = "http://localhost:7000";

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
        <li class="contact-item ${activeChat && activeChat.username === c.username ? 'active' : ''}" 
            data-username="${c.username}"
            data-name="${c.name}"
            onclick="openChat(this.dataset.username, this.dataset.name)">
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

    applyOnlineStatuses();
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
        <li class="contact-item-mini"
            data-username="${c.username}"
            data-name="${c.name}"
            onclick="openChat(this.dataset.username, this.dataset.name)">
            <div class="contact-avatar tiny">${getInitials(c.name)}</div>
            <span>${c.username}</span>
        </li>
    `).join("");

    applyOnlineStatuses();
}

function applyOnlineStatuses() {
    if (typeof onlineUsers === "undefined") return;
    onlineUsers.forEach(username => {
        document.querySelectorAll(`[data-username="${username}"]`).forEach(el => {
            el.classList.add("is-online");
        });
    });
}


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