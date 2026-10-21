## Data Setup

Download the DevEval dataset from [here](https://huggingface.co/datasets/LJ0815/DevEval/blob/main/Source_Code.tar.gz) and move the archive into this folder, then run:

```bash
tar -xzf Source_Code.tar.gz
find Source_Code -type d -name "__pycache__" -exec rm -r {} +
python create_delif_env.py
```

`all_*.txt` files and `Source_Code_no_code/` must be present before running any experiment.

For metadata, please refer to `metadata/README.md`.

## Installation

Requires **Python 3.12+**. Install only the framework(s) you need.

```bash
# smolagents (sm)
uv pip install "smolagents[toolkit,openai]"

# OpenHands (oh)
uv pip install openhands-sdk openhands-tools openhands-workspace openhands-agent-server

# agno (ag)
uv pip install agno
```

Also install shared dependencies used by all frameworks:

```bash
uv pip install jedi
```

## Configuration

Open `experiments/common/config.py` and set:

```python
API_KEY = "<your OpenRouter API key>"
```

`DEVEVAL` is set automatically to the current working directory at import time, so **always run scripts from the `SWE-Misbehavior/` root**:

```bash
cd SWE-Misbehavior
python experiments/run_cg_batch.py ...

# or
cd experiments
python run_cg_batch.py ...
```

## Running Experiments

All experiments are in `experiments/` and use a single `--framework` flag to select the agent backend.

### Single sample (for testing)

```bash
python run_cg_one.py --framework sm --lv 1 --model_id openai/gpt-4o-mini --workdir <workdir> --key s1
python run_exec_one.py --framework oh --lv execute --model_id openai/gpt-4o-mini --workdir <workdir> --key s1
python run_fm_one.py   --framework ag --lv aef --model_id openai/gpt-4o-mini --workdir <workdir> --key s1
```

`<workdir>` is the name of a source-code environment directory (created automatically by the batch script, or manually with `shutil.copytree`).

### Batch

```bash
python run_cg_batch.py --framework [sm | oh | ag] --lv [1 | 2 | 3] --model_id openai/gpt-4o-mini [options]
python run_exec_batch.py --framework [sm | oh | ag] --lv [execute|testing] --model_id openai/gpt-4o-mini [options]
python run_fm_batch.py --framework [sm | oh | ag] --lv [delf | delif | aef | anf] --model_id openai/gpt-4o-mini [options]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--framework` | ✓ | `sm`, `oh`, or `ag` |
| `--model_id` | ✓ | OpenRouter model ID, e.g. `openai/gpt-4o-mini` |
| `--lv` | ✓ | Level — see table below |
| `--outdir` | | Output directory (default: `results`) |
| `--num_samples` | | Max samples to run (default: all / 200 / 50) |
| `--parallel` | | Parallel workers (default: `4`) |
| `--mnr` | | Max retries on no-response (default: `3`) |
| `--full_tools` | | Enable full toolset (AST tools, jedi) |
| `--lessons` | | Append `lessons.txt` guidance to prompt |
| `--json` | | Metadata file name (default: `samples`) |

### Levels (`--lv`)

| Experiment | `--lv` values |
|---|---|
| Code generation (`cg`) | `1`, `2`, `3` |
| Execution (`exec`) | `execute`, `testing` |
| Function modification (`fm`) | `aef`, `anf`, `delf`, `delif` |

`aef` = add existing file, `anf` = add new file, `delf` = delete file, `delif` = delete irrelevant file.

### Output

Results are written to:

```
results/<framework>/<experiment>/<lv>/<model_id>/
  run_samples.json        # per-sample metrics
  file_history.txt        # file change log per sample
  run_status.txt          # [OK] / [FAIL] per sample (batch only)
  <path>/run_history_<key>.txt   # agent conversation history
  <path>/<key>.log               # subprocess stdout/stderr (batch only)
```

## Resume & Restart

Completed samples are tracked across runs. When you re-run a batch script on a partially finished set, you will be prompted:

```
You've already run N samples. Proceed with next M? ('c' continue, 'r' restart, <other> quit)
```

To re-run only failed samples, press `r` to reset the tracker.

## Common Issues

**Windows** - `fcntl` is not available on Windows. The cross-platform lock in `common/config.py` falls back to `msvcrt` (advisory) or a no-op. For parallel batch runs on Windows, avoid very high `--parallel` values.
