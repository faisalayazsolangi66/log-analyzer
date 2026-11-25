#!/usr/bin/env python3
"""Analyze a log file and summarize errors, warnings and frequent messages.

Counts log levels, lists the most common error/warning messages, and can
filter by level or a text pattern. Works on plain-text logs.
"""
import argparse
import re
import sys
from collections import Counter

LEVEL_RE = re.compile(r"\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\b")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def normalize_level(raw):
    return "WARNING" if raw == "WARN" else raw


def message_of(line):
    """Strip timestamp and level prefix to get the core message."""
    text = TS_RE.sub("", line).strip()
    text = LEVEL_RE.sub("", text, count=1).strip(" -:[]")
    return text.strip() or line.strip()


def analyze(path, level_filter=None, pattern=None):
    levels = Counter()
    messages = Counter()
    error_messages = Counter()
    total = 0
    first_ts = last_ts = None
    pat = re.compile(pattern, re.IGNORECASE) if pattern else None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if pat and not pat.search(line):
                continue
            match = LEVEL_RE.search(line)
            level = normalize_level(match.group(1)) if match else "UNKNOWN"
            if level_filter and level != level_filter:
                continue
            total += 1
            levels[level] += 1
            msg = message_of(line)
            messages[msg] += 1
            if level in ("ERROR", "CRITICAL"):
                error_messages[msg] += 1
            ts = TS_RE.match(line)
            if ts:
                first_ts = first_ts or ts.group(0)
                last_ts = ts.group(0)
    return total, levels, messages, error_messages, first_ts, last_ts


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a log file and summarize errors and warnings.")
    parser.add_argument("logfile", help="Path to the log file to analyze")
    parser.add_argument("--level", choices=["DEBUG", "INFO", "WARNING",
                                            "ERROR", "CRITICAL"],
                        help="Only count lines at this level")
    parser.add_argument("--pattern", help="Only count lines matching this regex")
    parser.add_argument("--top", type=int, default=5,
                        help="How many top messages to show (default: 5)")
    parser.add_argument("--errors-only", action="store_true",
                        help="Only show the top error messages")
    args = parser.parse_args()

    try:
        total, levels, messages, errors, first, last = analyze(
            args.logfile, args.level, args.pattern)
    except OSError as exc:
        print(f"Error: cannot read log file: {exc}", file=sys.stderr)
        return 1

    print(f"File: {args.logfile}")
    print(f"Lines analyzed: {total}")
    if first:
        print(f"Time range: {first} -> {last}")
    print("\nBy level:")
    for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "UNKNOWN"):
        if levels.get(level):
            pct = 100.0 * levels[level] / total if total else 0
            print(f"  {level:<9} {levels[level]:>6}  ({pct:.1f}%)")
    if not total:
        print("No matching lines found.")
        return 0

    def show(title, counter):
        print(f"\n{title}:")
        for msg, count in counter.most_common(args.top):
            print(f"  {count:>4}x  {msg[:120]}")

    if args.errors_only:
        show("Top errors", errors)
    else:
        show("Top messages", messages)
        if errors:
            show("Top errors", errors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
