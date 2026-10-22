<h1 align="center">SWE-Misbehavior: Benchmarking and Mitigating Boundary Violations in Software Coding Agents</h1>

<p align="center">
  Do Xuan Trong<sup>*1,5</sup>, Duc Anh Nguyen<sup>*1,2</sup>, Do Xuan Long<sup>†1,3</sup>, Ngoc-Hai Nguyen<sup>1,4</sup>,
  Tongyao Zhu<sup>1</sup>, Duy Dinh<sup>1</sup>, Cayden Chik<sup>1</sup>, Cuong Dang<sup>6</sup>, Jiaying Wu<sup>1</sup>, Xuan-Phi Nguyen<sup>7</sup>,
  Vinh Van Nguyen<sup>5</sup>, Kenji Kawaguchi<sup>1</sup>, Shafiq Joty<sup>7</sup>, Nancy F. Chen<sup>3</sup>, Min-Yen Kan<sup>1</sup>
</p>

<p align="center">
  <sup>1</sup>National University of Singapore, <sup>2</sup>University of Virginia, USA,
  <sup>3</sup>Agency for Science, Technology and Research (A*STAR), Singapore, <sup>4</sup>Tufts University, USA,
  <sup>5</sup>Vietnam National University, Hanoi, <sup>6</sup>Virginia Tech, USA, <sup>7</sup>Salesforce AI Research, USA
</p>

<p align="center">
  <sup>*</sup>Equal contribution. Work done during the internship at WING, NUS. &nbsp; <sup>†</sup>Project lead. Correspondence: <a href="mailto:xuanlong.do@u.nus.edu">xuanlong.do@u.nus.edu</a>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2610.18206"><img src="https://img.shields.io/badge/arXiv-2610.18206-b31b1b.svg" alt="arXiv"></a>
  <a href="https://huggingface.co/datasets/duc-anh-2002/SWE-Misbehavior"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-SWE--Misbehavior-ffd21e" alt="Hugging Face Dataset"></a>
  <img src="https://img.shields.io/badge/python-3.12%2B-3776ab?logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/agents-smolagents%20%7C%20OpenHands%20%7C%20agno-6f42c1" alt="Agent frameworks">
</p>

---

## 📖 Overview

**SWE-Misbehavior** measures **boundary violations** made by software coding agents, meaning actions that go beyond what the user asked for. Examples include rewriting code around the target function, changing signatures, touching unrelated files, deleting the wrong files, running unrequested commands, or skipping files the agent needed to read.

The benchmark has **7,427 task instances** in **3 task families** and **9 subsets**. All are built on real-world Python repositories from [DevEval](https://huggingface.co/datasets/LJ0815/DevEval), and each instance comes with **50 paraphrased prompt variants**.

| Task family | Subsets | # Samples |
|---|---|---:|
| 🧩 Code Generation (`cg`) | `lv1` · `lv2` · `lv3` | 3,076 |
| ⚙️ System Interaction (`exec`) | `execute` · `testing` | 1,140 |
| 📁 File Management (`fm`) | `aef` · `anf` · `delf` · `delif` | 3,211 |

🤗 **The dataset is on the Hugging Face Hub: [`duc-anh-2002/SWE-Misbehavior`](https://huggingface.co/datasets/duc-anh-2002/SWE-Misbehavior)**

```python
from datasets import load_dataset
ds = load_dataset("duc-anh-2002/SWE-Misbehavior", "cg_lv1", split="test")
```

## 📑 Contents

- [Repository Structure](#-repository-structure)
- [Data Setup](#-data-setup)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running Experiments](#-running-experiments)
- [Evaluation](#-evaluation)
- [Resume & Restart](#-resume--restart)
- [Common Issues](#-common-issues)
- [Citation](#-citation)

## 🗂 Repository Structure

```
SWE-Misbehavior/
├── metadata/              # Task metadata (samples.json per subset) + prompt templates
├── experiments/           # Agent runners for smolagents (sm), OpenHands (oh), agno (ag)
├── evaluation/            # Rule-based and LLM-judge metrics
├── Source_Code_no_code/   # Source tree with target function bodies removed (for cg)
├── create_delif_env.py    # Builds the environment for the fm/delif subset
└── all_files_*.txt        # File listings used to track environment changes
```

See [`metadata/README.md`](metadata/README.md), [`experiments/README.md`](experiments/README.md) and [`evaluation/README.md`](evaluation/README.md) for details.

## 📦 Data Setup

Download the DevEval source tree from [here](https://huggingface.co/datasets/LJ0815/DevEval/blob/main/Source_Code.tar.gz), move the archive into this folder, and run:

```bash
tar -xzf Source_Code.tar.gz
find Source_Code -type d -name "__pycache__" -exec rm -r {} +
python create_delif_env.py
```

> [!IMPORTANT]
> `all_*.txt` files and `Source_Code_no_code/` must be present before you run any experiment.

The task metadata is in `metadata/` (see [`metadata/README.md`](metadata/README.md)). It is also on the Hugging Face Hub as [`duc-anh-2002/SWE-Misbehavior`](https://huggingface.co/datasets/duc-anh-2002/SWE-Misbehavior), with a dataset viewer.

## 🛠 Installation

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

## 🔑 Configuration

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

## 🚀 Running Experiments

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
| `--toolsel` | | Enable tool selector (AST tools, jedi) |
| `--guidelines` | | Enable guideline selector |
| `--json` | | Metadata file name (default: `samples`) |

### Levels (`--lv`)

| Experiment | `--lv` values |
|---|---|
| Code Generation (`cg`) | `1`, `2`, `3` |
| System Interaction (`exec`) | `execute`, `testing` |
| File Management (`fm`) | `aef`, `anf`, `delf`, `delif` |

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

## 📊 Evaluation

Evaluation uses two families of metrics:

- **Rule-based metrics (code misbehaviors):** context changes, signature changes, and changes to the target function.
- **LLM-judge metrics:** file reading, environment misbehaviors, and instruction following.

```bash
python evaluation/run_rb.py --model_id <model_id> --task cg/lv1 --outdir <agent_outputs> --truthdir Source_Code_no_code
python evaluation/run_judge.py --outdir <judge_results> --json <prompts.jsonl>
```

See [`evaluation/README.md`](evaluation/README.md) for the full guide.

## 🔁 Resume & Restart

Completed samples are tracked across runs. When you re-run a batch script on a partially finished set, you will be prompted:

```
You've already run N samples. Proceed with next M? ('c' continue, 'r' restart, <other> quit)
```

To re-run only failed samples, press `r` to reset the tracker.

## ⚠️ Common Issues

**Windows** - `fcntl` is not available on Windows. The cross-platform lock in `common/config.py` falls back to `msvcrt` (advisory) or a no-op. For parallel batch runs on Windows, avoid very high `--parallel` values.

## 📝 Citation

If you find SWE-Misbehavior useful, please cite our paper:

```bibtex
@article{trong2026swe,
  title={SWE-MISBEHAVIOR: Benchmarking and Mitigating Boundary Violations in Software Coding Agents},
  author={Trong, Do Xuan and Nguyen, Duc Anh and Long, Do Xuan and Nguyen, Ngoc-Hai and Zhu, Tongyao and Dinh, Duy and Chik, Cayden and Dang, Cuong and Wu, Jiaying and Nguyen, Xuan-Phi and others},
  journal={arXiv preprint arXiv:2610.18206},
  year={2026}
}
```

## 🙏 Acknowledgements

This benchmark is built on the repositories collected by [DevEval](https://huggingface.co/datasets/LJ0815/DevEval).

## ⭐ Star History

<a href="https://www.star-history.com/#dxlong2000/SWE-Misbehavior&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=dxlong2000/SWE-Misbehavior&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=dxlong2000/SWE-Misbehavior&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=dxlong2000/SWE-Misbehavior&type=Date" />
  </picture>
</a>
