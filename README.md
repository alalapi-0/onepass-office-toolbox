# OnePass Office Toolbox

OnePass Office Toolbox 是一组面向日常办公场景的命令行小工具集合，旨在帮助完成批处理、文件整理、Excel/CSV 联动、文本清洗、报告生成等常见任务。本仓库采用 Python 构建，后续会逐步扩展各类子工具。

> 当前状态：第 1 轮初始化，仅包含项目骨架和基础 CLI，具体工具将在后续迭代中补充。

## 目录结构
```
onepass-office-toolbox/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── src/
│   └── onepass_office_toolbox/
│       ├── __init__.py
│       ├── cli.py
│       ├── fs_tools/
│       ├── list_tools/
│       ├── report_tools/
│       └── text_tools/
└── sample_data/
    ├── fs_demo/
    ├── list_demo/
    ├── report_demo/
    └── text_demo/
```

## 快速开始
1. 可选：安装预估依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 运行 CLI 查看欢迎信息
   ```bash
   PYTHONPATH=src python -m onepass_office_toolbox.cli
   ```

3. 查看版本号
   ```bash
   PYTHONPATH=src python -m onepass_office_toolbox.cli --version
   ```

后续轮次将补充各类工具的使用示例与详细说明。
