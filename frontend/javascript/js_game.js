const API_CANDIDATES = [
    sessionStorage.getItem("apiBaseUrl"),
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
].filter(Boolean);

let apiBaseUrl = "";
let socket = null;

const token = sessionStorage.getItem("authToken");
const currentUser = JSON.parse(sessionStorage.getItem("currentUser") || "null");
const currentGameId = Number(sessionStorage.getItem("currentGameId"));

if (!token || !currentUser || !currentGameId) {
    window.location.href = "main.html";
}

const chessBoard = document.getElementById("chessBoard");
const moveList = document.getElementById("moveList");
const turnText = document.getElementById("turnText");
const gameTitle = document.getElementById("gameTitle");
const whitePlayer = document.getElementById("whitePlayer");
const blackPlayer = document.getElementById("blackPlayer");
const resetBoardButton = document.getElementById("resetBoardButton");
const finishGameButton = document.getElementById("finishGameButton");
const gameMessage = document.getElementById("gameMessage");

let boardPieces = [];
let selectedSquare = null;
let moveNumber = 1;
let whiteTurn = true;

const pieceSymbols = {
    BLANCA: {
        King: "\u2654",
        Queen: "\u2655",
        Rook: "\u2656",
        Bishop: "\u2657",
        Knight: "\u2658",
        Pawn: "\u2659",
    },
    NEGRA: {
        King: "\u265A",
        Queen: "\u265B",
        Rook: "\u265C",
        Bishop: "\u265D",
        Knight: "\u265E",
        Pawn: "\u265F",
    },
};

function authHeaders() {
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
    };
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

function squareName(x, y) {
    const files = ["a", "b", "c", "d", "e", "f", "g", "h"];
    return `${files[x]}${y + 1}`;
}

function getPieceAt(x, y) {
    return boardPieces.find((piece) => piece.x === x && piece.y === y);
}

function getPieceSymbol(piece) {
    return pieceSymbols[piece.color]?.[piece.tipo] || "";
}

function renderBoard() {
    chessBoard.innerHTML = "";

    for (let row = 0; row < 8; row += 1) {
        for (let col = 0; col < 8; col += 1) {
            const x = col;
            const y = 7 - row;
            const piece = getPieceAt(x, y);
            const square = document.createElement("button");

            square.type = "button";
            square.className = `square ${(row + col) % 2 === 0 ? "light" : "dark"}`;
            square.dataset.x = x;
            square.dataset.y = y;
            square.textContent = piece ? getPieceSymbol(piece) : "";
            square.setAttribute("aria-label", squareName(x, y));

            if (selectedSquare && selectedSquare.x === x && selectedSquare.y === y) {
                square.classList.add("selected");
            }

            square.addEventListener("click", () => handleSquareClick(x, y));
            chessBoard.appendChild(square);
        }
    }

    turnText.textContent = `Turno: ${whiteTurn ? "blancas" : "negras"}`;
}

function addMove(piece, from, to) {
    const item = document.createElement("li");
    item.textContent = `${moveNumber}. ${getPieceSymbol(piece)} ${squareName(from.x, from.y)} -> ${squareName(to.x, to.y)}`;
    moveList.prepend(item);
    moveNumber += 1;
}

async function handleSquareClick(x, y) {
    gameMessage.textContent = "";
    const piece = getPieceAt(x, y);

    if (!selectedSquare && piece) {
        selectedSquare = { x, y };
        renderBoard();
        return;
    }

    if (!selectedSquare) {
        return;
    }

    if (selectedSquare.x === x && selectedSquare.y === y) {
        selectedSquare = null;
        renderBoard();
        return;
    }

    const from = selectedSquare;
    const movingPiece = getPieceAt(from.x, from.y);

    try {
        const result = await apiRequest(`/games/${currentGameId}/move`, {
            method: "PUT",
            body: JSON.stringify({
                from_x: from.x,
                from_y: from.y,
                to_x: x,
                to_y: y,
            }),
        });

        boardPieces = result.board || [];
        addMove(movingPiece, from, { x, y });
        selectedSquare = null;
        whiteTurn = result.turn !== "NEGRA";
        renderBoard();
    } catch (error) {
        gameMessage.textContent = error.message;
        selectedSquare = null;
        renderBoard();
    }
}

async function loadGame() {
    try {
        const state = await apiRequest(`/games/${currentGameId}/state`);
        const game = state.game;
        boardPieces = state.board || [];
        whiteTurn = state.turn !== "NEGRA";

        gameTitle.textContent = `Partida #${game.id}`;
        whitePlayer.textContent = `Usuario ${game.white_user_id}`;
        blackPlayer.textContent = `Usuario ${game.black_user_id}`;
        gameMessage.textContent = game.active ? "" : "Partida finalizada.";
        renderBoard();
    } catch (error) {
        gameMessage.textContent = error.message;
    }
}

resetBoardButton.addEventListener("click", async () => {
    selectedSquare = null;
    moveList.innerHTML = "";
    moveNumber = 1;
    whiteTurn = true;
    await loadGame();
});

finishGameButton.addEventListener("click", async () => {
    try {
        await apiRequest(`/games/${currentGameId}`, { method: "DELETE" });
        window.location.href = "main.html";
    } catch (error) {
        gameMessage.textContent = error.message;
    }
});

async function connectWebSocket() {
    const baseUrl = await resolveApiBase();
    const wsBaseUrl = baseUrl.replace("http://", "ws://").replace("https://", "wss://");
    socket = new WebSocket(`${wsBaseUrl}/ws?token=${encodeURIComponent(token)}`);

    socket.addEventListener("message", async (event) => {
        const message = JSON.parse(event.data);
        if (message.type === "game_updated" && Number(message.game_id) === currentGameId) {
            await loadGame();
        }
    });

    socket.addEventListener("close", () => {
        setTimeout(connectWebSocket, 2000);
    });
}

loadGame();
connectWebSocket();
