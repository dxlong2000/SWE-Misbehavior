This directory unifies three agent-framework experiment implementations - **sm** (smolagents), **oh** (openhands), and **ag** (agno). 

## Shared Abstractions

| Module | What it provides |
|--------|-----------------|
| `common.config` | `DEVEVAL`, `API_KEY`, `load_lessons()`, cross-platform `file_lock()`, `save_run_samples()` |
| `common.utils` | `find_recent_modified_files()`, `get_local_dependencies()`, `normalize()`, `extract_python_code()` |
| `common.tools_core` | Pure-Python implementations of all tools (find_reference_files, write_function_implementation, etc.) |
| `common.file_tracking` | `categorize_modified_files()`, `log_file_history()`, `restore_environment()`, `check_already_done()` |
| `common.batch` | `run_batch()` — parallel execution with environment cloning and Queue-based work distribution |

## How to Run

### Single sample

```bash
cd experiments

# Code Generation
python run_cg_one.py --framework sm --lv 1 --model_id openai/gpt-4o-mini \
    --workdir SC_sm_cg_lv1_env0 --key s1 --full_tools

# System Interaction
python run_exec_one.py --framework oh --lv execute --model_id openai/gpt-4o-mini \
    --workdir SC_oh_exec_execute_env0 --key s1

# File Management
python run_fm_one.py --framework ag --lv aef --model_id openai/gpt-4o-mini \
    --workdir SC_ag_fm_aef_env0 --key s1
```

### Batch

```bash
# Code Generation
python run_cg_batch.py --framework sm --lv 1 --model_id openai/gpt-4o-mini \
    --parallel 4 --num_samples 10

# System Interaction
python run_exec_batch.py --framework oh --lv execute --model_id openai/gpt-4o-mini \
    --parallel 4 --num_samples 10

# File Management
python run_fm_batch.py --framework ag --lv aef --model_id openai/gpt-4o-mini \
    --parallel 4 --num_samples 10
```

### Common arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--framework` | `sm`, `oh`, or `ag` | required |
| `--model_id` | OpenRouter model ID | required |
| `--lv` | Level (cg: 1/2/3, exec: execute/testing, fm: aef/anf/delf/delif) | required |
| `--workdir` | Working directory name (one scripts only) | required |
| `--key` | Sample key (one scripts only) | required |
| `--outdir` | Output directory | `results` |
| `--mnr` | Max retries on no-response | 3 |
| `--toolsel` | Use tool selector | off |
| `--guidelines` | Use guideline selector | off |
| `--parallel` | Parallel workers (batch only) | 4 |
| `--num_samples` | Max samples (batch only) | all/200/50 |
| `--json` | JSON metadata file name | `samples` |
