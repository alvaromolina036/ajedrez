const API_CANDIDATES = [
    sessionStorage.getItem("apiBaseUrl"),
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
].filter(Boolean);

let apiBaseUrl = "";
let socket = null;

const token = sessionStorage.getItem("authToken");
const currentUser = JSON.parse(sessionStorage.getItem("currentUser") || "null");

if (!token || !currentUser) {
    window.location.href = "landing.html";
}

const welcomeText = document.getElementById("welcomeText");
const sessionStatus = document.getElementById("sessionStatus");
const userIdLabel = document.getElementById("userIdLabel");
const loadedGamesCount = document.getElementById("loadedGamesCount");
const apiStatus = document.getElementById("apiStatus");
const createGameButton = document.getElementById("createGameButton");
const focusCreateGameButton = document.getElementById("focusCreateGameButton");
const refreshGamesButton = document.getElementById("refreshGamesButton");
const refreshInvitationsButton = document.getElementById("refreshInvitationsButton");
const logoutButton = document.getElementById("logoutButton");
const searchUserForm = document.getElementById("searchUserForm");
const rivalUsername = document.getElementById("rivalUsername");
const foundUserCard = document.getElementById("foundUserCard");
const foundUsername = document.getElementById("foundUsername");
const foundUserId = document.getElementById("foundUserId");
const createGameWithUserButton = document.getElementById("createGameWithUserButton");
const inviteUserButton = document.getElementById("inviteUserButton");
const openGameForm = document.getElementById("openGameForm");
const gameIdInput = document.getElementById("gameIdInput");
const createGameMessage = document.getElementById("createGameMessage");
const connectedUsersList = document.getElementById("connectedUsersList");
const invitationList = document.getElementById("invitationList");
const gameList = document.getElementById("gameList");

let selectedRival = null;

function authHeaders() {
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
    };
}

async function resolveApiBase() {
    if (apiBaseUrl) {
        return apiBaseUrl;
    }

    for (const candidate of API_CANDIDATES) {
        try {
            const response = await fetch(`${candidate}/`, {
                headers: authHeaders(),
            });

            if (response.ok) {
                apiBaseUrl = candidate;
                sessionStorage.setItem("apiBaseUrl", candidate);
                return candidate;
            }
        } catch {
            // Se prueba el siguiente puerto disponible.
        }
    }

    throw new Error("API desconectada");
}

async function apiRequest(path, options = {}) {
    const baseUrl = await resolveApiBase();
    const response = await fetch(`${baseUrl}${path}`, {
        ...options,
        headers: {
            ...authHeaders(),
            ...(options.headers || {}),
        },
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : null;

    if (!response.ok) {
        throw new Error(data?.detail || "La peticion no se ha podido completar.");
    }

    return data;
}

function setApiState(isOnline) {
    apiStatus.classList.toggle("online", isOnline);
    apiStatus.classList.toggle("offline", !isOnline);
    apiStatus.textContent = isOnline && apiBaseUrl ? `API ${apiBaseUrl.split(":").pop()}` : "API desconectada";
}

function openGame(gameId) {
    sessionStorage.setItem("currentGameId", String(gameId));
    window.location.href = "game.html";
}

function renderOnlineUsers(users) {
    connectedUsersList.innerHTML = "";

    if (users.length === 0) {
        connectedUsersList.innerHTML = "<li class=\"empty-state\">No hay usuarios conectados ahora mismo.</li>";
        return;
    }

    users.forEach((user) => {
        const item = document.createElement("li");
        item.className = "opponent-item";
        item.innerHTML = `
            <div>
                <strong>${user.username}</strong>
                <span>ID ${user.id} - conectado</span>
            </div>
        `;
        connectedUsersList.appendChild(item);
    });
}

function renderInvitations(invitations) {
    invitationList.innerHTML = "";

    if (invitations.length === 0) {
        invitationList.innerHTML = "<li class=\"empty-state\">No tienes invitaciones pendientes.</li>";
        return;
    }

    invitations.forEach((invitation) => {
        const item = document.createElement("li");
        item.className = "game-item";
        item.innerHTML = `
            <div>
                <strong>Invitacion #${invitation.id}</strong>
                <span>Usuario ${invitation.from_user_id} quiere jugar contigo</span>
            </div>
            <button type="button" data-action="accept">Aceptar</button>
            <button type="button" data-action="reject">Rechazar</button>
        `;

        item.querySelector("[data-action='accept']").addEventListener("click", () => answerInvitation(invitation.id, "accept"));
        item.querySelector("[data-action='reject']").addEventListener("click", () => answerInvitation(invitation.id, "reject"));
        invitationList.appendChild(item);
    });
}

function renderGames(games) {
    loadedGamesCount.textContent = games.length;
    gameList.innerHTML = "";

    if (games.length === 0) {
        gameList.innerHTML = "<li class=\"empty-state\">No hay partidas activas en la API.</li>";
        return;
    }

    games.forEach((game) => {
        const item = document.createElement("li");
        item.className = "game-item";
        item.innerHTML = `
            <div>
                <strong>Partida #${game.id}</strong>
                <span>Blancas ${game.white_user_id} / negras ${game.black_user_id}</span>
            </div>
            <button type="button">Abrir</button>
        `;
        item.querySelector("button").addEventListener("click", () => openGame(game.id));
        gameList.appendChild(item);
    });
}

async function verifySession() {
    try {
        await apiRequest("/authentication/verify");
        setApiState(true);
        sessionStatus.textContent = "Activa";
    } catch {
        setApiState(false);
        sessionStatus.textContent = "Caducada";
    }
}

async function loadOnlineUsers() {
    try {
        renderOnlineUsers(await apiRequest("/users/online"));
    } catch (error) {
        connectedUsersList.innerHTML = `<li class="empty-state">${error.message}</li>`;
    }
}

async function loadInvitations() {
    try {
        renderInvitations(await apiRequest("/invitations/pending"));
    } catch (error) {
        invitationList.innerHTML = `<li class="empty-state">${error.message}</li>`;
    }
}

async function loadLiveGames() {
    try {
        renderGames(await apiRequest("/games/live"));
    } catch (error) {
        gameList.innerHTML = `<li class="empty-state">${error.message}</li>`;
    }
}

async function searchUser(query) {
    selectedRival = null;
    foundUserCard.classList.add("hidden");
    createGameMessage.textContent = "";

    const users = await apiRequest(`/users/search?query=${encodeURIComponent(query)}`);
    const user = users.find((candidate) => candidate.id !== currentUser.user_id);

    if (!user) {
        throw new Error("No se ha encontrado ningun usuario rival con esa busqueda.");
    }

    selectedRival = user;
    foundUsername.textContent = user.username;
    foundUserId.textContent = `ID ${user.id} - usuario encontrado en la API`;
    foundUserCard.classList.remove("hidden");
}

async function createGameWithSelectedUser() {
    if (!selectedRival) {
        createGameMessage.textContent = "Busca primero un usuario rival.";
        return;
    }

    const game = await apiRequest("/games", {
        method: "POST",
        body: JSON.stringify({
            white_user_id: currentUser.user_id,
            black_user_id: selectedRival.id,
        }),
    });

    openGame(game.id);
}

async function sendInvitationToSelectedUser() {
    if (!selectedRival) {
        createGameMessage.textContent = "Busca primero un usuario rival.";
        return;
    }

    const invitation = await apiRequest("/invitations", {
        method: "POST",
        body: JSON.stringify({
            to_user_id: selectedRival.id,
        }),
    });

    createGameMessage.textContent = `Invitacion #${invitation.id} enviada.`;
}

async function answerInvitation(invitationId, action) {
    try {
        const result = await apiRequest(`/invitations/${invitationId}/${action}`, {
            method: "PUT",
        });
        await loadInvitations();
        await loadLiveGames();
        if (action === "accept" && result.game) {
            openGame(result.game.id);
        }
    } catch (error) {
        createGameMessage.textContent = error.message;
    }
}

async function connectWebSocket() {
    const baseUrl = await resolveApiBase();
    const wsBaseUrl = baseUrl.replace("http://", "ws://").replace("https://", "wss://");
    socket = new WebSocket(`${wsBaseUrl}/ws?token=${encodeURIComponent(token)}`);

    socket.addEventListener("message", async (event) => {
        const message = JSON.parse(event.data);

        if (message.type === "presence_changed") {
            renderOnlineUsers(message.users || []);
        }

        if (message.type === "game_updated") {
            await loadLiveGames();
        }

        if (message.type === "invitation_received" || message.type === "invitation_answered") {
            await loadInvitations();
            await loadLiveGames();
        }
    });

    socket.addEventListener("close", () => {
        setTimeout(connectWebSocket, 2000);
    });
}

welcomeText.textContent = `Bienvenido, ${currentUser.username}`;
userIdLabel.textContent = String(currentUser.user_id);

createGameButton.addEventListener("click", () => {
    document.getElementById("createGamePanel").scrollIntoView({ behavior: "smooth", block: "start" });
    rivalUsername.focus();
});

focusCreateGameButton.addEventListener("click", () => {
    document.getElementById("createGamePanel").scrollIntoView({ behavior: "smooth", block: "start" });
    rivalUsername.focus();
});

refreshGamesButton.addEventListener("click", loadLiveGames);
refreshInvitationsButton.addEventListener("click", loadInvitations);

logoutButton.addEventListener("click", () => {
    if (socket) {
        socket.close();
    }
    sessionStorage.clear();
    window.location.href = "landing.html";
});

searchUserForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        await searchUser(rivalUsername.value.trim());
    } catch (error) {
        createGameMessage.textContent = error.message;
    }
});

createGameWithUserButton.addEventListener("click", async () => {
    createGameMessage.textContent = "";

    try {
        await createGameWithSelectedUser();
    } catch (error) {
        createGameMessage.textContent = error.message;
    }
});

inviteUserButton.addEventListener("click", async () => {
    createGameMessage.textContent = "";

    try {
        await sendInvitationToSelectedUser();
    } catch (error) {
        createGameMessage.textContent = error.message;
    }
});

openGameForm.addEventListener("submit", (event) => {
    event.preventDefault();
    openGame(Number(gameIdInput.value));
});

verifySession();
loadOnlineUsers();
loadInvitations();
loadLiveGames();
connectWebSocket();
