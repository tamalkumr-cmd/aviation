function showToast(msg, ok = false) {
    const t = document.getElementById("toast");
    if (!t) return alert(msg);
    t.textContent = msg;
    t.className = "toast " + (ok ? "ok" : "error");
}

async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    showToast(data.message || data.error, res.ok);

    if (res.ok) setTimeout(() => window.location.href = "/login", 600);
}

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    showToast(data.message || data.error, res.ok);

    if (res.ok) setTimeout(() => window.location.href = "/dashboard", 600);
}