// frontend/src/components/tree/nodes/CompanyNode.tsx
// 矩形节点，橙色（bg-node-company），参考 design.md 第 7.3 节

import { Handle, Position, type NodeProps } from '@xyflow/react';

export interface CompanyNodeData {
  label: string;
  company?: string;
  role?: string;
  [key: string]: unknown;
}

export default function CompanyNode({ data }: NodeProps) {
  const nodeData = data as unknown as CompanyNodeData;
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg bg-bg-secondary text-node-company border-2 border-node-company px-6 py-2 min-w-[140px] shadow-md"
    >
      <span className="text-xs font-semibold text-node-company">
        {nodeData.company ?? nodeData.label}
      </span>
      {nodeData.role && (
        <span className="text-xs text-text-primary">
          {nodeData.role}
        </span>
      )}
      <Handle type="source" position={Position.Right} className="!bg-node-company !border-node-company" />
      <Handle type="target" position={Position.Left} className="!bg-node-company !border-node-company" />
    </div>
  );
}
