from io import BytesIO

import pandas as pd
import pytest

from finbridge.data import FINANCIAL_COLUMNS, load_uploaded_financial_data


def test_load_csv_and_fill_missing_financial_columns():
    content = b"company_name,revenue\nSimulated Co,1000\n"

    frame = load_uploaded_financial_data("companies.csv", content)

    assert frame.loc[0, "company_name"] == "Simulated Co"
    assert frame.loc[0, "revenue"] == 1000
    assert all(column in frame.columns for column in FINANCIAL_COLUMNS)
    assert pd.isna(frame.loc[0, "total_assets"])


def test_load_xlsx():
    buffer = BytesIO()
    pd.DataFrame({"company_name": ["Simulated Co"], "revenue": [1000]}).to_excel(
        buffer, index=False
    )

    frame = load_uploaded_financial_data("companies.xlsx", buffer.getvalue())

    assert frame.loc[0, "company_name"] == "Simulated Co"
    assert frame.loc[0, "revenue"] == 1000


@pytest.mark.parametrize(
    "filename,content,error",
    [
        ("companies.json", b"{}", "仅支持"),
        ("companies.csv", b"revenue\n1000\n", "company_name"),
        ("companies.csv", b"company_name\n", "没有企业记录"),
    ],
)
def test_reject_invalid_uploads(filename, content, error):
    with pytest.raises(ValueError, match=error):
        load_uploaded_financial_data(filename, content)