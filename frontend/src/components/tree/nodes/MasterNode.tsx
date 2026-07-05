// frontend/src/components/tree/nodes/MasterNode.tsx
// 圆形节点，青色（bg-node-master），参考 design.md 第 7.3 节

import { Handle, Position, type NodeProps } from '@xyflow/react';

export interface MasterNodeData {
  label: string;
  sublabel?: string;
  [key: string]: unknown;
}

export default function MasterNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as MasterNodeData;
  return (
    <div
      className={`flex flex-col items-center justify-center rounded-full bg-bg-secondary text-node-master shadow-glow-master w-16 h-16 border-2 transition-shadow cursor-grab active:cursor-grabbing ${
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
    </div>
  );
}
