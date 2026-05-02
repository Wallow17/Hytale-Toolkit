/**
 * Distribution configuration loader.
 *
 * Reads fork-specific URLs from config/distribution.json so that
 * maintaining a fork only requires editing that single file.
 */
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

interface DistributionConfig {
  github_repo: string;
  git_clone_url: string;
  cdn_base_url: string;
  javadocs: {
    release_url: string;
    prerelease_url: string;
  };
}

let cached: DistributionConfig | null = null;

function configPath(): string {
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  return path.resolve(__dirname, "..", "config", "distribution.json");
}

export function load(): DistributionConfig {
  if (cached) return cached;
  cached = JSON.parse(fs.readFileSync(configPath(), "utf-8")) as DistributionConfig;
  return cached;
}

export function githubRepo(): string {
  return load().github_repo;
}

export function releasesPageUrl(): string {
  return `https://github.com/${githubRepo()}/releases`;
}

export function releasesLatestUrl(): string {
  return `https://github.com/${githubRepo()}/releases/latest`;
}

export function releasesApiUrl(): string {
  return `https://api.github.com/repos/${githubRepo()}/releases/latest`;
}
