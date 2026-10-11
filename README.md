# 融智 Agent（FinBridge AI）

面向中小企业的融资诊断与融资方式匹配原型。第一阶段使用模拟或用户上传的财务数据；所有财务指标由 Python 计算，DeepSeek 通过 OpenAI Python SDK 的 Function Calling 请求计算工具，不生成银行产品、利率或审批结论。

## 项目结构

```text
.
├── app.py                         # Streamlit 中文网页
├── data/sample_financials.csv     # 模拟企业数据
├── src/finbridge/
│   ├── agent.py                   # DeepSeek 对话、工具校验与调用闭环
│   ├── config.py                  # 从 .env 读取配置
│   ├── data.py                    # CSV/Excel 读取
│   └── finance.py                 # 纯 Python 财务指标计算
├── tests/                         # 财务计算、参数校验、工具闭环测试
├── .env.example                   # 环境变量模板
└── requirements.txt
```

## 安装与运行

需要 Python 3.11 或更高版本。Windows PowerShell 示例：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

在 `.env` 中填写 `DEEPSEEK_API_KEY`、`BASE_URL` 和 `MODEL`。当前已有配置也支持 `DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`。不要提交 `.env`。

```powershell
streamlit run app.py
```

未配置 API 时，模拟数据、上传和本地指标计算仍可使用；聊天区会提示配置 API，不会模拟 AI 回复。上传 CSV 或 XLSX 时需要 `company_name` 列；财务列名为 `total_assets`、`total_liabilities`、`current_assets`、`current_liabilities`、`revenue`、`net_profit`。金额单位为元，缺少的列会显示为不可计算。

## 测试

```powershell
pytest -q
```

工具调用最多每轮 3 次；指标参数由 Python 进行类型、有限数值和范围校验。测试使用模拟 SDK 响应，不会请求真实 API。

如需手动验证当前 DeepSeek 模型确实会发起 Function Calling（会产生一次真实 API 请求），可在 PowerShell 中执行：

```powershell
$env:FINBRIDGE_LIVE_API_TEST = "1"
pytest -q tests/test_live_agent.py
Remove-Item Env:FINBRIDGE_LIVE_API_TEST
```

## 后续阶段

第二阶段可在确认指标口径后，增加可配置的诊断规则和融资准备材料清单；第三阶段再评估真实企业数据接入、权限与数据保护方案，以及产品信息来源核验。任何融资产品、利率或审批判断都应以可验证的正式数据为依据。