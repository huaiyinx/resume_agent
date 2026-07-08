// frontend/src/components/section/SectionOrderPanel.tsx
// US-13: 简历段落排序面板
// - 拖拽排序（HTML5 Drag API，不引入新依赖）
// - 显示/隐藏开关
// - 防抖保存 500ms
// - 节点切换时重新加载

import { useState, useEffect, useCallback, useRef } from 'react';
import { getSectionOrder, updateSectionOrder } from '@/lib/api';
import type { SectionItem } from '@/types/section';

interface SectionOrderPanelProps {
  nodeId: string | null;
  /** section_order 保存后通知外部更新 selectedNode 的 content_json */
  onOrderUpdated?: (sections: SectionItem[]) => void;
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export default function SectionOrderPanel({ nodeId, onOrderUpdated }: SectionOrderPanelProps) {
  const [sections, setSections] = useState<SectionItem[]>([]);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [loading, setLoading] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const skipNextSave = useRef(false);
  const dragIndex = useRef<number | null>(null);

  // 节点切换时加载
  useEffect(() => {
    if (!nodeId) {
      setSections([]);
      return;
    }

    setLoading(true);
    getSectionOrder(nodeId)
      .then((data) => {
        setSections(data);
        skipNextSave.current = true;
      })
      .catch(() => setSections([]))
      .finally(() => setLoading(false));

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [nodeId]);

  // 防抖保存
  const triggerSave = useCallback(
    (newSections: SectionItem[]) => {
      if (!nodeId || skipNextSave.current) {
        skipNextSave.current = false;
        return;
      }

      setSaveStatus('saving');
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(async () => {
        try {
          await updateSectionOrder(nodeId, newSections);
          setSaveStatus('saved');
          onOrderUpdated?.(newSections);
          setTimeout(() => setSaveStatus('idle'), 1500);
        } catch {
          setSaveStatus('error');
        }
      }, 500);
    },
    [nodeId],
  );

  // 拖拽排序
  function handleDragStart(idx: number) {
    dragIndex.current = idx;
  }

  function handleDragOver(e: React.DragEvent, idx: number) {
    e.preventDefault();
    if (dragIndex.current === null || dragIndex.current === idx) return;
    const newSections = [...sections];
    const dragged = newSections[dragIndex.current];
    newSections.splice(dragIndex.current, 1);
    newSections.splice(idx, 0, dragged);
    dragIndex.current = idx;
    setSections(newSections);
    triggerSave(newSections);
  }

  function handleDragEnd() {
    dragIndex.current = null;
  }

  // 切换显示/隐藏
  function toggleVisible(idx: number) {
    const newSections = sections.map((s, i) =>
      i === idx ? { ...s, visible: !s.visible } : s,
    );
    setSections(newSections);
    triggerSave(newSections);
  }

  if (!nodeId) {
    return null;
  }

  const statusText = {
    idle: '',
    saving: '保存中...',
    saved: '已保存',
    error: '保存失败',
  }[saveStatus];

  return (
    <div className="border-b border-border-subtle">
      {/* 标题栏 */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-bg-tertiary transition-colors"
      >
        <div className="flex items-center gap-1.5">
          <svg
            width="14"
            height="14"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            className="text-brand-primary"
          >
            <path d="M2 4h12M2 8h12M2 12h12" />
            <circle cx="6" cy="4" r="0.5" fill="currentColor" />
            <circle cx="10" cy="8" r="0.5" fill="currentColor" />
            <circle cx="4" cy="12" r="0.5" fill="currentColor" />
          </svg>
          <span className="text-xs font-semibold text-text-primary">段落排序</span>
          {statusText && (
            <span
              className={`text-[10px] ${saveStatus === 'error' ? 'text-error' : 'text-text-muted'}`}
            >
              {statusText}
            </span>
          )}
        </div>
        <svg
          width="10"
          height="10"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className={`text-text-muted transition-transform ${collapsed ? '' : 'rotate-90'}`}
        >
          <path d="M6 4l4 4-4 4" />
        </svg>
      </button>

      {!collapsed && (
        <div className="px-3 pb-3 space-y-1">
          {loading ? (
            <div className="flex items-center justify-center py-2">
              <svg
                className="animate-spin w-3 h-3 text-text-tertiary"
                viewBox="0 0 16 16"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
              >
                <path d="M8 1.5a6.5 6.5 0 1 0 6.5 6.5" />
              </svg>
            </div>
          ) : (
            sections.map((section, idx) => (
              <div
                key={section.key}
                draggable
                onDragStart={() => handleDragStart(idx)}
                onDragOver={(e) => handleDragOver(e, idx)}
                onDragEnd={handleDragEnd}
                className={`flex items-center gap-2 px-2 py-1.5 rounded border border-border-subtle bg-bg-elevated cursor-move transition-all ${
                  dragIndex.current === idx ? 'opacity-50 border-brand-primary' : ''
                } ${!section.visible ? 'opacity-60' : ''}`}
              >
                {/* 拖拽手柄 */}
                <svg
                  width="10"
                  height="14"
                  viewBox="0 0 10 14"
                  fill="currentColor"
                  className="text-text-muted flex-shrink-0"
                >
                  <circle cx="2" cy="3" r="1" />
                  <circle cx="8" cy="3" r="1" />
                  <circle cx="2" cy="7" r="1" />
                  <circle cx="8" cy="7" r="1" />
                  <circle cx="2" cy="11" r="1" />
                  <circle cx="8" cy="11" r="1" />
                </svg>

                {/* 段落标题 */}
                <span className="text-xs text-text-primary flex-1">
                  {section.title}
                </span>

                {/* 序号 */}
                <span className="text-[10px] text-text-muted w-4 text-center">
                  {idx + 1}
                </span>

                {/* 显示/隐藏开关 */}
                <button
                  onClick={() => toggleVisible(idx)}
                  className={`relative w-7 h-3.5 rounded-full transition-colors ${
                    section.visible ? 'bg-brand-primary' : 'bg-border-default'
                  }`}
                >
                  <span
                    className={`absolute top-0.5 w-2.5 h-2.5 rounded-full bg-white transition-transform ${
                      section.visible ? 'translate-x-3.5' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
