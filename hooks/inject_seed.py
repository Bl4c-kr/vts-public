#!/usr/bin/env python3
"""VTS seed injection — a Claude Code SessionStart hook.

Prints the 8 numbered seed lines into the session context on startup/resume/clear/compact,
so the seed survives context compaction and new sessions.

- Reads only the 8 numbered lines (1.–8.) of the Korean section of the seed file.
- If the file is missing or does not yield exactly 8 lines, prints nothing (no partial seed)
  and logs an error.
- Logs time, source, and the first 8 hex chars of the file's sha256 to a JSONL file,
  as evidence that the seed was actually loaded (compliance is checked outside the model).

Set VTS_SEED_FILE / VTS_SEED_LOG to override the default paths.
"""
import datetime
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.environ.get("VTS_SEED_FILE") or os.path.join(ROOT, "seed", "vts_seed_v3.0_candidate.md")
LOG = os.environ.get("VTS_SEED_LOG") or os.path.expanduser("~/.claude/logs/vts_seed_inject.jsonl")


def log(rec):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}
    rec = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "source": event.get("source"),
        "session": event.get("session_id"),
    }
    try:
        raw = open(SEED, encoding="utf-8").read()
    except OSError as e:
        rec["error"] = f"read: {e}"
        log(rec)
        return
    # Korean (canonical) section only: stop at the English translation heading.
    canonical = raw.split("## English", 1)[0]
    lines = [l for l in canonical.split("\n") if l[:2] in {f"{i}." for i in range(1, 9)}]
    if len(lines) != 8:
        rec["error"] = f"lines={len(lines)}"
        log(rec)
        return
    rec["sha8"] = hashlib.sha256(raw.encode()).hexdigest()[:8]
    print("[VTS seed v3.0 candidate — re-read before judging, analyzing, or proposing]")
    print("\n".join(lines))
    print("Priority: if this conflicts with the user's instructions, follow the user and note the conflict.")
    log(rec)


if __name__ == "__main__":
    main()
