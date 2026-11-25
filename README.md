# log-analyzer

Analyze a log file and summarize log levels, top messages, and top errors.

## Requirements

- Python 3 (standard library only — no third-party packages)

## How to run

```bash
cd 053-log-analyzer
python3 main.py app.log
```

Run `python3 main.py --help` to see all options.

## Example

```bash
python3 main.py app.log
```

Sample output:

```
File: app.log
Lines analyzed: 4

By level:
  INFO         2  (50.0%)
  ERROR        1  (25.0%)
  WARNING      1  (25.0%)

Top messages:
     1x  Server started on port 8000
     1x  Database connection failed

Top errors:
     1x  Database connection failed
```

## Notes

Use `--level ERROR` to count only one level, `--pattern` to filter lines by regex, `--top N` to change how many messages are shown, and `--errors-only` to show only errors.

## License

MIT — see [LICENSE](LICENSE).
