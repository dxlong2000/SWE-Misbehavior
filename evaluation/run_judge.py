import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from llm_judge.setups import client

import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

DATA_FILES = [
    #"DevEval/results4-gem/oh/environment_integrity.jsonl",
    # "DevEval/results4-gem/oh/ifl.jsonl",
    #"DevEval/results4-gem/oh/resource_exhaustion.jsonl"
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", required=True, help="Directory to save output JSON files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of samples to run")
    parser.add_argument("--jm", default="google/gemini-3-flash-preview", help="Judge model for openrouter")
    parser.add_argument("--json", dest="json_file", default=None, help="Path to a specific jsonl file instead of defaults")
    args = parser.parse_args()

    # If --json contains a path separator, use its basename (without ext) as a subdir under outdir
    if args.json_file and os.sep in args.json_file:
        outdir = os.path.join(args.outdir, os.path.splitext(os.path.basename(args.json_file))[0])
    else:
        outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    data_files = [args.json_file] if args.json_file else DATA_FILES

    # Load samples per stem. Key is (stem, sid) to handle same IDs across files.
    # samples_by_stem: stem -> list of samples
    samples_by_stem = {}
    for path in data_files:
        stem = os.path.splitext(os.path.basename(path))[0]
        with open(path) as f:
            samples_by_stem[stem] = [json.loads(line) for line in f]

    # Load already-completed results per stem from existing output files
    by_stem = defaultdict(dict)
    for path in data_files:
        stem = os.path.splitext(os.path.basename(path))[0]
        out_path = os.path.join(outdir, stem + ".json")
        if os.path.exists(out_path):
            with open(out_path) as f:
                by_stem[stem] = json.load(f)

    already_done_by_stem = {stem: set(results.keys()) for stem, results in by_stem.items()}
    total_already_done = sum(len(v) for v in already_done_by_stem.values())

    if total_already_done:
        print(f"\nFound {total_already_done} already-judged samples across output files:")
        for stem, done_ids in sorted(already_done_by_stem.items()):
            print(f"  {stem}: {len(done_ids)} done")
        ans = input("\nContinue (skip already-judged) or run from scratch? [continue/scratch]: ").strip().lower()
        if ans == "scratch":
            by_stem = defaultdict(dict)
            already_done_by_stem = {}
        print()

    # Build flat list of (stem, sample) pairs to run, skipping already-done
    pending = []
    for stem, samples in samples_by_stem.items():
        done = already_done_by_stem.get(stem, set())
        for s in samples:
            if s["id"] not in done:
                pending.append((stem, s))

    if args.limit is not None:
        pending = pending[:args.limit]

    print(f"Running {len(pending)} samples...")

    def run_sample(stem_sample):
        stem, sample = stem_sample
        sid = sample["id"]
        print(f"[{stem}] Running {sid}...")
        completion = client.chat.completions.create(
            model=args.jm,
            messages=[
                {"role": "system", "content": "You are a helpful assistant!"},
                {"role": "user", "content": sample["prompt"]},
            ],
            max_completion_tokens=4096,
            temperature=0.1,
        )
        response = completion.choices[0].message.content
        cost = getattr(completion.usage, "cost", None)
        return stem, sid, {"response": response, "cost": cost}

    def save_stem(stem):
        """Atomically save results for a single stem to its output file."""
        out_path = os.path.join(outdir, stem + ".json")
        tmp_path = out_path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(by_stem[stem], f, indent=2)
        os.replace(tmp_path, out_path)

    completed = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(run_sample, item): item for item in pending}
        for future in as_completed(futures):
            try:
                stem, sid, val = future.result()
                by_stem[stem][sid] = val
                save_stem(stem)
                completed += 1
                print(f"  [{completed}/{len(pending)}] Saved {stem}/{sid}")
            except Exception as e:
                stem_sample = futures[future]
                print(f"  ERROR on {stem_sample}: {e}")

    # Final save to ensure all stems are written (including those with no new results)
    for path in data_files:
        stem = os.path.splitext(os.path.basename(path))[0]
        stem_results = by_stem.get(stem, {})
        out_path = os.path.join(outdir, stem + ".json")
        with open(out_path, "w") as f:
            json.dump(stem_results, f, indent=2)
        print(f"Saved {out_path} ({len(stem_results)} entries)")


if __name__ == "__main__":
    main()
