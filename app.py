"""Streamlit interface for the FinBridge AI phase-one prototype."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from finbridge.agent import AgentConfigurationError, AgentRequestError, FinancialAgent
from finbridge.config import load_settings
from finbridge.data import FINANCIAL_COLUMNS, load_uploaded_financial_data
from finbridge.finance import METRIC_LABELS, calculate_financial_metrics

st.set_page_config(page_title="融智 Agent | FinBridge AI", page_icon="FB", layout="wide")
st.markdown(
    """
    <style>
    :root { --ink: #173332; --teal: #087f73; --mint: #dff3ed; --amber: #d78637; }
    .stApp { background: radial-gradient(ellipse at 85% 0%, #e8f5ef 0, transparent 35%), #f7f8f4; color: var(--ink); }
    [data-testid="stSidebar"] { background: #173332; }
    [data-testid="stSidebar"] * { color: #f5f6ef !important; }
    .brand-kicker { color: #087f73; font-size: .78rem; font-weight: 700; letter-spacing: .08em; }
    .brand-title { color: #173332; font-size: 2rem; line-height: 1.15; margin: .15rem 0 .4rem; }
    .brand-subtitle { color: #617370; margin: 0 0 1.4rem; }
    [data-testid="stMetric"] { background: white; border: 1px solid #dce8e2; border-radius: 8px; padding: 12px 14px; }
    [data-testid="stChatMessage"] { border-radius: 8px; }
    div.stButton > button[kind="primary"] { background: #087f73; border-color: #087f73; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="brand-kicker">FINBRIDGE AI · 融资诊断原型</div>', unsafe_allow_html=True)
st.markdown('<h1 class="brand-title">融智 Agent</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="brand-subtitle">基于模拟或用户上传的财务数据，计算关键指标并开展审慎分析。</p>',
    unsafe_allow_html=True,
)

settings = load_settings()
sample_path = PROJECT_ROOT / "data" / "sample_financials.csv"
sample_data = pd.read_csv(sample_path)

with st.sidebar:
    st.subheader("企业信息")
    company_name = st.text_input("企业名称", value=str(sample_data.iloc[0]["company_name"]))
    industry_options = sorted(sample_data["industry"].dropna().unique().tolist())
    industry = st.selectbox("所属行业", industry_options)
    region = st.text_input("所在地区", value=str(sample_data.iloc[0]["region"]))
    years_in_operation = st.number_input("成立年限", min_value=0, max_value=200, value=8, step=1)
    st.divider()
    st.caption("当前数据为模拟数据。上传文件后将仅在本次会话中用于分析。")
    uploaded_file = st.file_uploader("上传财务数据", type=["csv", "xlsx", "xlsm"])

financial_frame = sample_data
if uploaded_file is not None:
    try:
        financial_frame = load_uploaded_financial_data(uploaded_file.name, uploaded_file.getvalue())
    except (ValueError, pd.errors.ParserError, ImportError) as error:
        st.error(f"无法读取文件：{error}")
        financial_frame = sample_data

company_labels = [
    f"{index + 1}. {row.get('company_name', '未命名企业')}"
    for index, (_, row) in enumerate(financial_frame.iterrows())
]
selected_index = st.selectbox(
    "财务记录（模拟或上传）",
    range(len(company_labels)),
    format_func=lambda index: company_labels[index],
    label_visibility="collapsed",
)
selected_row = financial_frame.iloc[selected_index]
financial_data = {column: selected_row.get(column) for column in FINANCIAL_COLUMNS}
metrics = calculate_financial_metrics(financial_data)
metric_values = metrics["values"]
metric_errors = metrics["errors"]

left_column, right_column = st.columns([1.02, 1.18], gap="large")
with left_column:
    st.subheader("财务健康概览")
    st.caption(f"分析对象：{selected_row.get('company_name', company_name)} · 金额单位：元")
    metric_columns = st.columns(3)
    display_formats = {
        "debt_to_asset_ratio": lambda value: f"{value:.1%}",
        "current_ratio": lambda value: f"{value:.2f} 倍",
        "net_profit_margin": lambda value: f"{value:.1%}",
    }
    for column, metric in zip(metric_columns, METRIC_LABELS):
        value = metric_values[metric]
        column.metric(METRIC_LABELS[metric], display_formats[metric](value) if value is not None else "缺少数据")
        if value is None:
            column.caption(metric_errors[metric])

    if any(value is None for value in metric_values.values()):
        missing_labels = [METRIC_LABELS[key] for key, value in metric_values.items() if value is None]
        st.warning("部分指标无法计算，请补充对应财务字段：" + "、".join(missing_labels))

    available_metrics = {key: value for key, value in metric_values.items() if value is not None}
    if available_metrics:
        chart_labels = [METRIC_LABELS[key] for key in available_metrics]
        chart_values = [
            metric_values[key] * 100 if key != "current_ratio" else metric_values[key]
            for key in available_metrics
        ]
        chart = go.Figure(
            go.Bar(
                x=chart_values,
                y=chart_labels,
                orientation="h",
                marker_color=["#087f73", "#d78637", "#3f7e9b"],
                text=[f"{value:.2f}" if key == "current_ratio" else f"{value:.1%}"
                      for key, value in available_metrics.items()],
                textposition="outside",
            )
        )
        chart.update_layout(
            title="核心指标",
            height=250,
            margin=dict(l=4, r=36, t=42, b=12),
            xaxis_title="比率（流动比率为倍数，其余为百分比）",
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(chart, use_container_width=True)

    with st.expander("查看当前财务原始数据"):
        st.dataframe(
            pd.DataFrame(
                [{"字段": key, "数值（元）": financial_data.get(key)} for key in FINANCIAL_COLUMNS]
            ),
            hide_index=True,
            use_container_width=True,
        )

with right_column:
    st.subheader("AI 融资诊断")
    if not settings.api_configured:
        st.info("财务指标可正常使用。配置 `.env` 中的 API Key、BASE_URL 和 MODEL 后即可启用 DeepSeek 对话。")
    else:
        st.caption(f"模型：{settings.model} · 财务指标由 Python 工具计算")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("询问企业财务状况或融资准备建议", disabled=not settings.api_configured)
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("正在分析并核验财务指标…"):
                try:
                    agent = FinancialAgent(settings)
                    company_context = {
                        "企业名称": company_name,
                        "行业": industry,
                        "地区": region,
                        "成立年限": years_in_operation,
                        **financial_data,
                    }
                    answer = agent.chat(st.session_state.chat_history, company_context)
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except (AgentConfigurationError, AgentRequestError) as error:
                    st.error(str(error))