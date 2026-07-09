// frontend/src/components/tree/nodes/BranchNode.tsx
// 圆角矩形节点，紫色（bg-node-branch），参考 design.md 第 7.3 节
// US-25: 节点 hover tooltip

import { Handle, Position, type NodeProps } from '@xyflow/react';
import { useNodeTooltip, TooltipLayer, type TooltipData } from './NodeTooltip';

export interface BranchNodeData {
  label: string;
  direction?: string;
  has_upstream_update?: boolean;
  /** US-25: tooltip 数据 */
  tooltipData?: TooltipData;
  [key: string]: unknown;
}

export default function BranchNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as BranchNodeData;
  const { tooltip, handleMouseEnter, handleMouseLeave } = useNodeTooltip();

  return (
    <div
      onMouseEnter={(e) => nodeData.tooltipData && handleMouseEnter(e, nodeData.tooltipData)}
      onMouseLeave={handleMouseLeave}
      className={`flex items-center justify-center rounded-lg bg-gradient-to-br from-bg-secondary to-bg-tertiary text-node-branch border-2 px-6 py-3 min-w-[100px] shadow-glow-secondary cursor-grab active:cursor-grabbing transition-all hover:scale-105 hover:shadow-lg relative node-enter ${
        selected ? 'border-brand-primary shadow-glow-primary' : 'border-node-branch'
      }`}
    >
      <span className="text-sm font-semibold pointer-events-none">
        {nodeData.label}
      </span>
      {nodeData.has_upstream_update && (
        <span
          className="absolute -top-1 -right-1 w-3 h-3 bg-orange-500 rounded-full border-2 border-white shadow-sm badge-pulse"
          title="有上游变更待合并"
        />
      )}
      <Handle type="source" position={Position.Right} className="!bg-node-branch !border-node-branch !w-2 !h-2" />
      <Handle type="target" position={Position.Left} className="!bg-node-branch !border-node-branch !w-2 !h-2" />
      <TooltipLayer tooltip={tooltip} />
    </div>
  );
}
