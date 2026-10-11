"""Pure Python financial metric calculations and input validation."""

from __future__ import annotations

import math
from numbers import Real
from typing import Mapping

MAX_AMOUNT = 1_000_000_000_000_000


def _number(value: object, field: str) -> float:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"缺少财务数据：{field}")
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{field} 必须是数值")
    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{field} 必须是有限数值")
    return numeric_value


def _amount(value: object, field: str, *, allow_negative: bool = False) -> float:
    numeric_value = _number(value, field)
    lower_bound = -MAX_AMOUNT if allow_negative else 0
    if not lower_bound <= numeric_value <= MAX_AMOUNT:
        raise ValueError(f"{field} 必须在 {lower_bound} 到 {MAX_AMOUNT} 之间")
    return numeric_value


def calculate_debt_to_asset_ratio(total_liabilities: object, total_assets: object) -> float:
    """Return total liabilities divided by total assets as a decimal ratio."""
    liabilities = _amount(total_liabilities, "负债总额")
    assets = _amount(total_assets, "资产总额")
    if assets == 0:
        raise ValueError("资产总额必须大于 0")
    return liabilities / assets


def calculate_current_ratio(current_assets: object, current_liabilities: object) -> float:
    """Return current assets divided by current liabilities."""
    assets = _amount(current_assets, "流动资产")
    liabilities = _amount(current_liabilities, "流动负债")
    if liabilities == 0:
        raise ValueError("流动负债必须大于 0，无法计算流动比率")
    return assets / liabilities


def calculate_net_profit_margin(net_profit: object, revenue: object) -> float:
    """Return net profit divided by revenue as a decimal ratio."""
    profit = _amount(net_profit, "净利润", allow_negative=True)
    total_revenue = _amount(revenue, "营业收入")
    if total_revenue == 0:
        raise ValueError("营业收入必须大于 0，无法计算净利润率")
    return profit / total_revenue


METRIC_INPUTS: dict[str, tuple[str, ...]] = {
    "debt_to_asset_ratio": ("total_liabilities", "total_assets"),
    "current_ratio": ("current_assets", "current_liabilities"),
    "net_profit_margin": ("net_profit", "revenue"),
}

METRIC_LABELS = {
    "debt_to_asset_ratio": "资产负债率",
    "current_ratio": "流动比率",
    "net_profit_margin": "净利润率",
}


def calculate_financial_metrics(data: Mapping[str, object]) -> dict[str, object]:
    """Calculate all available metrics and report missing/invalid inputs per metric."""
    calculators = {
        "debt_to_asset_ratio": calculate_debt_to_asset_ratio,
        "current_ratio": calculate_current_ratio,
        "net_profit_margin": calculate_net_profit_margin,
    }
    results: dict[str, object] = {"values": {}, "errors": {}}
    for metric, fields in METRIC_INPUTS.items():
        try:
            values = [data.get(field) for field in fields]
            results["values"][metric] = calculators[metric](*values)
        except (TypeError, ValueError) as error:
            results["values"][metric] = None
            results["errors"][metric] = str(error)
    return results