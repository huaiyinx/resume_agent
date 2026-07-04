// frontend/src/types/tree.ts

export type NodeType = 'master' | 'branch' | 'company';

export interface ResumeNode {
  id: string;
  node_id: string;
  parent_id: string | null;
  node_type: NodeType;
  title: string;
  company?: string | null;
  direction?: string | null;
}

export interface TreeEdge {
  source: string;
  target: string;
}

export interface TreeData {
  nodes: ResumeNode[];
  edges: TreeEdge[];
}

/** API 统一响应格式 */
export interface ApiResponse<T> {
  ok: boolean;
  data: T | null;
  error: { code: string; message: string } | null;
}
