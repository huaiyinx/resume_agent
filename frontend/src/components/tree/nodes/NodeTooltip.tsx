// frontend/src/components/tree/nodes/NodeTooltip.tsx
// US-25: 节点 hover tooltip — 悬停 500ms 后显示节点关键信息

import { useCallback, useRef, useState } from 'react';

/** Tooltip 显示的数据 */
export interface TooltipData {
  /** 节点名称 */
  label: string;
  /** 节点类型显示名 */
  typeLabel: string;
  /** 简历完整度评分（0-100，null 表示无数据） */
  completeness?: number | null;
  /** 上游变更数量（0 表示无） */
  upstreamCount?: number;
  /** 创建时间 */
  createdAt?: string;
  /** 最后更新时间 */
  updatedAt?: string;
}

/** 格式化时间戳为可读字符串 */
function formatTime(ts?: string): string {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    return d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return ts;
  }
}

/** 节点 hover tooltip 组件 */
export function useNodeTooltip() {
  const [tooltip, setTooltip] = useState<{
    data: TooltipData;
    x: number;
    y: number;
  } | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleMouseEnter = useCallback(
    (e: React.MouseEvent, data: TooltipData) => {
      // 在 setTimeout 之前捕获 DOM 引用，因为 React 合成事件的
      // currentTarget 在事件处理器返回后会被置为 null
      const target = e.currentTarget as HTMLElement;
      // 500ms 延迟后显示
      timerRef.current = setTimeout(() => {
        const rect = target.getBoundingClientRect();
        const tooltipWidth = 240;
        const tooltipHeight = 160;

        // 避让画布边缘
        let x = rect.right + 8;
        let y = rect.top;

        // 右侧空间不够 → 显示在左侧
        if (x + tooltipWidth > window.innerWidth - 20) {
          x = rect.left - tooltipWidth - 8;
        }
        // 如果左侧也不够 → 居中显示在下方
        if (x < 20) {
          x = rect.left + (rect.width - tooltipWidth) / 2;
          y = rect.bottom + 8;
        }
        // 底部空间不够 → 上移
        if (y + tooltipHeight > window.innerHeight - 20) {
          y = Math.max(20, window.innerHeight - tooltipHeight - 20);
        }

        setTooltip({ data, x, y });
      }, 500);
    },
    [],
  );

  const handleMouseLeave = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    setTooltip(null);
  }, []);

  return { tooltip, handleMouseEnter, handleMouseLeave };
}

/** Tooltip 渲染层 — 固定定位在画布上 */
export function TooltipLayer({
  tooltip,
}: {
  tooltip: { data: TooltipData; x: number; y: number } | null;
}) {
  if (!tooltip) return null;

  const { data, x, y } = tooltip;

  return (
    <div
      className="fixed z-50 pointer-events-none"
      style={{ left: x, top: y, width: 240 }}
    >
      <div className="bg-white border border-border-default rounded-lg shadow-lg p-3 space-y-1.5">
        {/* 节点名称 */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-text-primary truncate">
            {data.label}
          </span>
        </div>
        {/* 节点类型 */}
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-text-muted">类型</span>
          <span className="text-[10px] text-text-secondary font-medium">
            {data.typeLabel}
          </span>
        </div>
        {/* 完整度评分 */}
        {data.completeness != null && (
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-text-muted">完整度</span>
            <span className="text-[10px] text-text-secondary font-medium">
              {data.completeness}%
            </span>
          </div>
        )}
        {/* 上游变更 */}
        {data.upstreamCount != null && data.upstreamCount > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-text-muted">变更</span>
            <span className="text-[10px] text-orange-600 font-medium">
              有 {data.upstreamCount} 项变更待合并
            </span>
          </div>
        )}
        {/* 时间信息 */}
        <div className="pt-1 border-t border-border-subtle space-y-0.5">
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-text-muted">创建</span>
            <span className="text-[10px] text-text-tertiary">
              {formatTime(data.createdAt)}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-text-muted">更新</span>
            <span className="text-[10px] text-text-tertiary">
              {formatTime(data.updatedAt)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
