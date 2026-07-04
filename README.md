# Resume-Agent

把简历当代码仓库来管：Git 式版本树 + RAG 知识库 + AI 动态生成。

技术求职者手里从来不是「一份简历」，而是十几份针对不同公司、不同方向裁剪过的版本。Resume-Agent 用 Git 的方式管理这整片「简历森林」——Master 主干分化方向分支，分支长出公司专属节点，改一次主干所有子分支自动继承。

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
git clone https://github.com/DeLightor/resume_agent.git
cd resume_agent
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY
docker compose up
```

访问 http://localhost:5173

### 方式二：源码开发

```bash
git clone https://github.com/DeLightor/resume_agent.git
cd resume_agent
make install    # 安装前后端依赖（需要 uv + pnpm）
make dev        # 启动开发服务器
```

- 前端：http://localhost:5173
- API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 前置要求

| 工具 | 版本 | 安装方式 |
|------|------|----------|
| Node.js | ≥ 20 | [nodejs.org](https://nodejs.org/) |
| pnpm | ≥ 9 | `npm install -g pnpm` |
| Python | ≥ 3.12 | [python.org](https://python.org/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker | ≥ 24（可选） | [docker.com](https://docker.com/) |

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + Vite + TypeScript + Tailwind CSS v4 + React Flow v12 |
| 后端 | Python 3.12 + FastAPI + LangGraph |
| 数据库 | SQLite（元数据）+ Chroma（向量库，嵌入式） |
| 部署 | Docker Compose 单容器 |

## 项目结构

```
resume-agent/
├── backend/              # Python 后端
│   ├── src/resume_agent/
│   │   ├── api/          # FastAPI 路由
│   │   ├── db/           # SQLite + 建表脚本
│   │   ├── rag/          # Chroma 向量库
│   │   ├── parsers/      # 简历解析（骨架）
│   │   ├── agents/       # LangGraph 工作流（骨架）
│   │   ├── config.py     # 环境变量配置
│   │   └── main.py       # FastAPI 入口
│   └── tests/
├── frontend/             # React 前端
│   ├── src/
│   │   ├── components/   # 组件（layout / tree / common）
│   │   ├── routes/       # 路由页面
│   │   ├── styles/       # 设计令牌 + Tailwind
│   │   ├── data/         # mock 数据
│   │   └── types/        # TypeScript 类型
│   └── vite.config.ts
├── openspec/             # 规格文档
├── docs/                 # 文档
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── .env.example
```

## 开发命令

```bash
make install    # 安装依赖
make dev        # 启动开发服务器（前后端热更新）
make build      # 构建前端
make test       # 运行测试
make lint       # 代码检查
make docker-build  # Docker 构建
make docker-up     # Docker 启动
```

## 数据存储

所有数据默认存储在 `~/.resume-agent/`：

```
~/.resume-agent/
├── data.db          # SQLite 元数据（版本树、上传记录）
├── chroma/          # Chroma 向量索引
└── files/           # 上传的原始文件
```

## License

MIT
