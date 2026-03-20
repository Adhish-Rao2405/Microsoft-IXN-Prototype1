# Robot LLM PyBullet Demo

A complete local Python project where a Franka Panda robot in PyBullet GUI picks up a cube from a table using LLM-generated strict JSON actions.

## Features

- PyBullet GUI simulation with:
  - plane
  - table
  - Franka Panda robot
  - one cube object
- CLI command loop
- Foundry Local integration via OpenAI-compatible `POST /v1/chat/completions`
- Uses `max_completion_tokens` (not `max_tokens`)
- Strict JSON-only action output, validated before execution
- Safety clamps for workspace, orientation, speed, gripper width, and force
- Required actions:
  - `describe_scene()`
  - `move_ee(target_xyz, target_rpy, speed)`
  - `open_gripper(width)`
  - `close_gripper(force)`
  - `pick(object)`
  - `place(target_xyz)`
  - `reset()`

## Requirements

- Python 3.10+
- Local GUI support for PyBullet

## Install

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Environment Variables

Base URL variable support:

- `FOUNDRY_LOCAL_BASE_URL` (preferred)
- `FOUNDY_LOCAL_BASE_URL` (supported alias)
- Default if neither is set: `http://127.0.0.1:8000`

Optional:

- `FOUNDRY_LOCAL_MODEL` (default: `gpt-4o-mini`)
- `FOUNDRY_LOCAL_API_KEY`
- `REQUEST_TIMEOUT_S` (default: `60`)
- `LLM_TEMPERATURE` (default: `0`)
- `MAX_COMPLETION_TOKENS` (default: `600`)
- `SIM_TIMESTEP` (default: `1/240`)

PowerShell example:

```powershell
$env:FOUNDRY_LOCAL_BASE_URL = "http://127.0.0.1:8000"
$env:FOUNDRY_LOCAL_MODEL = "your-local-model"
```

## Start Foundry Local First

Before running the app, start a local model server in Foundry Local so the OpenAI-compatible endpoint is available at:

- `POST /v1/chat/completions`

Typical sequence:

1. Open Foundry Local.
2. Download or select a local chat model.
3. Start the model server.
4. Confirm the server URL and port (for example `http://127.0.0.1:8000`).
5. Set environment variables in your shell.

PowerShell example:

```powershell
$env:FOUNDRY_LOCAL_BASE_URL = "http://127.0.0.1:8000"
$env:FOUNDRY_LOCAL_MODEL = "your-local-model"
```

Quick check before app startup:

```powershell
python -c "from src.config import Settings; s=Settings.from_env(); print(s.foundry_local_base_url, s.foundry_local_model)"
```

## Run

```bash
python -m src.app
```

Then type commands such as:

- `pick up the cube`
- `describe the scene`
- `reset`
- `exit`

## LLM Action Contract

The app asks the model to return strict JSON in this shape:

```json
{
  "actions": [
    {
      "action": "pick",
      "parameters": {
        "object": "cube"
      }
    }
  ]
}
```

No markdown, prose, or Python code is accepted. Invalid output is rejected and not executed.

## Acceptance Check

1. Start app with `python -m src.app`.
2. Enter `pick up the cube`.
3. Verify the robot performs pick and lift at least once in the GUI.

## Troubleshooting

- Foundry endpoint misconfigured or unreachable
  - Set `FOUNDRY_LOCAL_BASE_URL` (or `FOUNDY_LOCAL_BASE_URL`) to your local server URL, or use default `http://127.0.0.1:8000` and ensure the model server is running.
- LLM output parse/validation errors
  - Ensure your local model supports structured JSON output and follows the action contract.
- Robot does not pick cube
  - Retry command; physics can vary slightly. Use `reset` and run pickup again.

# Microsoft-IXN-Prototype1
Picking up a cube
