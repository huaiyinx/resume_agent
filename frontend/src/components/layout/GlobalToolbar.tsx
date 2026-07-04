// frontend/src/components/layout/GlobalToolbar.tsx
// 顶部 48px 工具栏：logo + 导航 Tab + 右侧状态（本地模式 chip + 头像）

import { useState } from 'react';

const NAV_TABS = ['总览面板', '简历版本分支', '知识库', '设置'] as const;

export default function GlobalToolbar() {
  const [activeTab, setActiveTab] = useState<string>('总览面板');

  return (
    <header
      className="h-12 bg-bg-secondary border-b border-border-default flex items-center justify-between px-6 sticky top-0 z-50 backdrop-blur-md"
    >
      {/* Logo */}
      <div className="flex items-center gap-2 font-body font-semibold text-text-primary tracking-tight text-sm">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ color: 'var(--color-brand-primary)' }}
        >
          <line x1="6" y1="3" x2="6" y2="15" />
          <circle cx="18" cy="6" r="3" />
          <circle cx="6" cy="18" r="3" />
          <path d="M18 9a9 9 0 0 1-9 9" />
        </svg>
        Resume-Agent
        <span className="font-mono text-xs text-text-muted bg-bg-tertiary px-2 py-px rounded-sm tracking-wider">
          v0.3.1
        </span>
      </div>

      {/* Nav tabs */}
      <nav className="flex gap-1">
        {NAV_TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1.5 rounded-md text-sm transition-all border-none cursor-pointer font-body ${
              activeTab === tab
                ? 'text-brand-primary bg-brand-primary-muted font-medium'
                : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
            }`}
          >
            {tab}
          </button>
        ))}
      </nav>

      {/* Right status */}
      <div className="flex items-center gap-3 text-xs">
        <div
          className="w-1.5 h-1.5 rounded-full"
          style={{ background: 'var(--state-success)', boxShadow: '0 0 6px var(--state-success)' }}
        />
        <span className="text-text-secondary">知识库在线</span>
        <span className="text-xs px-3 py-px rounded-full bg-bg-tertiary text-text-tertiary border border-border-subtle font-body">
          本地模式
        </span>
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold text-white"
          style={{
            background:
              'linear-gradient(135deg, var(--color-brand-primary), var(--color-brand-secondary))',
          }}
        >
          L
        </div>
      </div>
    </header>
  );
}
