const API_BASE = "http://localhost:7000"; 

function showTab(tab) {
    document.getElementById("error").textContent = "";
    document.getElementById("error").style.color = "red";
    const tabs = document.querySelectorAll(".tab");
    tabs.forEach(t => t.classList.remove("active"));

    if (tab === "login") {
        tabs[0].classList.add("active");
        document.getElementById("login-form").classList.remove("hidden");
        document.getElementById("signup-form").classList.add("hidden");
    } else {
        tabs[1].classList.add("active");
        document.getElementById("login-form").classList.add("hidden");
        document.getElementById("signup-form").classList.remove("hidden");
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    try {
        const res = await fetch(`${API_BASE}/auth/signin`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ username, password })
        });

        if (res.ok) {
            window.location.href = "http://localhost:7000/static/home/home.html";
        } else {
            const data = await res.json();
            document.getElementById("error").textContent = data.detail || "Login failed";
        }
    } catch (err) {
        document.getElementById("error").textContent = "Connection error";
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const name = document.getElementById("signup-name").value;
    const username = document.getElementById("signup-username").value;
    const password = document.getElementById("signup-password").value;

    try {
        const res = await fetch(`${API_BASE}/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ username, password, name })
        });

        if (res.ok) {
            const loginRes = await fetch(`${API_BASE}/auth/signin`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ username, password })
            });

            if (loginRes.ok) {
                window.location.href = "http://localhost:7000/static/home/home.html"
            } else {
                showTab("login");
                document.getElementById("error").textContent = "Signup successful! Please login.";
                document.getElementById("error").style.color = "green";
            }
        } else {
            const data = await res.json();
            document.getElementById("error").textContent = data.detail || "Signup failed";
        }
    } catch (err) {
        document.getElementById("error").textContent = "Connection error";
    }
}