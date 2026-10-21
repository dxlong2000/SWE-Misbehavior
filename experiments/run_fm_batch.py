#!/usr/bin/env python
"""
Unified function-modification (fm) batch runner.

Usage:
    python run_fm_batch.py --framework sm --lv aef --model_id openai/gpt-4o-mini \
        --parallel 4 --num_samples 10

Supports all three frameworks via --framework {sm, oh, ag}.
FM levels: aef, anf, delf, delif.
"""

import argparse

from common.config import DEVEVAL
from common.batch import run_batch


def parse_args():
    parser = argparse.ArgumentParser(description="Run a batch of FM samples")
    parser.add_argument("--framework", type=str, required=True, choices=["sm", "oh", "ag"])
    parser.add_argument("--lv", type=str, required=True, help="aef, anf, delf, or delif")
    parser.add_argument("--model_id", type=str, required=True)
    parser.add_argument("--num_samples", type=int, default=50)
    parser.add_argument("--max_steps", type=int, default=20)
    parser.add_argument("--no_stream", action="store_true")
    parser.add_argument("--outdir", type=str, default="results")
    parser.add_argument("--mnr", type=int, default=3)
    parser.add_argument("--parallel", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--json", type=str, default="samples")
    parser.add_argument("--toolsel", action="store_true")
    parser.add_argument("--guidelines", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # For delif level, the source directory is different
    source_subdir = "Source_Code_fmdelif" if args.lv == "delif" else "Source_Code"

    run_batch(
        framework=args.framework,
        experiment="fm",
        lv=args.lv,
        model_id=args.model_id,
        outdir=args.outdir,
        num_samples=args.num_samples,
        parallel=args.parallel,
        mnr=args.mnr,
        json_name=args.json,
        toolsel=args.toolsel,
        guidelines=args.guidelines,
        max_steps=args.max_steps,
        no_stream=args.no_stream,
        source_subdir=source_subdir,
    )
