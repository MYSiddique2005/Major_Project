"""Step 1: download the Wide World Importers PostgreSQL dump and extract every table to CSV.

Source: Microsoft's sample ERP database, PostgreSQL port published at
https://github.com/Azure/azure-postgresql/tree/master/samples/databases/wide-world-importers (MIT licence).

The dump is read with pg_restore, which turns it into SQL text; no database is created or touched.
Output: Data/raw/csv/<schema>.<table>.csv, values exactly as stored in the source (nulls are empty).
"""
import csv
import hashlib
import io
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = DATA_DIR / "raw"
CSV_DIR = RAW_DIR / "csv"
DUMP = RAW_DIR / "wide_world_importers_pg.dump"
URL = (
    "https://raw.githubusercontent.com/Azure/azure-postgresql/master/"
    "samples/databases/wide-world-importers/wide_world_importers_pg.dump"
)
SHA256 = "f2cb95c02bfba871384669ed27fc694d4cc3091a72e1c21e1a2598bdbe471f8f"

COPY_RE = re.compile(r"^COPY (\S+) \((.*)\) FROM stdin;$")
SEARCH_PATH_RE = re.compile(r"^SET search_path = ([^,;]+)")
ESCAPE_RE = re.compile(r"\\(.)")
ESCAPES = {"b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v", "\\": "\\"}


def pg_restore_binary() -> str:
    candidates = sorted(Path("/usr/lib/postgresql").glob("*/bin/pg_restore"), key=lambda p: int(p.parts[-3]))
    return str(candidates[-1]) if candidates else "pg_restore"


def unescape(field: str) -> str | None:
    """Decode one field of PostgreSQL's COPY text format."""
    if field == "\\N":
        return None
    if "\\" not in field:
        return field
    return ESCAPE_RE.sub(lambda m: ESCAPES.get(m.group(1), m.group(1)), field)


def main() -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    if not DUMP.exists():
        print(f"Downloading {URL}")
        urllib.request.urlretrieve(URL, DUMP)
    digest = hashlib.sha256(DUMP.read_bytes()).hexdigest()
    if digest != SHA256:
        sys.exit(f"Checksum mismatch for {DUMP.name}: got {digest}")

    process = subprocess.Popen(
        [pg_restore_binary(), "--no-owner", "--no-privileges", "-f", "-", str(DUMP)],
        stdout=subprocess.PIPE,
    )
    lines = io.TextIOWrapper(process.stdout, encoding="utf-8", newline="\n")
    schema = "public"
    writer = handle = None
    name = ""
    rows = 0
    for line in lines:
        line = line.rstrip("\n")
        if writer is None:
            if match := SEARCH_PATH_RE.match(line):
                schema = match.group(1).strip()
            elif match := COPY_RE.match(line):
                name = f"{schema}.{match.group(1)}"
                handle = open(CSV_DIR / f"{name}.csv", "w", newline="", encoding="utf-8")
                writer = csv.writer(handle)
                writer.writerow(column.strip() for column in match.group(2).split(","))
                rows = 0
        elif line == "\\.":
            handle.close()
            print(f"{name:45s} {rows:>8,d} rows")
            writer = None
        else:
            writer.writerow("" if (value := unescape(field)) is None else value for field in line.split("\t"))
            rows += 1
    if process.wait() != 0:
        sys.exit("pg_restore failed")


if __name__ == "__main__":
    main()
