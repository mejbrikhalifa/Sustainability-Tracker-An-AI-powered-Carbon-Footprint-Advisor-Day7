## Safeguards

This project includes several safeguards to keep tips trustworthy, stable, and privacy‑conscious.

- **Input sanitization**
  - Implemented in `ai_tips.py` via `sanitize_inputs_for_prompt()` (alias of `_sanitize_inputs_for_prompt`).
  - Only allows known activity keys from `CATEGORY_MAP`.
  - Coerces values to floats, converts negatives to 0, and clamps extremes to heuristic thresholds in `EXTREME_THRESHOLDS`.
  - Prevents prompt‑injection by ignoring unexpected keys and non‑numeric content.

- **Output guardrails**
  - Implemented in `ai_tips.py` `_sanitize_tip_output()` and `clean_tip()`.
  - Removes URLs/HTML/code blocks, filters endorsements/medical terms, normalizes whitespace.
  - Caps tip length (~220 chars) and enforces concise UI display (1–2 short sentences).

- **Caching and backoff**
  - GPT prompts use exponential backoff with jitter and a short negative cache to avoid repeated failures.
  - UI (`app.py`) adds `st.cache_data` caching for tips using a normalized numeric key of user inputs.

- **Fallbacks**
  - If GPT is unavailable or inputs are ambiguous, deterministic local tips are generated.
  - Summary generation has a rules‑based fallback when the API errors.

- **Privacy**
  - No PII is collected. User inputs are simple numeric activity values.
  - API keys are read from environment variables (e.g., `.env`), not embedded in code.

If you find an area where an additional guardrail would help, please open an issue or PR.

# Sustainability Tracker 🌍

![Updated](https://img.shields.io/badge/updated-2025--10--03-blue) ![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b)

Track your daily CO₂ emissions across Energy, Transport, and Meals. Get personalized eco-tips (GPT with fallback), view history and trends, and export beautiful PDF summaries with your branding.

Last updated: 2025-10-03

---

## Features

- **Dashboard** (Energy, Transport, Meals) with compact/comfy density
- **Personalized Eco Tips**
  - GPT-powered tips with resilient local fallback
  - Source badge (GPT vs Fallback)
- **History & Trends**
  - Per-category KPIs
  - 7-day change metrics, sparklines (in PDF)
- **Exports**
  - CSV downloads (Dashboard + History tab)
  - PDF export (server-side) with branding:
    - Title, logo (upload or fallback), accent color, text color, chart background
    - Optional pie chart and 7-day sparklines
    - Footer with &copy;/URL + page numbers
- **Demo Mode**
  - One-click demo values, “Exit Demo Mode” restore
  - Snapshot of pre-demo values and density + status indicator
  - “View snapshot detail” popover
- **Presets**
  - Prefill demo/presets safely (no widget state errors)
- **Robust UX**
  - Theme-aware defaults (light/dark)
  - Safe reruns (no deprecated APIs), no duplicate widget keys

---

## Quickstart

### Requirements

- Python 3.9+
- Pip packages:
  - streamlit
  - pandas
  - python-dotenv
  - openai (for GPT tips, optional)
  - reportlab (for PDF export)
  - matplotlib (optional, for PDF charts)

### Install

Using Anaconda (Windows)
```powershell
conda create -n sustain python=3.10 -y
conda activate sustain
pip install streamlit pandas python-dotenv openai reportlab matplotlib
```

Using pip (Windows PowerShell)
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install streamlit pandas python-dotenv openai reportlab matplotlib
```

### Run

```powershell
streamlit run app.py
```

Streamlit will open at:
- Local URL: http://localhost:8501
- Network URL: http://<your-ip>:8501

### Tech Stack

- **Frontend/UI**: Streamlit
- **AI Tips**: OpenAI Chat Completions API (optional; robust local fallback if unavailable)
- **Data/Storage**: CSV (`history.csv`) for daily entries, JSON for user prefs
- **Caching**: Streamlit `st.cache_data` + in-module negative cache for failed GPT calls
- **PDF**: ReportLab (optional Matplotlib for charts)
- **Experimentation/Charts**: Altair (with optional `altair_saver`), pandas

---

## Environment & AI Tips

Set your OpenAI API key to enable GPT tips (optional). Without it, the app falls back to local tips automatically with a clear source badge.

Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-...
```

If you see 429 “insufficient_quota” errors:
- The app will retry and then use a local fallback tip.
- You can continue testing without GPT; the UI shows “AI source: Fallback”.

## Secrets

<a id="secrets"></a>

- Store your OpenAI key in a local `.env` file next to `app.py` and never commit it.
- Alternative (temporary) for a single session in Windows PowerShell:
  ```powershell
  setx OPENAI_API_KEY "sk-..." /M
  # Or for current session only
  $env:OPENAI_API_KEY = "sk-..."
  ```
- If the key is missing or invalid, the app automatically falls back to local tips and the UI labels the source accordingly.

---

## Using the App

### Density & Layout
- Density toggle at the top: `Compact` (tight, best for PDF) or `Comfy`.
- “Reset layout” sets Compact and collapses expanders for better PDF export.

### Inputs
- Enter daily values in the three sections:
  - Energy: e.g., `electricity_kwh`, `natural_gas_m3`, `district_heating_kwh`...
  - Transport: `bus_km`, `train_km`, `petrol_liter`, etc.
  - Meals: `meat_kg`, `dairy_kg`, `vegetarian_kg`, etc.

### Calculate & Save
- Computes total emissions, KPIs, and saves to `history.csv`.
- CSV download buttons are uniquely keyed (no duplicate-widget errors).

### Eco Tips
- Generate a personalized tip based on today’s inputs.
- GPT-backed with fallback. Source badge shows “GPT” or “Fallback”.
- Copy-ready code blocks with built-in copy icon (no fragile JS).
- Summary and Tip are both shown as copyable code blocks and downloadable text.

### Prompt Testing Suite
- Run predefined scenarios across modes: `Contextualized`, `Directive`, `Persona`.
- Optional ambiguous/edge-case inputs to stress-test guardrails.
- Computes per-mode metrics: OK-rate (relevant, actionable, simple), uniqueness, bigram diversity.
- Bootstrap 95% CIs for OK-rate and diversity; charts via Altair.
- Export full results as CSV/MD/ZIP with embedded interactive HTML charts when available.

### Day 7: LLM Optimization & UI Polish
- LLM parameters are configurable at runtime:
  - `Tip temperature`, `Tip max_tokens`, `Summary temperature`, `Summary max_tokens`.
  - UI: Debug → “LLM settings” expander; persisted to `.user_prefs.json`.
  - Applied via `ai_tips.set_llm_params(...)` and used in GPT calls.
- Scoped tip cache invalidation: changing LLM settings bumps `tip_cache_salt` so new tips are regenerated.
- Error handling and loading states:
  - GPT errors are retried with backoff and then fall back to local tips; UI never crashes.
  - Tip area shows a placeholder and spinner when generation is slow.
- Advanced thresholds polish:
  - Thresholds are adjustable in the “Advanced: Edge-case thresholds” section.
  - Keys aligned with activity names; applied via `set_extreme_thresholds(...)`.
- Debug tools:
  - “Simulate API failures” toggle to exercise fallback paths.

### Demo Mode
- Toggle “Demo mode” in the header:
  - Forces Compact density on next run
  - Loads representative demo values
  - Auto-generates a tip
  - Shows snapshot capture time
  - “View snapshot detail” lets you inspect saved inputs
- “Exit Demo Mode” restores your previous values and density safely.

### Presets
- Prefill demos/presets via the “Prefill demos/presets” popover.
- Uses a “pending apply” mechanism to avoid Streamlit widget-state exceptions.

---

## PDF Export (Server-side)

Use the UI in the Eco Tips tab:
- “PDF Branding & Options” expander:
  - Title
  - Accent color (auto default by theme)
  - Text color (auto default by theme)
  - Chart background color (auto default by theme)
  - Include pie chart
  - Include 7-day sparklines
  - Margins (top/side/bottom)
  - Footer text and toggle
  - Logo upload (PNG/JPG). If none, fallback path check: `logo.png` in project root.
  - If no upload and no `logo.png`: a styled vector fallback badge (rounded rect “ST”) is drawn.
- Click “Generate Eco Tips PDF (beta)”, then the download button.

Dependencies:
- Required: `reportlab`
- Optional for charts: `matplotlib`

Install:
```powershell
pip install reportlab matplotlib
```

Note:
- The original “Export PDF tips” popover describes manual browser-based printing. The new server-side export produces a file directly.

---

## Files & Structure

- `app.py` — Main Streamlit app
  - Tabs: Dashboard, History, Breakdown, Tips
  - Demo mode, presets, density controls
  - CSV and PDF exports
  - AI source badge, copy-ready blocks
- `co2_engine.py` — Emissions engine
  - `CO2_FACTORS`, `calculate_co2()`, `calculate_co2_breakdown()`
- `utils.py` — Formatting, normalization, helper functions
  - `format_emissions()`, `percentage_change()`, `friendly_message()`, etc.
- `ai_tips.py` — GPT/local tips
  - `generate_tip()`; fallback-safe, retries
  - `LAST_TIP_SOURCE` to signal GPT vs Fallback
- `history.csv` — Saved user entries (auto-created)
- `logo.png` — Optional default logo for PDF
- `test_co2_engine.py`, `test_utils.py` — Sample tests

---

## Troubleshooting

- **DuplicateWidgetID**: Fixed by unique `key=` props on all download buttons.
- **StreamlitAPIException**: “cannot be modified after widget is instantiated”
  - We use pending state mechanisms (`_pending_values`, `_pending_density`, `_pending_demo_off`) and rerun before widgets build.
- **`st.experimental_rerun()` deprecated**
  - We use `st.rerun()` or avoid forced reruns with smooth success notices.
- **GPT quota errors (429)**
  - App retries and then falls back to local tips automatically.
- **Copy buttons “do nothing”**
  - Replaced with Streamlit code blocks. Use the built-in copy icon on the right.

---

## Testing

Run tests (if you add pytest):
```powershell
pip install pytest
pytest -q
```

---

## Changelog (2025-10-01)

- Added Demo Mode with snapshot, status, and “Exit Demo Mode” (safe).
- Fixed imports (use `co2_engine.calculate_co2` & local `get_yesterday_total`).
- Replaced all deprecated `st.experimental_rerun`.
- Unique `key` for download buttons to avoid DuplicateWidgetID.
- Reworked copy to built-in code-block copy icons.
- AI source badge (GPT vs Fallback).
- Server-side PDF export (ReportLab + optional Matplotlib):
  - Branding options and logo upload + fallback
  - Theme-aware defaults (accent, text, chart bg)
  - KPIs, summary, tip, per-category table, pie chart, per-activity table
  - 7-day sparklines per category
  - Footer (&copy;/URL + page numbers)
- Theme-aware colors and improved typography.

---

## Contributing

- **Issues/Ideas**: Open a GitHub issue describing the feature/bug with reproduction steps.
- **PRs**: Keep changes small and focused. Include before/after screenshots for UI changes.
- **Testing**: Prefer adding/adjusting unit tests where practical. See the Testing section.
- **Secrets**: Never commit real API keys; use `.env.example` if you need to illustrate variables.

---

## License

MIT (or add your license of choice)
