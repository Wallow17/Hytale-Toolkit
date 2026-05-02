/**
 * Active channel resolution shared by the runtime config loader and the
 * path formatters. Keeps a single source of truth for how the TS side
 * picks "release" vs "prerelease" at startup.
 */
import * as fs from "fs";
import * as path from "path";

const VALID = new Set(["release", "prerelease"]);

/**
 * Resolve the active Hytale channel.
 *
 * Priority:
 *   1. HYTALE_CHANNEL env var
 *   2. ~/.hytale-toolkit/active_channel sidecar (written by the GUI toggle
 *      and the bundled `hytale-channel` CLI)
 *   3. "release" default
 */
export function getActiveChannel(): string {
  const envChannel = process.env.HYTALE_CHANNEL?.trim();
  if (envChannel && VALID.has(envChannel)) return envChannel;

  const home = process.env.HOME || process.env.USERPROFILE;
  if (home) {
    try {
      const sidecar = path.join(home, ".hytale-toolkit", "active_channel");
      const value = fs.readFileSync(sidecar, "utf-8").trim();
      if (VALID.has(value)) return value;
    } catch {
      // file missing or unreadable -> fall through
    }
  }
  return "release";
}
