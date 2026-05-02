"""
Distribution configuration loader.

Centralizes all fork-specific URLs (GitHub repo, CDN, javadocs) so that
maintaining a fork only requires editing config/distribution.json.

Resolution order:
1. PyInstaller bundle (sys._MEIPASS/distribution.json)
2. Repo dev path (hytale-rag/config/distribution.json)
"""
import json
import sys
from pathlib import Path

_CACHED: dict | None = None


def _config_path() -> Path:
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS) / "distribution.json"
    return Path(__file__).parent / "config" / "distribution.json"


def load() -> dict:
    global _CACHED
    if _CACHED is not None:
        return _CACHED
    path = _config_path()
    with open(path, "r", encoding="utf-8") as f:
        _CACHED = json.load(f)
    return _CACHED


def github_repo() -> str:
    return load()["github_repo"]


def git_clone_url() -> str:
    return load()["git_clone_url"]


def cdn_base_url() -> str:
    return load()["cdn_base_url"]


def releases_api_url() -> str:
    return f"https://api.github.com/repos/{github_repo()}/releases/latest"


def releases_page_url() -> str:
    return f"https://github.com/{github_repo()}/releases/latest"


def javadocs_release_url() -> str:
    return load()["javadocs"]["release_url"]


def javadocs_prerelease_url() -> str:
    return load()["javadocs"]["prerelease_url"]
