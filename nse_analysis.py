from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


@dataclass
class PriceInsights:
    latest_date: pd.Timestamp
    latest_ltp: float
    latest_close: float
    prev_close: float
    change: float
    pct_change: float
    high_52w: float
    low_52w: float
    distance_from_high_pct: float
    distance_from_low_pct: float


@dataclass
class VolumeInsights:
    avg_volume: float
    max_volume: float
    max_volume_date: pd.Timestamp


@dataclass
class TrendInsights:
    window: int
    mean_return: float
    volatility: float
    trend_label: str


def compute_price_insights(df: pd.DataFrame) -> PriceInsights:
    latest = df.iloc[-1]
    latest_close = float(latest["CLOSE"])
    latest_ltp = float(latest.get("LTP", latest_close))
    prev_close = float(latest["PREV. CLOSE"])

    change = latest_close - prev_close
    pct_change = (change / prev_close) * 100 if prev_close != 0 else 0.0

    high_52w = float(latest.get("52W H", np.nan))
    low_52w = float(latest.get("52W L", np.nan))

    distance_from_high_pct = (
        ((high_52w - latest_close) / high_52w) * 100 if high_52w and not np.isnan(high_52w) else np.nan
    )
    distance_from_low_pct = (
        ((latest_close - low_52w) / low_52w) * 100 if low_52w and not np.isnan(low_52w) else np.nan
    )

    return PriceInsights(
        latest_date=latest["DATE"],
        latest_ltp=latest_ltp,
        latest_close=latest_close,
        prev_close=prev_close,
        change=change,
        pct_change=pct_change,
        high_52w=high_52w,
        low_52w=low_52w,
        distance_from_high_pct=distance_from_high_pct,
        distance_from_low_pct=distance_from_low_pct,
    )


def compute_volume_insights(df: pd.DataFrame) -> VolumeInsights:
    avg_volume = float(df["VOLUME"].mean())
    max_idx = df["VOLUME"].idxmax()
    max_row = df.loc[max_idx]
    return VolumeInsights(
        avg_volume=avg_volume,
        max_volume=float(max_row["VOLUME"]),
        max_volume_date=max_row["DATE"],
    )


def compute_trend_insights(df: pd.DataFrame, window: int = 20) -> TrendInsights:
    df_sorted = df.sort_values("DATE").copy()
    df_sorted["return"] = df_sorted["CLOSE"].pct_change()

    recent = df_sorted.tail(window)
    mean_return = float(recent["return"].mean())
    volatility = float(recent["return"].std())

    last_close = float(recent["CLOSE"].iloc[-1])
    ma = float(recent["CLOSE"].mean())

    # Simple rule-based trend classification
    if mean_return > 0 and last_close > ma * 1.01:
        trend = "bullish"
    elif mean_return < 0 and last_close < ma * 0.99:
        trend = "bearish"
    else:
        trend = "sideways"

    return TrendInsights(
        window=window,
        mean_return=mean_return,
        volatility=volatility,
        trend_label=trend,
    )


def compute_volatility_metrics(df: pd.DataFrame) -> Dict[str, float]:
    df_sorted = df.sort_values("DATE").copy()
    df_sorted["hl_range_pct"] = (df_sorted["HIGH"] - df_sorted["LOW"]) / df_sorted["CLOSE"].replace(0, np.nan)
    df_sorted["close_return"] = df_sorted["CLOSE"].pct_change()

    return {
        "avg_hl_range_pct": float(df_sorted["hl_range_pct"].mean(skipna=True) * 100),
        "std_close_return_pct": float(df_sorted["close_return"].std(skipna=True) * 100),
    }


def generate_summary_text(
    price: PriceInsights,
    volume: VolumeInsights,
    trend: TrendInsights,
    vol_metrics: Dict[str, float],
) -> str:
    """
    Generate a plain-English summary using computed insights.
    """
    lines = []

    # Price positioning vs 52-week range
    if not (np.isnan(price.high_52w) or np.isnan(price.low_52w)):
        if price.distance_from_high_pct is not None and price.distance_from_high_pct < 5:
            lines.append(
                f"The stock is trading very close to its 52-week high "
                f"({price.high_52w:.2f}), suggesting strong recent performance."
            )
        elif price.distance_from_low_pct is not None and price.distance_from_low_pct < 5:
            lines.append(
                f"The stock is trading close to its 52-week low ({price.low_52w:.2f}), "
                "indicating recent weakness."
            )
        else:
            lines.append(
                "The stock is trading comfortably within its 52-week range, "
                "neither near extreme highs nor lows."
            )

    # Daily move
    direction_word = "up" if price.change >= 0 else "down"
    lines.append(
        f"On the latest trading day ({price.latest_date.date()}), the stock closed at "
        f"{price.latest_close:.2f}, {direction_word} {abs(price.change):.2f} "
        f"({price.pct_change:.2f}%) from the previous close of {price.prev_close:.2f}."
    )

    # Volume
    lines.append(
        f"Average daily volume over the dataset is about {volume.avg_volume:,.0f} shares, "
        f"with the highest volume of {volume.max_volume:,.0f} on {volume.max_volume_date.date()}."
    )

    # Trend
    lines.append(
        f"Over the last {trend.window} sessions, the trend appears **{trend.trend_label}**, "
        f"with an average daily return of {trend.mean_return * 100:.2f}%."
    )

    # Volatility
    lines.append(
        f"Typical intraday high-low range has been around {vol_metrics['avg_hl_range_pct']:.2f}% "
        f"of price, and daily close-to-close volatility about {vol_metrics['std_close_return_pct']:.2f}%."
    )

    return "\n\n".join(lines)


if __name__ == "__main__":
    # Minimal manual test hook
    import pathlib

    from nse_loader import load_nse_csv

    path = pathlib.Path("data") / "sample_nse.csv"
    if path.exists():
        with open(path, "rb") as f:
            df_sample = load_nse_csv(f)
        p = compute_price_insights(df_sample)
        v = compute_volume_insights(df_sample)
        t = compute_trend_insights(df_sample)
        vol = compute_volatility_metrics(df_sample)
        print(generate_summary_text(p, v, t, vol))
    else:
        print("Place sample_nse.csv in data/ to test analysis functions.")

