from __future__ import annotations

"""
Visualization helpers for the NSE stock analysis app.

Each function accepts a cleaned `pandas.DataFrame` with at least the
columns used inside (DATE, CLOSE, VOLUME, VWAP) and returns a Matplotlib
figure object ready to be rendered in Streamlit or any other frontend.
"""

import matplotlib.pyplot as plt
import pandas as pd


def plot_close_price_over_time(df: pd.DataFrame):
    """
    Create a simple line chart of the CLOSE price over time.
    """
    figure, axis = plt.subplots(figsize=(10, 4))
    axis.plot(df["DATE"], df["CLOSE"], label="Close", color="tab:blue")
    axis.set_title("Close Price Over Time")
    axis.set_xlabel("Date")
    axis.set_ylabel("Price")
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    return figure


def plot_volume_over_time(df: pd.DataFrame):
    """
    Create a bar chart of traded volume over time.
    """
    figure, axis = plt.subplots(figsize=(10, 3))
    axis.bar(df["DATE"], df["VOLUME"], color="tab:gray")
    axis.set_title("Volume Over Time")
    axis.set_xlabel("Date")
    axis.set_ylabel("Volume")
    figure.tight_layout()
    return figure


def plot_vwap_vs_close(df: pd.DataFrame):
    """
    Plot VWAP and CLOSE price together so the user can compare
    where the closing price sits relative to the volume-weighted
    average price for each session.
    """
    figure, axis = plt.subplots(figsize=(10, 4))
    axis.plot(df["DATE"], df["CLOSE"], label="Close", color="tab:blue")
    if "VWAP" in df.columns:
        axis.plot(df["DATE"], df["VWAP"], label="VWAP", color="tab:orange")
    axis.set_title("VWAP vs Close")
    axis.set_xlabel("Date")
    axis.set_ylabel("Price")
    axis.legend()
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    return figure


if __name__ == "__main__":
    print(
        "This module only defines plotting helpers. "
        "Import and use them from your Streamlit app or other scripts."
    )

