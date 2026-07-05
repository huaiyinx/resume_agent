// frontend/src/types/gap.ts
// Gap 报告相关类型（US-5）

/** 单项 Gap 条目 */
export interface GapItem {
  skill: string;
  category: string; // tech_stack / hard_skills / soft_skills / bonus_items
  status: 'covered' | 'partial' | 'missing';
  score: number;
  description: string;
  evidence: { chunk_text: string; source_file: string; score: number }[];
}

/** 三色汇总 */
export interface GapSummary {
  covered: number;
  partial: number;
  missing: number;
}

/** POST /api/gap-report 响应 data */
export interface GapReport {
  overall_score: number;
  summary: GapSummary;
  items: GapItem[];
}
