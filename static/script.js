// Keep client session state in one place so polling and UI stay in sync.
const state = {
  username: "",
  afterId: 0,
  pollTimer: null,
  usersTimer: null,
};

// Cache DOM references once to avoid repeated queries and reduce UI bugs.
const ui = {
  status: document.getElementById("status"),
  users: document.getElementById("users"),
  messages: document.getElementById("messages"),
  motd: document.getElementById("motd"),
  username: document.getElementById("username"),
  to: document.getElementById("to"),
  text: document.getElementById("text"),
  loginBtn: document.getElementById("loginBtn"),
  sendBtn: document.getElementById("sendBtn"),
};

function setStatus(text, cssClass = "") {
  // Status feedback helps users understand whether actions succeeded.
  ui.status.textContent = text;
  ui.status.className = `status ${cssClass}`.trim();
}

async function api(path, options = {}) {
  // Centralized fetch wrapper keeps request format consistent.
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  return response.json();
}

function appendMessage(msg) {
  // Render each message card and keep the latest messages visible.
  const card = document.createElement("article");
  card.className = "msg";
  card.innerHTML = `
    <div class="meta">${escapeHtml(msg.from)} -> ${escapeHtml(msg.to)} at ${escapeHtml(msg.timestamp)}</div>
    <p class="text">${escapeHtml(msg.text)}</p>
  `;
  ui.messages.appendChild(card);
  ui.messages.scrollTop = ui.messages.scrollHeight;
}

function renderUsers(users) {
  ui.users.innerHTML = "";
  users.forEach((name) => {
    const item = document.createElement("li");
    item.textContent = name;
    ui.users.appendChild(item);
  });
}

async function loadMotd() {
  try {
    // Load dynamic MOTD from server so content can change without redeploy.
    const data = await api("/api/motd");
    ui.motd.textContent = data.motd || "Welcome";
  } catch {
    ui.motd.textContent = "Message not available right now";
  }
}

async function refreshUsers() {
  if (!state.username) {
    return;
  }
  try {
    // Refresh presence list periodically to reflect connected users.
    const data = await api("/api/users");
    renderUsers(data.users || []);
  } catch {
    setStatus("Connected with user list errors", "danger");
  }
}

async function pollMessages() {
  if (!state.username) {
    return;
  }
  try {
    // Ask only for new messages using after_id to avoid duplicates.
    const data = await api(
      `/api/messages?username=${encodeURIComponent(state.username)}&after_id=${state.afterId}`,
    );
    const incoming = data.messages || [];
    incoming.forEach((msg) => {
      appendMessage(msg);
      state.afterId = Math.max(state.afterId, msg.id || 0);
    });
  } catch {
    setStatus("Connected with message sync errors", "danger");
  }
}

async function login() {
  const username = ui.username.value.trim();
  if (!username) {
    setStatus("Enter a username", "danger");
    return;
  }

  try {
    // Login starts the chat session and activates periodic refresh loops.
    const data = await api("/api/login", {
      method: "POST",
      body: JSON.stringify({ username }),
    });
    if (data.error) {
      setStatus(data.error, "danger");
      return;
    }

    state.username = username;
    state.afterId = 0;
    setStatus(`Logged in as ${username}`, "ok");
    ui.messages.innerHTML = "";

    clearInterval(state.pollTimer);
    clearInterval(state.usersTimer);

    // Polling intervals keep chat and user list near real-time.
    await refreshUsers();
    await pollMessages();
    state.pollTimer = setInterval(pollMessages, 1200);
    state.usersTimer = setInterval(refreshUsers, 2000);
  } catch {
    setStatus("Could not reach server", "danger");
  }
}

async function sendMessage() {
  if (!state.username) {
    setStatus("Login first", "danger");
    return;
  }
  const to = ui.to.value.trim() || "all";
  const text = ui.text.value.trim();
  if (!text) {
    return;
  }

  try {
    // Send and then poll immediately so the sender sees fresh state fast.
    const data = await api("/api/send", {
      method: "POST",
      body: JSON.stringify({ from: state.username, to, text }),
    });
    if (data.error) {
      setStatus(data.error, "danger");
      return;
    }
    ui.text.value = "";
    await pollMessages();
  } catch {
    setStatus("Message failed", "danger");
  }
}

function escapeHtml(input) {
  // Escape user-provided content to prevent DOM injection.
  return String(input)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

ui.loginBtn.addEventListener("click", login);
ui.sendBtn.addEventListener("click", sendMessage);
ui.text.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});

window.addEventListener("beforeunload", async () => {
  if (!state.username) {
    return;
  }
  try {
    // Use sendBeacon so logout is still sent while the tab is closing.
    await navigator.sendBeacon(
      "/api/logout",
      new Blob([JSON.stringify({ username: state.username })], {
        type: "application/json",
      }),
    );
  } catch {
    // Ignore close-time network errors
  }
});

loadMotd();
