const API_CANDIDATES = [
    sessionStorage.getItem("apiBaseUrl"),
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8001",
].filter(Boolean);

let apiBaseUrl = "";

const authForm = document.getElementById("authForm");
const loginMode = document.getElementById("loginMode");
const registerMode = document.getElementById("registerMode");
const formTitle = document.getElementById("formTitle");
const formSubtitle = document.getElementById("formSubtitle");
const submitButton = document.getElementById("submitButton");
const errorMsg = document.getElementById("errorMsg");
const apiStatus = document.getElementById("apiStatus");

let currentMode = "login";

function setMode(mode) {
    currentMode = mode;
    const isLogin = mode === "login";

    loginMode.classList.toggle("active", isLogin);
    registerMode.classList.toggle("active", !isLogin);
    formTitle.textContent = isLogin ? "Iniciar sesion" : "Crear cuenta";
    formSubtitle.textContent = isLogin
        ? "Entra para acceder a tus partidas y crear nuevos tableros."
        : "Crea tu cuenta para empezar a jugar partidas.";
    submitButton.textContent = isLogin ? "Entrar" : "Registrarme";
    errorMsg.textContent = "";
}

function decodeJwtPayload(token) {
    const [, payload] = token.split(".");
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const decodedPayload = atob(base64.padEnd(base64.length + ((4 - base64.length % 4) % 4), "="));
    return JSON.parse(decodedPayload);
}

async function apiRequest(path, options = {}) {
    const baseUrl = await resolveApiBase();
    const response = await fetch(`${baseUrl}${path}`, {
        ...options,
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
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

async function resolveApiBase() {
    if (apiBaseUrl) {
        return apiBaseUrl;
    }

    for (const candidate of API_CANDIDATES) {
        try {
            const response = await fetch(`${candidate}/`, {
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
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

async function checkApiStatus() {
    try {
        await resolveApiBase();
        apiStatus.classList.remove("offline");
        apiStatus.classList.add("connected");
        apiStatus.title = `API activa en ${apiBaseUrl}`;
    } catch {
        apiStatus.classList.remove("connected");
        apiStatus.classList.add("offline");
        apiStatus.title = "API desconectada";
    }
}

async function login(username, password) {
    const data = await apiRequest("/authentication/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
    });

    const user = decodeJwtPayload(data.token);
    sessionStorage.setItem("authToken", data.token);
    sessionStorage.setItem("currentUser", JSON.stringify(user));
}

async function register(username, password) {
    await apiRequest("/users", {
        method: "POST",
        body: JSON.stringify({ username, password }),
    });
    await login(username, password);
}

loginMode.addEventListener("click", () => setMode("login"));
registerMode.addEventListener("click", () => setMode("register"));

authForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    errorMsg.textContent = "";

    if (username.length < 3) {
        errorMsg.textContent = "El usuario debe tener al menos 3 caracteres.";
        return;
    }

    if (password.length < 4) {
        errorMsg.textContent = "La contrasena debe tener al menos 4 caracteres.";
        return;
    }

    submitButton.disabled = true;
    submitButton.textContent = currentMode === "login" ? "Entrando..." : "Creando...";

    try {
        if (currentMode === "login") {
            await login(username, password);
        } else {
            await register(username, password);
        }

        window.location.href = "main.html";
    } catch (error) {
        errorMsg.textContent = error.message;
        submitButton.disabled = false;
        submitButton.textContent = currentMode === "login" ? "Entrar" : "Registrarme";
    }
});

checkApiStatus();
