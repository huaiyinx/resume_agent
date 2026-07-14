# LifeOS Resume-Agent 集成

本 Fork 作为 LifeOS 职业系统的独立主引擎运行。用户仍从 Love 输入、在 LifeOS 查看；Resume-Agent 负责简历版本树、JD、Gap、导师建议和 PDF。

## 部署边界

- 生产容器使用 host 网络，但应用只监听 `127.0.0.1:5174`，不直接暴露公网，并可直接访问宿主机 LiteLLM `127.0.0.1:4000`。
- 业务 API 在配置 `INTERNAL_API_TOKEN` 后要求 `X-Resume-Agent-Token`。
- `/api/health` 保持无凭据本机探活。
- 浏览器未来通过 `https://chat.19991023.xyz/life/career/` 访问，由现有认证和反向代理注入内部令牌。
- 数据持久化到 `/mnt/data/life-os/resume-agent`；导入源只读挂载为 `/imports`。

香港 VPS 构建时使用固定本地镜像名 `lifeos-resume-agent:local`。若需要美国出站加速，先用 `docker build --network host` 构建，再运行 `docker compose up -d --no-build`。

## Career-Ops 冷启动

```bash
docker exec lifeos-resume-agent uv run python /app/scripts/import_career_ops.py \
  --source-dir /imports/Career-Ops \
  --resume-file /imports/Career-Ops/cv.md
```

导入器以文件名幂等：知识文档已存在则跳过；`cv.md` 已上传则不重复解析。个人资料不会写入 Git 或日志。

## 后续链路

1. Love 职场截图通过 loopback 发送到 Resume-Agent。
2. Resume-Agent 返回结构化 JD、Gap 和导师建议。
3. LifeOS 职业页显示摘要，并提供全屏工作台入口。
