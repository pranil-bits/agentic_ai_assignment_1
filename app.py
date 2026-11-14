"""Streamlit UI: pick a scenario, run all agents on identical data, compare decisions."""
import pandas as pd
import streamlit as st

from agents import ACTIONS, AGENT_REASONS, LearningAgent, classical_agents
from scenarios import SCENARIOS

st.set_page_config(page_title="CI/CD Failure Assistant", layout="wide")
st.title("Intelligent CI/CD Pipeline Failure Assistant")
st.caption("Recommends the next troubleshooting step only. It never changes code or deploys.")

sid = st.sidebar.selectbox("Scenario", list(SCENARIOS), format_func=lambda k: f"{k}: {SCENARIOS[k]['title']}")
s = SCENARIOS[sid]

st.subheader(f"Scenario {sid}: {s['title']}")
with st.expander("Shared scenario data (identical input for all agents)"):
    st.json(s)
    st.code(s["logs"], language="text")

if st.button("Run all agents", type="primary"):
    decisions = [a.decide(s) for a in classical_agents()]
    st.session_state["res"] = {"sid": sid, "decisions": decisions}

res = st.session_state.get("res")
if not res or res["sid"] != sid:
    st.info("Select a scenario and click **Run all agents**.")
    st.stop()

decisions = res["decisions"]

st.subheader("Agent decisions")
for i in range(0, len(decisions), 3):
    cols = st.columns(3)
    for col, d in zip(cols, decisions[i:i + 3]):
        with col, st.container(border=True):
            st.markdown(f"### {d.agent}")
            st.markdown(f"**Category:** `{d.category}`  \n**Action:** `{d.action}`")
            st.markdown(f"**Next step:** {d.next_step}")
            st.markdown(f"**Likely cause:** {d.cause}")
            st.markdown("**Evidence:**")
            for e in d.evidence:
                st.markdown(f"- {e}")
            with st.expander("Reasoning"):
                st.write(d.reasoning)
            with st.expander("Post-fix verification checklist"):
                for c in d.checklist:
                    st.checkbox(c, key=f"{sid}-{d.agent}-{c}")
st.subheader("Comparison")
df = pd.DataFrame([{"Agent": d.agent, "Category": d.category, "Action": d.action,
                    "Likely cause": d.cause} for d in decisions])
st.dataframe(df, use_container_width=True, hide_index=True)

groups = {}
for d in decisions:
    groups.setdefault(d.action, []).append(d.agent)
if len(groups) == 1:
    st.success("All agents recommend the same action for this scenario.")
else:
    st.warning("Agents disagree on the next action.")
    for a, ags in groups.items():
        st.markdown(f"- **`{a}`**: {', '.join(ags)}")
    st.markdown("**Why decisions differ:**")
    for d in decisions:
        st.markdown(f"- **{d.agent}** {AGENT_REASONS[d.agent]}")

st.subheader("Learning agent: experience and feedback")
la = next(d for d in decisions if d.agent == "Learning")
learner = LearningAgent()
st.dataframe(pd.DataFrame([{"Action": a, "Successes": e["success"], "Failures": e["failure"],
                            "Success rate (Laplace)": round(learner.rate(a), 2)}
                           for a, e in learner.exp.items()]), hide_index=True, use_container_width=True)
st.write(f"Feedback on the Learning agent's recommendation `{la.action}` updates experience.json:")
c1, c2 = st.columns(2)
if c1.button("This recommendation worked"):
    learner.record(la.action, True)
    st.success("Recorded success. Click 'Run all agents' again to see the effect.")
if c2.button("This recommendation failed"):
    learner.record(la.action, False)
    st.error("Recorded failure. Click 'Run all agents' again to see the effect.")
