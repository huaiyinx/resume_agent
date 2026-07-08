# US-14: 一键生成整份简历 - 任务清单

## 后端

- [ ] 修改 `api/generate.py`
  - [ ] 新增 `_WRITER_PROMPT_SUMMARY` 系统提示
  - [ ] 新增 `POST /generate/full` 端点（asyncio.gather 并行生成）
  - [ ] 新增 `POST /generate/section` 端点（单段重新生成）
  - [ ] 从节点读取 personal_info 带入结果
  - [ ] 生成结果写入节点 content_json
- [ ] 编写测试 `tests/test_generate_full_api.py`
  - [ ] test_full_generate
  - [ ] test_section_regenerate
  - [ ] test_empty_knowledge_base
  - [ ] test_personal_info_carried_over

## 前端

- [ ] 添加 `generateFull` / `regenerateSection` 到 `api.ts`
- [ ] 中栏编辑器 Tab 工具栏新增"一键生成"按钮
- [ ] 预览区每个段落新增"重新生成"按钮
- [ ] 生成中 loading 状态
- [ ] 生成完更新预览区

## 验证

- [ ] 后端测试通过
- [ ] 前端 typecheck 通过
- [ ] HJ 人工验收
