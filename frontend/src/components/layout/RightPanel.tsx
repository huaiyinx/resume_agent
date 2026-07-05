// frontend/src/components/layout/RightPanel.tsx
// 右栏：JD 分析卡片 + Gap 报告列表 + AI 生成预览区（空状态）
// US-4：JD 分析区域接入真实后端（analyzeJD），无结果时显示 JDUploadZone，
//       有结果时显示 JDCard + "重新分析"按钮。

import { useState } from 'react';
import JDUploadZone from '@/components/jd/JDUploadZone';
import JDCard from '@/components/jd/JDCard';
import type { JDAnalysisResult } from '@/types/jd';

const GAP_ITEMS = [
  { name: 'C++ 底层', desc: '精通内存管理、模板编程', status: 'covered' },
  { name: '漏洞挖掘', desc: 'fuzzing 工具使用, 0day 发现流程', status: 'partial' },
  { name: 'x86 汇编', desc: '指令集熟练阅读与调试', status: 'covered' },
  { name: '逆向工程', desc: 'IDA Pro, Ghidra 等工具链', status: 'partial' },
  { name: 'Python 安全', desc: '安全自动化脚本开发', status: 'covered' },
  { name: 'ARM 汇编', desc: '移动端漏洞分析', status: 'missing' },
] as const;

const GAP_BADGE: Record<string, { label: string; cls: string }> = {
  covered: { label: '已覆盖', cls: 'bg-[rgba(5,150,105,0.08)] text-success' },
  partial: { label: '部分缺口', cls: 'bg-[rgba(217,119,6,0.08)] text-warning' },
  missing: { label: '未涉及', cls: 'bg-[rgba(220,38,38,0.08)] text-error' },
};

export default function RightPanel() {
  // JD 分析结果（US-4）：null 时显示上传区，非 null 时显示 JDCard
  const [jdResult, setJdResult] = useState<JDAnalysisResult | null>(null);

  function handleJDAnalyzed(result: JDAnalysisResult) {
    setJdResult(result);
  }

  function handleReset() {
    setJdResult(null);
  }

  return (
    <aside
      className="flex flex-col overflow-y-auto bg-bg-secondary border-l border-border-default"
      style={{ width: 'var(--right-panel-width)', minWidth: 'var(--right-panel-width)' }}
    >
      {/* Section 1: JD 分析 */}
      <section className="border-b border-border-subtle p-4">
        <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-text-primary">
          <svg
            className="w-4 h-4 opacity-70"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            style={{ color: 'var(--color-node-company)' }}
          >
            <rect x="2" y="3" width="12" height="10" rx="1.5" />
            <path d="M2 6h12" />
            <circle cx="11" cy="9" r="1.5" />
          </svg>
          职位截图分析
        </div>

        {/* 无分析结果：上传区；有结果：结构化卡片 + 重新分析 */}
        {jdResult ? (
          <div className="flex flex-col gap-2">
            <JDCard result={jdResult} />
            <button
              type="button"
              onClick={handleReset}
              className="self-start text-xs px-3 py-1.5 rounded-md border border-border-default text-text-secondary bg-bg-elevated cursor-pointer transition-all hover:border-brand-primary hover:text-brand-primary font-body"
            >
              重新分析
            </button>
          </div>
        ) : (
          <JDUploadZone onAnalyzed={handleJDAnalyzed} />
        )}
      </section>

      {/* Section 2: Gap 报告 */}
      <section className="border-b border-border-subtle p-4">
        <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-text-primary">
          <svg
            className="w-4 h-4 opacity-70"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            style={{ color: 'var(--state-warning)' }}
          >
            <path d="M8 1.5a6.5 6.5 0 0 0-6.5 6.5c0 2.5 1.5 4.5 3 5.8.5.4.8 1 .8 1.7v.5h5v-.5c0-.7.3-1.3.8-1.7 1.5-1.3 3-3.3 3-5.8A6.5 6.5 0 0 0 8 1.5z" />
            <line x1="5.5" y1="16" x2="10.5" y2="16" />
            <path d="M8 5v4M8 11.5v.5" />
          </svg>
          知识盲区报告
        </div>

        {GAP_ITEMS.map((item) => {
          const badge = GAP_BADGE[item.status];
          return (
            <div
              key={item.name}
              className="flex items-start gap-2 py-2 border-b border-border-subtle last:border-b-0"
            >
              <div className="flex-1">
                <div className="text-sm font-medium text-text-primary min-w-[90px]">
                  {item.name}
                </div>
                <div className="text-xs text-text-tertiary leading-tight">
                  {item.desc}
                </div>
              </div>
              <span
                className={`text-[10px] px-2 py-px rounded-full font-medium whitespace-nowrap flex-shrink-0 ${badge.cls}`}
              >
                {badge.label}
              </span>
            </div>
          );
        })}
      </section>

      {/* Section 3: AI 生成预览区（空状态） */}
      <section className="p-4">
        <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-text-primary">
          <svg
            className="w-4 h-4 opacity-70"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            style={{ color: 'var(--color-brand-primary)' }}
          >
            <path d="M12 10V5a4 4 0 1 0-8 0v5" />
            <rect x="1" y="10" width="14" height="4" rx="1.5" />
            <circle cx="5" cy="12" r="1" fill="currentColor" />
            <circle cx="11" cy="12" r="1" fill="currentColor" />
          </svg>
          AI 求职导师
        </div>

        <div className="bg-bg-tertiary rounded-lg p-4 border border-border-subtle">
          <div className="text-sm text-text-secondary leading-snug mb-3">
            针对该岗位分析，你的核心技术栈匹配度约{' '}
            <strong className="text-brand-primary">72%</strong>
            。主要差距集中在漏洞挖掘实战经验和 ARM 汇编方向。建议优先补充这两个领域的项目经历。
          </div>

          <div className="text-sm font-semibold text-text-primary mb-2">
            面试前补充建议
          </div>
          {[
            '完成 2-3 个真实漏洞复现实验 (CVE 复现), 整理 writeup 放入知识库',
            '学习 ARM 基础指令集, 完成 one CTF ARM PWN 题',
            '准备 1-2 个安全工具开发项目案例, 体现工程能力',
          ].map((tip) => (
            <div
              key={tip}
              className="flex items-start gap-2 text-xs text-text-secondary mb-1.5 leading-snug"
            >
              <div className="w-1 h-1 rounded-full bg-brand-primary flex-shrink-0 mt-1.5" />
              <span>{tip}</span>
            </div>
          ))}

          <div className="flex flex-wrap gap-1.5 mt-3">
            {['OWASP Top 10 实战项目', 'CTFtime PWN 入门', 'AFL++ Fuzzing 教程'].map((link) => (
              <a
                key={link}
                href="#"
                className="text-xs px-3 py-1 bg-bg-elevated text-brand-primary border border-brand-primary-muted rounded-full cursor-pointer transition-all hover:bg-brand-primary-muted no-underline"
              >
                {link}
              </a>
            ))}
          </div>
        </div>
      </section>
    </aside>
  );
}
