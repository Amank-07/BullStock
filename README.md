## BullStock – NSE Stock Analysis Tool

This project is a small, production‑style **NSE stock analysis app** built in Python with **Streamlit**.
It is designed for quick exploratory analysis of a single stock using CSV data downloaded directly
from the **NSE website**.

---

### Features

- **CSV upload & validation**
  - Accepts the standard NSE daily equity CSV with columns:  
    `DATE, SERIES, OPEN, HIGH, LOW, PREV. CLOSE, LTP, CLOSE, VWAP, 52W H, 52W L, VOLUME, VALUE, NO. OF TRADES`
  - Validates the header; if required columns are missing, shows a clear **“Invalid data format”** error and
    does **not** store the file locally.
  - Cleans data types (parses `DATE`, removes thousands separators like `1,444.00`, converts to numeric).

- **Core analysis / EDA**
  - Latest LTP and CLOSE price.
  - Daily change and % change vs `PREV. CLOSE`.
  - 52‑week high/low comparison and positioning.
  - Average volume and **highest volume day**.
  - Simple **trend classification** (bullish / bearish / sideways) based on recent closes and returns.
  - Volatility metrics using intraday **HIGH–LOW range** and **CLOSE returns**.

- **Visualizations**
  - Line chart of **CLOSE price over time**.
  - Bar chart of **VOLUME over time**.
  - **VWAP vs CLOSE** price comparison chart.

- **Plain‑English summary**
  - Generates a human‑readable summary such as:
    - “The stock is trading close to its 52‑week high…”
    - “Average daily volume is … and the highest volume day was …”
    - “Over the last N sessions, the trend appears bullish/bearish/sideways…”

- **PDF report export**
  - Creates a one‑page **PDF report** with:
    - Key metrics (prices, 52‑week range, volume, trend, volatility).
    - The same English summary shown in the app.
  - Downloadable via a **“Download PDF Report”** button in the UI.

---

### Tech Stack

- **Language**: Python 3
- **Data & analysis**: pandas, numpy
- **Visualizations**: matplotlib, seaborn
- **Web UI**: Streamlit
- **Reporting**: reportlab (PDF generation)

---

### Project Structure

```text
Bullstock/
  nse_app.py          # Streamlit UI (main entry point)
  nse_loader.py       # CSV loading, validation, and cleaning
  nse_analysis.py     # Computation of all numeric insights + summary text
  nse_viz.py          # Matplotlib charts (price, volume, VWAP vs CLOSE)
  report_generator.py # PDF report creation using reportlab
  data/               # (Optional) local copies of valid uploaded CSVs
  README.md           # This file
  requirements.txt    # Python dependencies (recommended)
```

The `train.py`, `features.py`, etc. from the earlier ML experiment can coexist in this repo,
but the **NSE dashboard** is driven by the `nse_*.py` modules.

---

### How to Run the App

#### 1. Set up a virtual environment (recommended)

```bash
cd Bullstock
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS / Linux
```

#### 2. Install dependencies

Create a `requirements.txt` if you don’t already have one with at least:

```text
pandas
numpy
matplotlib
seaborn
streamlit
reportlab
```

Then install:

```bash
pip install -r requirements.txt
```

#### 3. Run the Streamlit app

```bash
streamlit run nse_app.py
```

Open the URL printed in the terminal (usually `http://localhost:8501`).

---

### Using the App

1. Go to the **NSE website**, download the daily equity CSV for a stock
   (e.g. RELIANCE) in the standard format.
2. In the app, upload the CSV file.
3. Adjust the **start** and **end** dates in the sidebar if needed.
4. Explore:
   - Key metrics at the top.
   - Price, volume, and VWAP vs CLOSE charts.
   - Trend and volatility section.
   - Summary analysis paragraph.
5. Click **“Download PDF Report”** to save a snapshot of the analysis.

---

### Notes & Extensions

- The analysis is intentionally simple and rule‑based to keep it transparent.
- It can be extended with:
  - Technical indicators (RSI, MACD, moving averages).
  - Multi‑stock comparison.
  - Backtesting of simple trading rules.

> This tool is for **educational purposes only** and does **not** constitute financial advice.

# BullStock