import base64
import hashlib
import os
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Optional

import requests

from .config import load_env, get_env, get_default_redirect_port, read_tokens, write_tokens


class _CallbackHandler(BaseHTTPRequestHandler):
    code: Optional[str] = None
    state_expected: Optional[str] = None

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/callback"):
            from urllib.parse import urlparse, parse_qs

            query = parse_qs(urlparse(self.path).query)
            code = query.get("code", [None])[0]
            state = query.get("state", [None])[0]
            if _CallbackHandler.state_expected and state != _CallbackHandler.state_expected:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"State mismatch")
                return
            _CallbackHandler.code = code
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"You can close this window.")
        else:
            self.send_response(404)
            self.end_headers()


def _start_server_until_code(port: int, expected_state: str, timeout_seconds: int = 180) -> Optional[str]:
    _CallbackHandler.code = None
    _CallbackHandler.state_expected = expected_state
    httpd = HTTPServer(("127.0.0.1", port), _CallbackHandler)
    server_thread = threading.Thread(target=httpd.handle_request, daemon=True)
    server_thread.start()

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if _CallbackHandler.code:
            try:
                httpd.server_close()
            except Exception:
                pass
            return _CallbackHandler.code
        time.sleep(0.2)
    try:
        httpd.server_close()
    except Exception:
        pass
    return None


def _generate_pkce() -> Dict[str, str]:
    verifier = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b"=").decode("ascii")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return {"verifier": verifier, "challenge": challenge}


def authorize_and_cache_tokens() -> Dict[str, str]:
    load_env()
    client_id = get_env("WHOOP_CLIENT_ID")
    client_secret = get_env("WHOOP_CLIENT_SECRET")
    redirect_port = get_default_redirect_port()
    redirect_uri = f"http://127.0.0.1:{redirect_port}/callback"

    if not client_id or not client_secret:
        raise RuntimeError("WHOOP_CLIENT_ID and WHOOP_CLIENT_SECRET must be set in environment or .env")

    # WHOOP endpoints (adjust if docs differ)
    authorize_url = get_env("WHOOP_AUTH_URL", "https://api.prod.whoop.com/oauth/oauth2/auth")
    token_url = get_env("WHOOP_TOKEN_URL", "https://api.prod.whoop.com/oauth/oauth2/token")

    scopes = get_env("WHOOP_SCOPES", "offline_access read:recovery read:sleep read:cycle read:workout")

    pkce = _generate_pkce()
    state = secrets.token_urlsafe(16)

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": state,
        "code_challenge": pkce["challenge"],
        "code_challenge_method": "S256",
    }
    from urllib.parse import urlencode

    url = f"{authorize_url}?{urlencode(params)}"
    webbrowser.open(url)

    code = _start_server_until_code(redirect_port, state)
    if not code:
        raise RuntimeError("Authorization timed out")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": pkce["verifier"],
    }
    auth = (client_id, client_secret)
    resp = requests.post(token_url, data=data, auth=auth, timeout=30)
    resp.raise_for_status()
    tokens = resp.json()
    cached = read_tokens()
    cached["whoop"] = tokens
    write_tokens(cached)
    return tokens


def get_valid_token() -> str:
    load_env()
    token_url = get_env("WHOOP_TOKEN_URL", "https://api.prod.whoop.com/oauth/oauth2/token")
    client_id = get_env("WHOOP_CLIENT_ID")
    client_secret = get_env("WHOOP_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("WHOOP_CLIENT_ID and WHOOP_CLIENT_SECRET must be set")

    tokens = read_tokens().get("whoop") or {}
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")
    issued_at = tokens.get("issued_at")

    # naive expiry check; if missing data, attempt refresh anyway
    now = int(time.time())
    if access_token and issued_at and expires_in and now < (issued_at + int(expires_in) - 60):
        return access_token

    if not refresh_token:
        new_tokens = authorize_and_cache_tokens()
        new_tokens["issued_at"] = int(time.time())
        cached = read_tokens()
        cached["whoop"] = new_tokens
        write_tokens(cached)
        return new_tokens["access_token"]

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    auth = (client_id, client_secret)
    resp = requests.post(token_url, data=data, auth=auth, timeout=30)
    resp.raise_for_status()
    new_tokens = resp.json()
    new_tokens["issued_at"] = int(time.time())
    cached = read_tokens()
    cached["whoop"] = new_tokens
    write_tokens(cached)
    return new_tokens["access_token"]


