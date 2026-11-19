# Intelligent CI/CD Pipeline Failure Assistant

Assignment 1 Set 2 (Group 8). This Streamlit app presents four simulated CI/CD failure scenarios to six agents: five classical agents (Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based, Learning) and an LLM agent using a local Ollama model through LangChain (`langchain-ollama`) with tool calling. Each agent analyzes the same scenario data and recommends a troubleshooting step. The assistant does not change code or deploy.

## Project structure

| File | Purpose |
|---|---|
| `scenarios.py` | Defines scenarios A–D and their pipeline, test, change, dependency, health, and history data |
| `tools.py` | Read-only scenario inspection tools used by the LLM agent (`get_pipeline_status`, `read_build_logs`, `get_test_results`, `get_recent_change_summary`, `get_dependency_info`, `get_deployment_health`) |
| `agents.py` | Implements the five classical agents and shared decision-making helpers |
| `llm_agent.py` | Implements the LangChain + Ollama (`ChatOllama`) tool-calling LLM agent (requires at least 2 distinct tool calls before answering) |
| `app.py` | Streamlit UI for selecting a scenario, configuring the Ollama model, viewing agent recommendations, and recording Learning-agent feedback |
| `run_tests.py` | Runs all scenarios against the classical agents (and optionally the LLM agent with `--llm`) and writes `test_results.md` |
| `test_results.md` | Recorded results from the latest test run |
| `experience.json` | Created when feedback is recorded; stores the Learning agent's action success/failure counts |

## Setup

From this directory, create and activate a virtual environment, then install the project requirements:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

To enable the **LLM (Ollama)** agent, install [Ollama](https://ollama.com) (on Windows you can also run `winget install Ollama.Ollama`), pull a tool-capable model (such as `qwen3:8b`, `llama3.1`, or a smaller `qwen3:4b` if RAM/VRAM is limited), and ensure the Ollama service is running:

```bash
ollama pull qwen3:8b   # or qwen3:4b for lower-memory machines
ollama serve           # if not already running (or use the Ollama tray app)
```

## Run

Start the app from this directory:

```bash
streamlit run app.py
```

Choose a scenario in the sidebar, set the **Ollama model** (default `qwen3:8b`) or uncheck **Run LLM agent (needs Ollama)** to run only the five classical agents, and click **Run all agents**. The app displays each recommendation, its evidence, reasoning, verification checklist, the LLM agent's tool-call trace, a comparison table, and the Learning agent's experience. Use the feedback buttons to record whether the Learning agent's recommendation worked.

Run the classical-agent checks with:

```bash
python run_tests.py
```

To also verify the LLM agent (checks failure category and that at least 2 distinct tools are called):

```bash
python run_tests.py --llm --model qwen3:8b
```

The test runner uses in-memory Learning-agent experience and does not modify `experience.json`.

## Scenarios

| ID | Type | Description | Expected category |
|---|---|---|---|
| A | Normal | Two cart discount tests fail after a change to `cart/pricing.py` | `TEST_FAILURE` |
| B | Critical / mixed signals | A dependency version conflict blocks the build while a separate flaky test fails | `DEPENDENCY_ISSUE` |
| C | Post-release | Tests pass, but `/healthz` returns 503 because `PAYMENT_API_URL` is missing | `DEPLOYMENT_HEALTH` |
| D | Edge / ambiguous | A known flaky timeout fails in a test unrelated to a README-only change | `TEST_FAILURE` |

## How the agents work

- **Simple Reflex** applies condition-action rules to the current scenario data; it has no memory.
- **Model-Based Reflex** also considers internal state such as the last successful commit, changed files, failure history, and known flaky tests.
- **Goal-Based** compares root-cause hypotheses and selects the first step in the plan for the best-supported hypothesis.
- **Utility-Based** scores possible actions using estimated usefulness, severity, time cost, and risk.
- **Learning** combines evidence-based usefulness with Laplace-smoothed success/failure experience. Feedback recorded in the UI affects later recommendations.
- **LLM (Ollama)** investigates the scenario by calling read-only tools from `tools.py`, then returns a structured JSON decision grounded in the tool results. The UI shows each tool call and its output.

## Comparison

The following are the results recorded in `test_results.md`:

| Scenario | Simple Reflex | Model-Based Reflex | Goal-Based | Utility-Based | Learning | LLM (Ollama) |
|---|---|---|---|---|---|---|
| A | `inspect_test_failures` | `inspect_test_failures` | `inspect_test_failures` | `inspect_test_failures` | `inspect_test_failures` | `inspect_test_failures` |
| B | `inspect_test_failures` | `rerun_failed_tests` | `check_dependency_pins` | `check_dependency_pins` | `check_dependency_pins` | `check_dependency_pins` |
| C | `inspect_deploy_health` | `inspect_deploy_health` | `inspect_deploy_health` | `inspect_deploy_health` | `inspect_deploy_health` | `inspect_deploy_health` |
| D | `inspect_test_failures` | `rerun_failed_tests` | `inspect_test_failures` | `rerun_failed_tests` | `inspect_test_failures` | `inspect_test_failures` |

### Why decisions differ

In scenarios A and C, the evidence points clearly to a test regression or a deployment-health issue, so all six agents agree. Scenarios B and D have mixed signals:

- In **B**, the dependency conflict is the actual build issue, but the parallel flaky-test failure can mislead Simple Reflex and Model-Based Reflex. Goal-Based, Utility-Based, Learning, and LLM (Ollama) all identify the dependency issue and recommend checking dependency pins.
- In **D**, the failing test is known to be flaky and is unrelated to the changed README. Model-Based Reflex and Utility-Based recommend rerunning it; Simple Reflex, Goal-Based, and LLM (Ollama) recommend inspecting it. Learning's recommendation starts at `inspect_test_failures` and switches to `rerun_failed_tests` as failure feedback is recorded.

These are simulated scenarios and demonstrate how the agents' different decision strategies can produce different recommendations.

## Test results

See [`test_results.md`](test_results.md) for the recorded per-agent results and the Learning-agent experience-update check. Run `python run_tests.py` (or `python run_tests.py --llm --model qwen3:8b` with Ollama running) to regenerate the results.

## Screenshots

Capture the app's decision cards, comparison table, Learning agent's experience table, and the LLM agent's **Tool calls** expander for scenarios A–D before submission, and save the screenshots in a `screenshots/` directory.
