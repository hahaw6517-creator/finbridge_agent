"""Sample and uploaded financial data helpers."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd

FINANCIAL_COLUMNS = (
    "total_assets",
    "total_liabilities",
    "current_assets",
    "current_liabilities",
    "revenue",
    "net_profit",
)


def load_uploaded_financial_data(filename: str, content: bytes) -> pd.DataFrame:
    """Load a CSV or Excel upload and normalize absent financial columns."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(BytesIO(content))
    elif suffix in {".xlsx", ".xlsm"}:
        frame = pd.read_excel(BytesIO(content))
    else:
        raise ValueError("仅支持 CSV 或 XLSX 格式")

    if "company_name" not in frame.columns:
        raise ValueError("文件必须包含 company_name 列作为企业名称")
    for column in FINANCIAL_COLUMNS:
        if column not in frame.columns:
            frame[column] = None
    if frame.empty:
        raise ValueError("文件中没有企业记录")
    return frame