// frontend/src/components/tree/nodes/CompanyNode.tsx
// 矩形节点，橙色（bg-node-company），参考 design.md 第 7.3 节
// US-25: 节点 hover tooltip

import { Handle, Position, type NodeProps } from '@xyflow/react';
import { useNodeTooltip, TooltipLayer, type TooltipData } from './NodeTooltip';

export interface CompanyNodeData {
  label: string;
  company?: string;
  role?: string;
  has_upstream_update?: boolean;
  /** US-25: tooltip 数据 */
  tooltipData?: TooltipData;
  [key: string]: unknown;
}

export default function CompanyNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as CompanyNodeData;
  const { tooltip, handleMouseEnter, handleMouseLeave } = useNodeTooltip();

  return (
    <div
      onMouseEnter={(e) => nodeData.tooltipData && handleMouseEnter(e, nodeData.tooltipData)}
      onMouseLeave={handleMouseLeave}
      className={`flex flex-col items-center justify-center rounded-lg bg-gradient-to-br from-bg-secondary to-bg-tertiary text-node-company border-2 px-6 py-2 min-w-[140px] shadow-md cursor-grab active:cursor-grabbing transition-all hover:scale-105 hover:shadow-lg relative node-enter ${
        selected ? 'border-brand-primary shadow-glow-primary' : 'border-node-company'
      }`}
    >
      <span className="text-xs font-semibold text-node-company pointer-events-none">
        {nodeData.company ?? nodeData.label}
      </span>
      {nodeData.role && (
        <span className="text-xs text-text-primary pointer-events-none">
          {nodeData.role}
        </span>
      )}
      {nodeData.has_upstream_update && (
        <span
          className="absolute -top-1 -right-1 w-3 h-3 bg-orange-500 rounded-full border-2 border-white shadow-sm badge-pulse"
          title="有上游变更待合并"
        />
      )}
      <Handle type="source" position={Position.Right} className="!bg-node-company !border-node-company !w-2 !h-2" />
      <Handle type="target" position={Position.Left} className="!bg-node-company !border-node-company !w-2 !h-2" />
      <TooltipLayer tooltip={tooltip} />
    </div>
  );
}
