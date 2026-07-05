// frontend/src/types/jd.ts
// JD 截图分析相关类型：结构化职位描述 / 分析结果（US-4）

/** LLM 从职位截图提取的结构化数据 */
export interface JDStructured {
  job_title: string;
  company: string;
  tech_stack: string[];
  hard_skills: string[];
  soft_skills: string[];
  bonus_items: string[];
}

/** POST /api/jd/analyze 响应 data */
export interface JDAnalysisResult {
  raw_text: string;
  structured: JDStructured;
}
