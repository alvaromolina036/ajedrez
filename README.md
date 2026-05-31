# ♟️ Ajedrez Online Multiplayer

Plataforma web de ajedrez online multijugador en tiempo real. Permite a los usuarios jugar partidas entre sí, crear o aceptar invitaciones y ver el estado del juego sincronizado en directo sin necesidad de recargar la página.

---

## 🚀 Características

- 🔐 Sistema de autenticación de usuarios (registro/login con JWT)
- ♟️ Partidas de ajedrez 1vs1 en tiempo real
- 🔄 Actualización del tablero sin recargar la página
- 👥 Lobby con usuarios conectados en tiempo real
- 📩 Sistema de invitaciones entre jugadores
- 📊 Partidas activas y estado del juego dinámico
- 💾 Persistencia de partidas en base de datos
- ⚡ Sincronización entre clientes mediante WebSockets

---

## 🧠 Funcionalidades principales

### 🎮 Juego en tiempo real
Los movimientos se envían al servidor mediante API REST y se sincronizan con el rival mediante eventos en WebSocket, evitando recargas de página.

### 👤 Usuarios
- Búsqueda de usuarios por nombre o ID
- Listado de usuarios conectados (online)

### 🧩 Partidas
- Creación de partidas públicas o privadas
- Visualización de partidas en curso
- Estado del tablero persistente

### 📩 Invitaciones
- Envío de invitaciones a otros usuarios
- Aceptación o rechazo en tiempo real
- Creación automática de partida al aceptar

---

## 🛠️ Tecnologías utilizadas

### Backend
- Node.js / Express
- MariaDB
- WebSockets (para eventos en tiempo real)
- JWT para autenticación
- API REST

### Frontend
- HTML5 / CSS3 / JavaScript
- UI dinámica tipo SPA ligera
- WebSocket client + consumo de API REST

---

## 📡 Arquitectura del sistema

El sistema se basa en una arquitectura híbrida:

- **REST API**
  - Usuarios
  - Partidas
  - Invitaciones
  - Movimientos

- **WebSockets**
  - Notificación de movimientos (`game_updated`)
  - Invitaciones en tiempo real
  - Estado de usuarios online

---

## 🔄 Flujo de una partida

1. Usuario inicia sesión
2. Busca o recibe invitación de otro jugador
3. Se crea la partida en el backend
4. Ambos jugadores se conectan a la partida
5. Un jugador realiza un movimiento
6. El backend actualiza el estado de la partida
7. Se envía evento WebSocket al rival
8. El rival actualiza el tablero sin recargar

---

## 📂 Instalación y uso

```bash
git clone https://github.com/alvaromolina036/ajedrez.git
cd ajedrez
