# Intelligent CI/CD Pipeline Failure Assistant

Assignment 1 Set 2 (Group 8). This Streamlit app presents four simulated CI/CD failure scenarios to five classical agents. Each agent analyzes the same scenario data and recommends a troubleshooting step. The assistant does not change code or deploy.

## Project structure

| File | Purpose |
|---|---|
| `scenarios.py` | Defines scenarios A–D and their pipeline, test, change, dependency, health, and history data |
| `agents.py` | Implements the five classical agents and shared decision-making helpers |
| `app.py` | Streamlit UI for selecting a scenario, viewing agent recommendations, and recording Learning-agent feedback |
| `run_tests.py` | Runs all five agents against all scenarios and checks the expected categories |
| `test_results.md` | Recorded results from the latest test run |
| `experience.json` | Created when feedback is recorded; stores the Learning agent's action success/failure counts |
| `tools.py` | Read-only scenario inspection helpers; not used by the current five-agent UI |

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

## Run

Start the app from this directory:

```bash
streamlit run app.py
```

Choose a scenario and click **Run all agents**. The app displays each recommendation, its evidence and reasoning, a comparison table, and the Learning agent's experience. Use the feedback buttons to record whether that agent's recommendation worked.

Run the classical-agent checks with:

```bash
python run_tests.py
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

## Comparison

The following are the results recorded in `test_results.md`:

| Scenario | Simple Reflex | Model-Based Reflex | Goal-Based | Utility-Based | Learning |
|---|---|---|---|---|---|
| A | `inspect_test_failures` | `inspect_test_failures` | `inspect_test_failures` | `inspect_test_failures` | `inspect_test_failures` |
| B | `inspect_test_failures` | `rerun_failed_tests` | `check_dependency_pins` | `check_dependency_pins` | `check_dependency_pins` |
| C | `inspect_deploy_health` | `inspect_deploy_health` | `inspect_deploy_health` | `inspect_deploy_health` | `inspect_deploy_health` |
| D | `inspect_test_failures` | `rerun_failed_tests` | `inspect_test_failures` | `rerun_failed_tests` | `inspect_test_failures` |

### Why decisions differ

In scenarios A and C, the evidence points clearly to a test regression or a deployment-health issue, so the agents agree. Scenarios B and D have mixed signals:

- In **B**, the dependency conflict is the actual build issue, but the parallel flaky-test failure can mislead Simple Reflex and Model-Based Reflex. Goal-Based, Utility-Based, and Learning recommend checking dependency pins.
- In **D**, the failing test is known to be flaky and is unrelated to the changed README. Model-Based Reflex and Utility-Based recommend rerunning it; Simple Reflex and Goal-Based recommend inspecting it. Learning's recommendation can change as experience is recorded.

These are simulated scenarios and demonstrate how the agents' different decision strategies can produce different recommendations.

## Test results

See [`test_results.md`](test_results.md) for the recorded per-agent results and the Learning-agent experience-update check. Run `python run_tests.py` to regenerate the results.

## Screenshots

Capture the app's decision cards and comparison table for scenarios A–D before submission, and save the screenshots in a `screenshots/` directory.
