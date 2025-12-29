.
├── .agent/
│   ├── rules.md
│   └── structure.md
├── .github/
│   └── workflows/
│       └── test.yml
├── .vscode/
│   ├── extensions.json
│   └── settings.json
├── scripts/
│   └── dump_context.py
├── src/
│   ├── __init__.py         # 空ファイル
│   ├── config.py
│   ├── app/                # (Option) Web framework entry
│   │   └── __init__.py     # 空ファイル
│   ├── core/
│   │   ├── __init__.py     # 空ファイル
│   │   ├── logic.py        # [Template] Business Logic
│   │   ├── logging.py      # [Utils] Logger
│   │   └── result.py       # [Utils] Result Type
│   ├── infrastructure/
│   │   ├── __init__.py     # 空ファイル
│   │   └── adapters/
│   │       ├── __init__.py # 空ファイル
│   │       └── external.py # [Template] ACL Wrapper
│   └── interface/
│       ├── __init__.py     # 空ファイル
│       └── main.py         # Entry Point
├── tests/
│   ├── __init__.py         # 空ファイル
│   ├── conftest.py         # 空ファイル
│   └── unit/
│       ├── __init__.py     # 空ファイル
│       └── test_logic.py
├── .env
├── .env.example
├── .gitignore
├── Makefile
├── pyproject.toml
└── README.md
