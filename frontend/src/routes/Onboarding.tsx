// frontend/src/routes/Onboarding.tsx
// 首次引导（骨架，简单占位）

import { useNavigate } from 'react-router-dom';

export default function Onboarding() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary">
      <div className="text-center max-w-md px-8">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="mx-auto mb-4"
          style={{ color: 'var(--color-brand-primary)' }}
        >
          <line x1="6" y1="3" x2="6" y2="15" />
          <circle cx="18" cy="6" r="3" />
          <circle cx="6" cy="18" r="3" />
          <path d="M18 9a9 9 0 0 1-9 9" />
        </svg>
        <h1 className="text-xl font-bold text-text-primary mb-2">
          欢迎使用 Resume-Agent
        </h1>
        <p className="text-sm text-text-secondary mb-6">
          智能简历工作台 · 版本树管理 · AI 生成
        </p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-2.5 text-white text-sm font-medium rounded-md border-none cursor-pointer transition-all hover:brightness-110"
          style={{
            background:
              'linear-gradient(135deg, var(--color-accent-gradient-start), var(--color-accent-gradient-end))',
          }}
        >
          进入工作台
        </button>
      </div>
    </div>
  );
}
