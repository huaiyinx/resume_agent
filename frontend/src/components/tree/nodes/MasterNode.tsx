// frontend/src/components/tree/nodes/MasterNode.tsx
// 圆形节点，青色（bg-node-master），参考 design.md 第 7.3 节
// US-25: 节点 hover tooltip

import { Handle, Position, type NodeProps } from '@xyflow/react';
import { useNodeTooltip, TooltipLayer, type TooltipData } from './NodeTooltip';

export interface MasterNodeData {
  label: string;
  sublabel?: string;
  /** US-25: tooltip 数据 */
  tooltipData?: TooltipData;
  [key: string]: unknown;
}

export default function MasterNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as MasterNodeData;
  const { tooltip, handleMouseEnter, handleMouseLeave } = useNodeTooltip();

  return (
    <div
      onMouseEnter={(e) => nodeData.tooltipData && handleMouseEnter(e, nodeData.tooltipData)}
      onMouseLeave={handleMouseLeave}
      className={`flex flex-col items-center justify-center rounded-full bg-gradient-to-br from-bg-secondary to-bg-tertiary text-node-master shadow-glow-master w-16 h-16 border-2 transition-all hover:scale-105 hover:shadow-lg cursor-grab active:cursor-grabbing node-enter ${
        selected ? 'border-brand-primary shadow-glow-primary' : 'border-node-master'
      }`}
      style={{ width: 64, height: 64 }}
    >
      <span className="text-xs font-semibold leading-tight pointer-events-none">
        {nodeData.label}
      </span>
      {nodeData.sublabel && (
        <span className="text-[9px] font-mono text-text-muted leading-tight pointer-events-none">
          {nodeData.sublabel}
        </span>
      )}
      <Handle type="source" position={Position.Right} className="!bg-node-master !border-node-master !w-2 !h-2" />
      <Handle type="target" position={Position.Left} className="!bg-node-master !border-node-master !w-2 !h-2" />
      <TooltipLayer tooltip={tooltip} />
    </div>
  );
}
