// frontend/src/components/tree/VersionTree.tsx
// React Flow 画布，渲染 mock 版本树

import { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { mockTree } from '@/data/mockTree';
import MasterNode, { type MasterNodeData } from './nodes/MasterNode';
import BranchNode, { type BranchNodeData } from './nodes/BranchNode';
import CompanyNode, { type CompanyNodeData } from './nodes/CompanyNode';

const nodeTypes = {
  master: MasterNode,
  branch: BranchNode,
  company: CompanyNode,
};

/** 布局位置：从左到右三层 */
const POSITION_MAP: Record<string, { x: number; y: number }> = {
  master: { x: 80, y: 200 },
  security: { x: 310, y: 130 },
  algorithm: { x: 310, y: 310 },
  'tencent-researcher': { x: 570, y: 90 },
  'bytedance-security': { x: 570, y: 190 },
  'bytedance-algorithm': { x: 570, y: 310 },
};

export default function VersionTree() {
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = mockTree.nodes.map((n) => {
      const pos = POSITION_MAP[n.node_id] ?? { x: 0, y: 0 };
      const base = { id: n.node_id, type: n.node_type, position: pos };

      if (n.node_type === 'master') {
        return {
          ...base,
          data: { label: 'master', sublabel: 'main' } as MasterNodeData,
        };
      }
      if (n.node_type === 'branch') {
        return {
          ...base,
          data: { label: n.title, direction: n.direction ?? '' } as BranchNodeData,
        };
      }
      // company
      const [company, ...rest] = n.title.split(' ');
      return {
        ...base,
        data: {
          label: n.title,
          company: company,
          role: rest.join(' '),
        } as CompanyNodeData,
      };
    });

    const edges: Edge[] = mockTree.edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#a78bfa', strokeWidth: 1.8, opacity: 0.5 },
    }));

    return { nodes, edges };
  }, []);

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#e2e8f0" gap={30} size={1} />
        <Controls
          className="!bg-bg-secondary !border-border-default !rounded-md"
          showInteractive={false}
        />
        <MiniMap
          className="!bg-bg-secondary !border-border-default !rounded-md"
          nodeColor={(node) => {
            switch (node.type) {
              case 'master': return '#0891b2';
              case 'branch': return '#7c3aed';
              case 'company': return '#d97706';
              default: return '#cbd5e1';
            }
          }}
          maskColor="rgba(241, 245, 249, 0.7)"
        />
      </ReactFlow>

      {/* Legend */}
      <div className="absolute bottom-3 left-4 flex gap-5 text-xs text-text-tertiary bg-bg-secondary border border-border-subtle rounded-md px-4 py-2 z-10">
        <div className="flex items-center gap-1.5">
          <div
            className="w-2 h-2 rounded-full"
            style={{ background: 'var(--color-node-master)', boxShadow: '0 0 6px var(--color-node-master)' }}
          />
          <span>主干节点</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div
            className="w-2 h-2 rounded-full"
            style={{ background: 'var(--color-node-branch)', boxShadow: '0 0 6px var(--color-node-branch)' }}
          />
          <span>方向分支</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div
            className="w-2 h-2 rounded-full"
            style={{ background: 'var(--color-node-company)', boxShadow: '0 0 6px var(--color-node-company)' }}
          />
          <span>公司节点</span>
        </div>
      </div>
    </div>
  );
}
