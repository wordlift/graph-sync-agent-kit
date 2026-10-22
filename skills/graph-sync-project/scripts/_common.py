"""Shared helpers for the graph-sync kit scripts: worai.toml profiles, the API key, HTTP.

Standard library only, so the scripts run with any Python 3.11+ (`uv run python …` in a
graph-sync repo uses the project's Python 3.12).
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

API_BASE = "https://api.wordlift.io"
# Cloudflare in front of some endpoints rejects urllib's default User-Agent (error 1010).
USER_AGENT = "graph-sync-agent-kit (+https://github.com/wordlift/graph-sync-agent-kit)"
_ENV_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def configure_stdout() -> None:
    """Print non-ASCII page text on Windows consoles without UnicodeEncodeError."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def read_dotenv(path: Path) -> dict[str, str]:
    """Parse a `.env` file the way worai reads it: KEY=value lines, optional quotes."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        line = line.removeprefix("export ")
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


class Settings:
    """The resolved settings of one worai.toml profile plus the environment it runs with."""

    def __init__(self, profile: str | None, values: dict[str, Any], env: dict[str, str]):
        self.profile = profile
        self.values = values
        self.env = env

    def get(self, key: str, default: Any = None) -> Any:
        value = self.values.get(key, default)
        if isinstance(value, str):
            return _ENV_REF.sub(lambda m: self.env.get(m.group(1), ""), value)
        return value

    def api_key(self, key_env: str) -> str:
        """The profile's `api_key` (usually `${WORDLIFT_API_KEY}`), else the named variable."""
        raw = self.values.get("api_key")
        if isinstance(raw, str) and raw.strip():
            refs = _ENV_REF.findall(raw)
            resolved = self.get("api_key")
            if resolved:
                return resolved
            missing = ", ".join(refs) or "api_key"
            raise SystemExit(
                f"Profile '{self.profile}' reads its API key from {missing}, which is not set "
                "in the environment or in .env."
            )
        key = self.env.get(key_env, "")
        if not key:
            raise SystemExit(
                f"No API key: set {key_env} in .env (project root) or in the environment."
            )
        return key


def _deep_merge(parent: dict[str, Any], child: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(parent)
    for key, value in child.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _resolve_profile(profiles: dict[str, Any], name: str, stack: list[str]) -> dict[str, Any]:
    """Mirror the SDK's profile inheritance: `inherit` (default `_base`), deep-merged."""
    if name in stack:
        raise SystemExit(f"Profile inheritance cycle: {' -> '.join(stack + [name])}")
    node = profiles.get(name)
    if not isinstance(node, dict):
        raise SystemExit(f"Profile '{name}' not found in worai.toml.")
    parent = node.get("inherit")
    if parent is None and name != "_base" and "_base" in profiles:
        parent = "_base"
    if not parent:
        return deepcopy(node)
    return _deep_merge(_resolve_profile(profiles, parent, stack + [name]), node)


def load_settings(
    config: Path, profile: str | None, env_file: Path, *, require_profile: bool = True
) -> Settings:
    """Load `profile` from worai.toml; with no profile and no config, use only the environment.

    Without --profile and with several profiles: when `require_profile` is False and every
    profile resolves the same API key, the first profile is used (account-level checks).
    """
    env = read_dotenv(env_file)
    env.update({k: v for k, v in os.environ.items() if v})  # worai: real env wins over .env
    if not config.is_file():
        if profile:
            raise SystemExit(f"Config not found: {config}")
        return Settings(None, {}, env)
    if tomllib is None:
        raise SystemExit("Reading worai.toml needs Python 3.11+. Run the script with `uv run python`.")
    doc = tomllib.loads(config.read_text(encoding="utf-8"))
    profiles = doc.get("profiles") or {}
    names = [name for name in profiles if name != "_base"]
    if profile is None:
        if len(names) == 1:
            profile = names[0]
        else:
            keys = {
                Settings(n, _resolve_profile(profiles, n, []), env).get("api_key") for n in names
            }
            if require_profile or len(keys) != 1:
                raise SystemExit(f"Pick a profile with --profile: {', '.join(names) or '(none)'}")
            profile = names[0]
    return Settings(profile, _resolve_profile(profiles, profile, []), env)


def add_config_arguments(parser) -> None:
    parser.add_argument("--config", default="worai.toml", help="worai config (default: worai.toml)")
    parser.add_argument("--profile", help="worai.toml profile (default: the only one)")
    parser.add_argument("--env-file", default=".env", help="dotenv file (default: .env)")
    parser.add_argument(
        "--key-env",
        default="WORDLIFT_API_KEY",
        help="variable holding the API key when the profile has no api_key (default: WORDLIFT_API_KEY)",
    )


class ApiError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status = status
        self.body = body


def request(
    method: str,
    url: str,
    api_key: str | None,
    *,
    params: dict[str, str] | None = None,
    payload: Any = None,
    accept: str = "application/json",
    headers: dict[str, str] | None = None,
    timeout: float = 120,
    response_headers: dict[str, str] | None = None,
) -> tuple[int, str]:
    """Send one HTTP request; return (status, body text). Raise ApiError on 4xx/5xx.

    Pass a dict as `response_headers` to receive the response headers (lower-case names).
    """
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    data = None
    all_headers = {"Accept": accept, "User-Agent": USER_AGENT}
    if api_key:
        all_headers["Authorization"] = f"Key {api_key}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        all_headers["Content-Type"] = "application/json"
    all_headers.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=all_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if response_headers is not None:
                response_headers.update({name.lower(): value for name, value in resp.headers.items()})
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ApiError(exc.code, body) from None
