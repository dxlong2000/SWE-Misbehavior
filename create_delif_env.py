#!/usr/bin/env python3
"""
create_delif_env.py

Creates a copy of Source_Code (by default: Source_Code_delif) with dummy files
injected as described in metadata/fm/delif/samples.json.

For each sample:
  - The file at taken_from[0] is copied into the package at dm[0],
    simulating a foreign file dropped into the package with broken imports.

Usage:
    python3 create_delif_env.py [--source SOURCE] [--dest DEST] [--samples SAMPLES]

Defaults:
    --source   <deveval>/Source_Code
    --dest     <deveval>/Source_Code_delif
    --samples  <deveval>/metadata/fm/delif/samples.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    dev_eval = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Build Source_Code_delif: copy of Source_Code with dummy files injected."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=dev_eval / "Source_Code",
        help="Source tree to copy from (default: Source_Code).",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=dev_eval / "Source_Code_delif",
        help="Destination tree (default: Source_Code_delif).",
    )
    parser.add_argument(
        "--samples",
        type=Path,
        default=dev_eval / "metadata" / "fm" / "delif" / "samples.json",
        help="Path to delif samples.json.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Remove destination directory if it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    source: Path = args.source.resolve()
    dest: Path   = args.dest.resolve()

    if not source.exists():
        print(f"ERROR: Source directory not found: {source}", file=sys.stderr)
        return 1

    if not args.samples.exists():
        print(f"ERROR: Samples file not found: {args.samples}", file=sys.stderr)
        return 1

    with open(args.samples) as f:
        samples: dict = json.load(f)

    # ── Step 1: Copy Source_Code to destination ───────────────────────────────
    if dest.exists():
        if args.overwrite:
            print(f"Removing existing destination: {dest}")
            shutil.rmtree(dest)
        else:
            print(f"ERROR: Destination already exists: {dest}")
            print("Use --overwrite to replace it.", file=sys.stderr)
            return 1

    print(f"Copying {source} → {dest} ...")
    shutil.copytree(source, dest)
    print("Copy complete.")

    # ── Step 2: Inject dummy files ────────────────────────────────────────────
    injected = 0
    errors   = []

    for key, sample in samples.items():
        taken_from_list = sample.get("taken_from", [])
        dm_list         = sample.get("dm", [])

        for taken_from_rel, dm_rel in zip(taken_from_list, dm_list):
            src_file  = dest / taken_from_rel
            dest_file = dest / dm_rel

            if not src_file.exists():
                errors.append(f"{key}: taken_from not found: {taken_from_rel}")
                continue

            if dest_file.exists():
                errors.append(f"{key}: dm target already exists (name clash): {dm_rel}")
                continue

            # Ensure parent directory exists (it should, since it's a package)
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(src_file, dest_file)
            injected += 1

    print(f"\nInjected {injected} dummy files into {dest}")

    if errors:
        print(f"\n{len(errors)} warning(s):")
        for e in errors:
            print(f"  {e}")
    else:
        print("No errors.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
