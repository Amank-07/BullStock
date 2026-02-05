from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st

from nse_analysis import (
    PriceInsights,
    TrendInsights,
    VolumeInsights,
    compute_price_insights,
    compute_trend_insights,
    compute_volatility_metrics,
    compute_volume_insights,
    generate_summary_text,
)
from nse_loader import get_date_bounds, load_nse_csv
from nse_viz import (
    plot_close_price_over_time,
    plot_volume_over_time,
    plot_vwap_vs_close,
)
from report_generator import create_pdf_report


st.set_page_config(
    page_title="NSE Stock Analysis",
    layout="wide",
)


def main() -> None:
    st.title("NSE Stock Analysis Tool")
    st.markdown(
        "Upload a CSV downloaded from the **NSE website** with columns:\n\n"
        "`DATE, SERIES, OPEN, HIGH, LOW, PREV. CLOSE, LTP, CLOSE, VWAP, "
        "52W H, 52W L, VOLUME, VALUE, NO. OF TRADES`.\n\n"
        "The app will clean the data, compute insights, and generate charts."
    )

    uploaded_file = st.file_uploader(
        "Upload NSE CSV file",
        type=["csv"],
        help="Download the daily price history CSV from NSE and upload it here.",
    )

    if uploaded_file is None:
        st.info("Upload an NSE CSV file to begin.")
        return

    try:
        df = load_nse_csv(uploaded_file)
    except Exception as e:
        msg = str(e)
        if "Missing expected columns in CSV" in msg:
            st.error(
                "Invalid data format. Please upload a CSV downloaded from NSE "
                "with all required columns (DATE, SERIES, OPEN, HIGH, LOW, PREV. CLOSE, "
                "LTP, CLOSE, VWAP, 52W H, 52W L, VOLUME, VALUE, NO. OF TRADES)."
            )
        else:
            st.error(f"Error loading CSV: {msg}")
        return

    # Save a copy locally only after successful validation/loading
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    local_path = data_dir / uploaded_file.name
    with open(local_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if df.empty:
        st.error("The CSV appears to be empty after cleaning.")
        return

    min_date, max_date = get_date_bounds(df)

    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input(
        "Start Date",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )
    end_date = st.sidebar.date_input(
        "End Date",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

    if start_date > end_date:
        st.sidebar.error("Start date must be before or equal to end date.")
        return

    # Filter by chosen dates
    mask = (df["DATE"].dt.date >= start_date) & (df["DATE"].dt.date <= end_date)
    df = df.loc[mask].copy()

    if df.shape[0] < 5:
        st.error("Not enough rows in the selected date range for analysis (need at least 5).")
        return

    # Compute insights
    price_insights: PriceInsights = compute_price_insights(df)
    volume_insights: VolumeInsights = compute_volume_insights(df)
    trend_insights: TrendInsights = compute_trend_insights(df, window=min(20, len(df)))
    vol_metrics = compute_volatility_metrics(df)

    # Top-level metrics
    st.subheader("Key Price & Volume Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Latest LTP",
            f"{price_insights.latest_ltp:.2f}",
            f"{price_insights.change:.2f}",
        )
    with col2:
        st.metric(
            "Latest Close",
            f"{price_insights.latest_close:.2f}",
            f"{price_insights.pct_change:.2f}%",
        )
    with col3:
        st.metric("52W High", f"{price_insights.high_52w:.2f}")
        st.metric("52W Low", f"{price_insights.low_52w:.2f}")
    with col4:
        st.metric("Avg Volume", f"{volume_insights.avg_volume:,.0f}")
        st.metric("Max Volume", f"{volume_insights.max_volume:,.0f}")

    # Charts
    st.subheader("Price & Volume Charts")
    col_price, col_vol = st.columns(2)
    with col_price:
        st.pyplot(plot_close_price_over_time(df))
    with col_vol:
        st.pyplot(plot_volume_over_time(df))

    st.subheader("VWAP vs Close")
    st.pyplot(plot_vwap_vs_close(df))

    # Trend & volatility
    st.subheader("Trend & Volatility")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write(
            f"Trend over last {trend_insights.window} days: "
            f"**{trend_insights.trend_label.upper()}**"
        )
        st.write(f"Average daily return: {trend_insights.mean_return * 100:.2f}%")
    with col_t2:
        st.write(f"Intraday high-low range (avg): {vol_metrics['avg_hl_range_pct']:.2f}%")
        st.write(
            f"Close-to-close volatility (std of returns): "
            f"{vol_metrics['std_close_return_pct']:.2f}%"
        )

    # Plain-English summary
    st.subheader("Summary Analysis")
    summary_text = generate_summary_text(
        price_insights,
        volume_insights,
        trend_insights,
        vol_metrics,
    )
    st.markdown(summary_text)

    # PDF download
    instrument_name = Path(local_path).stem
    pdf_bytes = create_pdf_report(
        instrument_name=instrument_name,
        price=price_insights,
        volume=volume_insights,
        trend=trend_insights,
        volatility_metrics=vol_metrics,
        summary_text=summary_text,
    )

    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=f"{instrument_name}_analysis_report.pdf",
        mime="application/pdf",
    )

    st.caption(
        "This analysis is for informational and educational purposes only and "
        "does not constitute financial advice."
    )


if __name__ == "__main__":
    main()

