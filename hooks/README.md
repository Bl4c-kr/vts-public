# Hooks

`inject_seed.py` loads the 8-line seed at every Claude Code session start, resume, `/clear`, and compaction.

Example `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [{ "type": "command", "command": "python3 /path/to/vts-public/hooks/inject_seed.py" }]
      }
    ]
  }
}
```

The log file (`~/.claude/logs/vts_seed_inject.jsonl`) is the evidence that the seed was loaded. Line 7 of the seed: compliance is not proven by self-report.
