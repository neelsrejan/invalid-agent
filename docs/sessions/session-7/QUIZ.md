# Session 7 quiz

1. Why is rules-only the default on the hosted page?
2. Which environment variable names the model, and what does the page request when it is unset and rules-only is off?
3. Why does the before/after chart say the after series is not observed follow-up?
4. What is cached, and what is not recomputed when you only change the audience radio?
5. What does Neel still have to do before a public Streamlit URL exists?

## Answers

1. Streamlit Community Cloud's free RAM is too small for an 8B model, and this repo does not ship weights. The deterministic templates answer without a download. A missing model is a fallback, not a crash.
2. `LLM_MODEL`. Hosted Streamlit runs rules-only (deterministic); Streamlit Cloud has no Ollama. On a local or self-hosted machine, with the toggle off and `LLM_MODEL` unset, the page asks Ollama for `llama3.2:1b` (Llama 3.2 1B). The CLI default, when the variable is unset, remains `llama3.1:8b`.
3. `projection_summary` clears invalids on the leading stratum of the same synthetic file. No new field data were collected. The label says so.
4. `_run` is cached on scenario, week, backend, and model. The audience radio only picks a string already stored on `status_updates`.
5. Sign in to Streamlit Community Cloud with GitHub and select `app/streamlit_app.py` (or the root `streamlit_app.py`). The repo cannot do that sign-in.
