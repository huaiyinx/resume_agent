# US-13: 简历段落可排序 - 任务清单

## 后端

- [ ] 创建 `backend/src/resume_agent/api/section_order.py`
  - [ ] 定义默认 8 段顺序常量 `DEFAULT_SECTION_ORDER`
  - [ ] `GET /tree/node/{node_id}/section-order` 端点
  - [ ] `PUT /tree/node/{node_id}/section-order` 端点
- [ ] 修改 `api/tree.py` 的 `create_node`
  - [ ] 创建子节点时从父节点继承 `section_order`
- [ ] 注册路由到 `api/router.py`
- [ ] 编写测试 `backend/tests/test_section_order_api.py`
  - [ ] test_get_default_section_order
  - [ ] test_update_section_order
  - [ ] test_inherit_on_create
  - [ ] test_reorder
  - [ ] test_toggle_visible
  - [ ] test_get_nonexistent_node

## 前端

- [ ] 创建 `frontend/src/types/section.ts`
  - [ ] SectionItem 类型（key, title, visible）
- [ ] 创建 `frontend/src/components/section/SectionOrderPanel.tsx`
  - [ ] 拖拽排序（HTML5 Drag API）
  - [ ] 显示/隐藏开关
  - [ ] 防抖保存 500ms
  - [ ] 节点切换时重新加载
- [ ] 添加 `getSectionOrder` / `updateSectionOrder` 到 `api.ts`
- [ ] 集成到 `CenterPanel.tsx`（编辑器 Tab 工具栏下方）
- [ ] 修改 `ResumePreview.tsx` 按 section_order 渲染

## 验证

- [ ] 后端测试全部通过
- [ ] 前端 typecheck 通过
- [ ] HJ 人工验收
