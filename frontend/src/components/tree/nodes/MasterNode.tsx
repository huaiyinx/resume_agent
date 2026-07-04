// frontend/src/components/tree/nodes/MasterNode.tsx
// 圆形节点，青色（bg-node-master），参考 design.md 第 7.3 节

import { Handle, Position, type NodeProps } from '@xyflow/react';

export interface MasterNodeData {
  label: string;
  sublabel?: string;
  [key: string]: unknown;
}

export default function MasterNode({ data }: NodeProps) {
  const nodeData = data as unknown as MasterNodeData;
  return (
    <div
      className="flex flex-col items-center justify-center rounded-full bg-bg-secondary text-node-master shadow-glow-master w-16 h-16 border-2 border-node-master"
    >
      <span className="text-xs font-semibold leading-tight">
        {nodeData.label}
      </span>
      {nodeData.sublabel && (
        <span className="text-[9px] font-mono text-text-muted leading-tight">
          {nodeData.sublabel}
        </span>
      )}
      <Handle type="source" position={Position.Right} className="!bg-node-master !border-node-master" />
      <Handle type="target" position={Position.Left} className="!bg-node-master !border-node-master" />
    </div>
  );
}
