import base64
import hashlib
import hmac
import json
import secrets
import time


JWT_SECRET = "change-this-secret-key"
JWT_ALGORITHM = "HS256"
PASSWORD_ITERATIONS = 100_000


# Codifica bytes en formato base64 seguro para JWT.
def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


# Decodifica texto base64 seguro para JWT.
def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


# Genera un hash seguro de la password con sal aleatoria.
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${password_hash}"


# Comprueba una password contra el hash guardado.
def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$")
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(password_hash, expected_hash)


# Crea un JWT firmado con HMAC SHA256.
def create_jwt(payload: dict, expires_in_seconds: int = 3600) -> str:
    header = {
        "alg": JWT_ALGORITHM,
        "typ": "JWT",
    }
    payload = {
        **payload,
        "exp": int(time.time()) + expires_in_seconds,
    }

    encoded_header = _base64url_encode(json.dumps(header).encode("utf-8"))
    encoded_payload = _base64url_encode(json.dumps(payload).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}"

    signature = hmac.new(
        JWT_SECRET.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return f"{signing_input}.{_base64url_encode(signature)}"


# Verifica la firma y caducidad de un JWT.
def verify_jwt(token: str) -> dict | None:
    clean_token = token.replace("Bearer ", "", 1)
    parts = clean_token.split(".")
    if len(parts) != 3:
        return None

    encoded_header, encoded_payload, encoded_signature = parts
    signing_input = f"{encoded_header}.{encoded_payload}"

    expected_signature = hmac.new(
        JWT_SECRET.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    received_signature = _base64url_decode(encoded_signature)
    if not hmac.compare_digest(received_signature, expected_signature):
        return None

    payload = json.loads(_base64url_decode(encoded_payload))
    if not isinstance(payload, dict):
        return None

    if payload.get("exp", 0) < int(time.time()):
        return None

    return payload
