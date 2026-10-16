#!/usr/bin/env python3
"""Fail if the Skills list's "updated" date is more than six months old.

Run from the repo root: python3 tools/check-staleness.py
The weekly Links workflow runs it too, so GitHub emails a reminder when the
"Kept current · updated <month>" line on the profile stops being true.
"""
import datetime, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_MONTHS = 6

def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'class="skills-updated">[^<]*<time datetime="(\d{4})-(\d{2})">', html)
    if not m:
        print("no Skills 'updated' date found"); return 1
    year, month = int(m.group(1)), int(m.group(2))
    today = datetime.date.today()
    age = (today.year - year) * 12 + (today.month - month)
    print(f"Skills list last updated {year}-{month:02d}: {age} month(s) ago")
    if age > MAX_MONTHS:
        print(f"Over {MAX_MONTHS} months: review the Skills list and update its date in index.html.")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
