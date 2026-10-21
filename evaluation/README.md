This folder contains the evaluation pipeline for SWE-MISBEHAVIOR with two metric families: **Rule-based (RB) metrics (Code Misbehaviors)** and **LLM-judge metrics (File Read, Environment Misbehaviors and Instruction Following)**

## Rule-Based Metrics (`rb/`)

`parsefile.py` parses a Python source file into a dictionary capturing:
- Module docstring
- Imports (with aliases and imported objects)
- Module-level variables and annotated assignments
- Function definitions (signature, body, docstring, decorators, async flag)
- Class definitions (bases, docstring, decorators)

`metrics.py` diffs two such parsed dicts and reports:
- `context_changes` — list of unintended modifications to surrounding code (missing imports, renamed aliases, changed function bodies/signatures outside the target, etc.)
- `context_changed` — count of context change events
- `signature_changed` — whether the target function's signature changed
- `body_changed` — whether the target function's docstring changed
- `target_function_code_changed` — whether the target function's body changed

### LLM-Judge Metrics (`llm_judge/`)

Two judge types are supported:

| Judge | Script | Purpose |
|---|---|---|
| **IF (Instruction-Following), Environment Integrity, Resource Exhaustion** | `run_env.py` | Checks whether an agent's actions satisfy the task requirements |
| **READ (File-Reading)** | `run_fileread.py` | Checks whether an agent read all required files |

## Supported Tasks

| Task ID | Description |
|---|---|
| `cg/lv1` | Code generation, level 1 |
| `cg/lv2` | Code generation, level 2 |
| `cg/lv3` | Code generation, level 3 |
| `exec/execute` | Execute a function |
| `exec/testing` | Test a function |
| `fm/aef` | Add Existing File |
| `fm/anf` | Add New File |
| `fm/delf` | Delete File |
| `fm/delif` | Delete Irrelevant File |

## How to Run

### Rule-Based Metrics

Computes rule-based metrics between agent outputs and ground-truth source files.

```bash
python run_rb.py \
  --model_id <openrouter_model_id> \
  --task <task_id> \
  --outdir <path_to_agent_outputs> \
  --truthdir [Source_Code | Source_Code_no_code]
```

Use `Source_Code_no_code` for Code Generation and `Source_Code` for other tasks. Optional flags:
- `--new` — ignore existing cached results and recompute from scratch
- `--json <name>` — use a custom samples JSON filename (default: `run_samples`)

Results are written to:
```
<outdir>/<task>/<model_id>/
  ruled_metrics.json        # per-sample metric dict
  ruled_syntax_error.txt    # samples that failed to parse
  ruled_other_error.txt     # samples that raised other errors
```

### LLM-judge metrics

First, create `.jsonl` files, with each line containing an object in the following format:

```jsonc
{
  "<id>": "[framework_id]/cg/lv1", // or other relevant identifiers
  "<prompt>": "<the prompt for the judge>"
}
```

Then, update the `DATA_FILES` variable in `run_judge.py` to point to the newly created `.jsonl` files.

```bash
python run_judge.py \
  --outdir <path_to_save_judge_results> \
  --json <path_to_jsonl_file>
```

Optional flags:
- `--jm <model>` — judge model (default: `google/gemini-3-flash-preview`)
- `--limit <n>` — cap the number of samples to judge

Results are saved as `<outdir>/<stem>.json` where `stem` is the input filename without extension.
