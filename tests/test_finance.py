import pytest

from finbridge.finance import (
    calculate_current_ratio,
    calculate_debt_to_asset_ratio,
    calculate_financial_metrics,
    calculate_net_profit_margin,
)


def test_debt_to_asset_ratio():
    assert calculate_debt_to_asset_ratio(40, 100) == pytest.approx(0.4)


def test_current_ratio():
    assert calculate_current_ratio(150, 100) == pytest.approx(1.5)


def test_net_profit_margin_supports_loss():
    assert calculate_net_profit_margin(-10, 100) == pytest.approx(-0.1)


@pytest.mark.parametrize(
    "calculation,arguments",
    [
        (calculate_debt_to_asset_ratio, (10, 0)),
        (calculate_current_ratio, (10, 0)),
        (calculate_net_profit_margin, (10, 0)),
        (calculate_current_ratio, (-1, 2)),
        (calculate_net_profit_margin, (True, 2)),
    ],
)
def test_financial_calculations_reject_invalid_values(calculation, arguments):
    with pytest.raises(ValueError):
        calculation(*arguments)


def test_metrics_report_missing_data_without_failing_all_metrics():
    result = calculate_financial_metrics(
        {"total_liabilities": 20, "total_assets": 100, "current_assets": None}
    )

    assert result["values"]["debt_to_asset_ratio"] == pytest.approx(0.2)
    assert result["values"]["current_ratio"] is None
    assert "缺少财务数据" in result["errors"]["current_ratio"]
    assert result["values"]["net_profit_margin"] is None