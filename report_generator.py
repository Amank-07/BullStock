from __future__ import annotations

"""
Helpers to generate a simple PDF report for the NSE stock analysis.

We keep the layout intentionally minimal:
- A title with the instrument / file name
- Key numeric metrics (latest price, change, volume, trend, volatility)
- The same plain‑English summary text that appears in the app
"""

from io import BytesIO
from typing import Dict

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from nse_analysis import PriceInsights, TrendInsights, VolumeInsights


def _draw_wrapped_text(
    pdf: canvas.Canvas,
    text: str,
    x: int,
    y_start: int,
    max_width: int,
    line_height: int = 10,
) -> int:
    """
    Draw multi-line text with simple word‑wrapping.

    Returns the y‑coordinate of the next free line (so callers can
    continue writing below).
    """
    words = text.split()
    line = ""
    y = y_start

    for word in words:
        candidate = f"{line} {word}".strip()
        if pdf.stringWidth(candidate, "Helvetica", 10) <= max_width:
            line = candidate
        else:
            pdf.drawString(x, y, line)
            y -= line_height
            line = word

    if line:
        pdf.drawString(x, y, line)
        y -= line_height

    return y


def create_pdf_report(
    instrument_name: str,
    price: PriceInsights,
    volume: VolumeInsights,
    trend: TrendInsights,
    volatility_metrics: Dict[str, float],
    summary_text: str,
) -> bytes:
    """
    Build a one‑page PDF report and return it as raw bytes.
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin_x = 50
    y = height - 50

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin_x, y, f"NSE Stock Analysis Report - {instrument_name}")
    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        margin_x,
        y,
        f"Latest date: {price.latest_date.date()}",
    )
    y -= 20

    # Key metrics block
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(margin_x, y, "Key Metrics")
    y -= 18

    pdf.setFont("Helvetica", 10)
    key_lines = [
        f"Latest LTP: {price.latest_ltp:.2f}",
        f"Latest Close: {price.latest_close:.2f} (change {price.change:.2f}, {price.pct_change:.2f}%)",
        f"Previous Close: {price.prev_close:.2f}",
        f"52W High / Low: {price.high_52w:.2f} / {price.low_52w:.2f}",
        f"Average Volume: {volume.avg_volume:,.0f}",
        f"Max Volume: {volume.max_volume:,.0f} on {volume.max_volume_date.date()}",
        f"Trend (last {trend.window} sessions): {trend.trend_label} "
        f"with avg daily return {trend.mean_return * 100:.2f}%",
        f"Intraday high‑low range (avg): {volatility_metrics['avg_hl_range_pct']:.2f}%",
        f"Close‑to‑close volatility (std): {volatility_metrics['std_close_return_pct']:.2f}%",
    ]

    for line in key_lines:
        pdf.drawString(margin_x, y, line)
        y -= 14

    y -= 10

    # Summary section
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin_x, y, "Summary")
    y -= 18
    pdf.setFont("Helvetica", 10)

    y = _draw_wrapped_text(
        pdf,
        summary_text,
        x=margin_x,
        y_start=y,
        max_width=int(width - 2 * margin_x),
        line_height=14,
    )

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    print("PDF report generator helpers. Import and use create_pdf_report from the Streamlit app.")

