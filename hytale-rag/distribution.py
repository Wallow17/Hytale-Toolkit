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


# =============================================================================
# Channel handling (release vs prerelease)
# =============================================================================

CHANNELS = ("release", "prerelease")
DEFAULT_CHANNEL = "release"


def _active_channel_file() -> Path:
    return Path.home() / ".hytale-toolkit" / "active_channel"


def get_active_channel() -> str:
    """Return the currently active Hytale channel.

    Reads ~/.hytale-toolkit/active_channel; falls back to DEFAULT_CHANNEL.
    """
    try:
        value = _active_channel_file().read_text(encoding="utf-8").strip()
        if value in CHANNELS:
            return value
    except OSError:
        pass
    return DEFAULT_CHANNEL


def set_active_channel(channel: str) -> None:
    """Persist the active channel choice. Safe to call repeatedly."""
    if channel not in CHANNELS:
        raise ValueError(f"channel must be one of {CHANNELS}, got {channel!r}")
    path = _active_channel_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(channel, encoding="utf-8")


def db_tarball_name(provider: str, channel: str) -> str:
    """Asset name for a per-channel database tarball."""
    return f"lancedb-{provider}-{channel}.tar.gz"


def detect_channel_from_hytale_path(path: str | Path) -> str:
    """Infer the Hytale channel from an install path.

    Hypixel's launcher splits release / prerelease at the install root:
        ~/.../Hytale/install/release/...     -> release
        ~/.../Hytale/install/pre-release/... -> prerelease

    Falls back to DEFAULT_CHANNEL when neither token is present.
    """
    s = str(path).replace("\\", "/").lower()
    # Order matters: "/release/" is a substring of "/pre-release/" inverted check.
    if "/pre-release/" in s or "/prerelease/" in s:
        return "prerelease"
    if "/release/" in s:
        return "release"
    return DEFAULT_CHANNEL


# =============================================================================
# CLI: `python -m distribution channel [release|prerelease]`
#  - no arg  -> prints active channel
#  - with arg -> sets active channel and prints confirmation
# Restart Claude Code (or any running MCP server) afterwards to pick up.
# =============================================================================

def _main_cli(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] != "channel":
        print("Usage: python -m distribution channel [release|prerelease]")
        return 2
    if len(argv) == 2:
        print(get_active_channel())
        return 0
    target = argv[2]
    try:
        set_active_channel(target)
    except ValueError as e:
        print(f"error: {e}")
        return 1
    print(f"active channel set to: {target}")
    print("note: restart Claude Code (or your MCP host) to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main_cli(sys.argv))
