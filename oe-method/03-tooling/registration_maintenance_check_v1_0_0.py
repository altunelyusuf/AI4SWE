#!/usr/bin/env python3
"""
registration_maintenance_check_v1_0_0.py — the registration-maintenance ceremony's check tool.

Reads 08-registration-maintenance/REGISTERED_SUBJECTS_v*.tsv, fetches each live repo's current
VERSION.txt via the GitHub contents API (requires a token with read access in GH_TOKEN or
GITHUB_TOKEN), and reports per subject whether the gap between the registered version and the
current one crosses the standing threshold:
  - a MAJOR bump since registration, or
  - 5 or more MINOR bumps since registration.

Reports, does not act: this tool never touches a registrant's files and never files a handover
itself. A subject with no known, verifiable live repo location, or an unparseable registered
baseline, is reported UNCHECKED / UNVERIFIABLE-BASELINE, disclosed rather than silently skipped.

Usage:
    GH_TOKEN=<token> python3 registration_maintenance_check_v1_0_0.py <registry.tsv>
"""
import sys
import os
import re
import json
import urllib.request
import urllib.error


def parse_semver(s):
    """Return (major, minor, patch) ints, or None if not a plain X.Y.Z token."""
    m = re.match(r'^(\d+)\.(\d+)\.(\d+)$', s.strip())
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def fetch_current_version(repo_url, token):
    """Fetch VERSION.txt content from a GitHub repo's default branch via the contents API."""
    m = re.match(r'https://github\.com/([^/]+)/([^/]+?)/?$', repo_url)
    if not m:
        return None, f"repo_url does not match https://github.com/<owner>/<repo>: {repo_url}"
    owner, repo = m.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/VERSION.txt"
    req = urllib.request.Request(api_url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.raw",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8").strip(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} fetching {api_url}"
    except Exception as e:
        return None, f"error fetching {api_url}: {e}"


def classify_gap(registered, current):
    """Apply the standing threshold: MAJOR bump, or >=5 MINOR bumps, since registration."""
    r_major, r_minor, r_patch = registered
    c_major, c_minor, c_patch = current
    if c_major > r_major:
        return "FLAG", f"MAJOR bump since registration ({r_major}.{r_minor}.{r_patch} -> {c_major}.{c_minor}.{c_patch})"
    if c_major == r_major and (c_minor - r_minor) >= 5:
        return "FLAG", f"{c_minor - r_minor} MINOR bumps since registration ({r_major}.{r_minor}.{r_patch} -> {c_major}.{c_minor}.{c_patch})"
    return "OK", f"within threshold ({r_major}.{r_minor}.{r_patch} -> {c_major}.{c_minor}.{c_patch})"


def main():
    if len(sys.argv) != 2:
        print("usage: registration_maintenance_check_v1_0_0.py <registry.tsv>", file=sys.stderr)
        sys.exit(2)

    registry_path = sys.argv[1]
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    rows = []
    with open(registry_path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            rows.append(parts[:5] if len(parts) >= 5 else parts + [""])

    results = []
    for row in rows:
        subject, repo_url, registered_version, closure_pack_version = row[0], row[1], row[2], row[3]
        note = row[4] if len(row) > 4 else ""

        if repo_url in ("IN-MONOREPO", "UNKNOWN"):
            results.append((subject, "UNCHECKED", f"no live repo location tracked ({repo_url})"))
            continue

        registered = parse_semver(registered_version)
        if registered is None:
            results.append((subject, "UNVERIFIABLE-BASELINE",
                             f"registered_version '{registered_version}' is not a plain X.Y.Z token"))
            continue

        if not token:
            results.append((subject, "UNCHECKED", "no GH_TOKEN/GITHUB_TOKEN in environment"))
            continue

        current_raw, err = fetch_current_version(repo_url, token)
        if err:
            results.append((subject, "UNCHECKED", err))
            continue

        current = parse_semver(current_raw)
        if current is None:
            results.append((subject, "UNCHECKED", f"current VERSION.txt '{current_raw}' is not a plain X.Y.Z token"))
            continue

        status, detail = classify_gap(registered, current)
        results.append((subject, status, detail))

    print(f"registration maintenance check — {len(results)} subject(s)")
    for subject, status, detail in results:
        print(f"  {status:22s} {subject:28s} {detail}")

    flagged = [r for r in results if r[1] == "FLAG"]
    print(f"\nflagged: {len(flagged)}/{len(results)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
