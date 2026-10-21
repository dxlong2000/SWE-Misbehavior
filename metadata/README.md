This directory contains sample metadata for all experiments. 

```
metadata/
├── cg/
│   ├── lv1/samples.json      # 1253 samples
│   ├── lv2/samples.json      # 1253 samples
│   └── lv3/samples.json      #  570 samples
├── exec/
│   ├── execute/samples.json  #  570 samples
│   └── testing/samples.json  #  570 samples
├── fm/
│   ├── aef/samples.json      #  257 samples
│   ├── anf/samples.json      #  904 samples
│   ├── delf/samples.json     # 1000 samples
│   └── delif/samples.json    # 1050 samples
└── prompt-templates/         # raw templates used to generate the prompts
```


## Sample Schema

Every sample is a JSON object keyed by a sample ID (e.g. `"s1"`). The `prompt` field is always a list of 50 paraphrased variants; the run scripts pick one with `random.choice`.

### Code Generation (`cg`)

| Field | Description |
|---|---|
| `namespace` | Fully-qualified Python name of the target function |
| `completion_path` | Path to the original source file (ground truth) in `Source_Code/` |
| `new_completion_path` | Path to the copy with the function body removed, in `Source_Code_no_code/` |
| `project_path` | Root directory of the project within the source tree |
| `function_name` | Short name of the function to implement |
| `prompt` | 50 task prompt variants |
| `need_read` | Files the agent must read to solve the task |

**Level differences:**

| Level | Meaning | `need_read` |
|---|---|---|
| `lv1` | Function-level | 1 file |
| `lv2` | File-level | 1 file |
| `lv3` | Repository-level | 2+ files |

### System Interaction (`exec`)

The schema is identical to that of Code Generation, except for the omission of `new_completion_path`.

* `execute` prompts ask the agent to **run** the function; 
* `testing` prompts ask it to **test** the function.

### File Management (`fm`)

#### `aef` — Add Existing File (move a function to another file)

* `namespace`, `function_name` and `prompt`: same as in Code Generation
* `completion_path`: the file contain the target function 
* `need_update`: the files need to be updated after moving the target function

#### `anf` — Add New File (add a function to a new location)

Same schema as `aef`. The prompt asks to add the function to a **new** file rather than an existing one.

#### `delf` — Delete File

```jsonc
{
  "<sample_id>": {
    "completion_path": <the file to delete>,
    "prompt": [...]
  }
}
```

#### `delif` — Delete Irrelevant File

```jsonc
{
  "<sample_id>": {
    "completion_path": <the target Python leaf package>,
    "prompt": [...],
    "dm": [<the file to delete>],
    "taken_from": [<where it comes from>],
    "need_read": [<all files in the package, including the dummy>]
  }
}
```

## Prompt Templates

`prompt-templates/` contains the raw templates used to generate the 50 prompt variants in each `samples.json`. They are provided for reference only; the run scripts use the pre-generated prompts in `samples.json`.
