// frontend/src/components/common/KnowledgeStatus.tsx
// 知识库状态指示器（切片数+索引进度）

interface KnowledgeStatusProps {
  chunkCount?: number;
  progress?: number; // 0-100
  backend?: string;
}

export default function KnowledgeStatus({
  chunkCount = 86,
  progress = 72,
  backend = 'Chroma local',
}: KnowledgeStatusProps) {
  return (
    <div className="mt-auto p-4 border-t border-border-subtle">
      <div className="flex items-center gap-2 text-xs text-text-tertiary mb-2">
        <svg
          width="12"
          height="12"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          style={{ color: 'var(--color-brand-primary)' }}
        >
          <path d="M8 2l1.5 3H14l-2.5 2 1 3.5L8 8.5 3.5 10.5l1-3.5L2 5h4.5z" />
        </svg>
        <span>知识库索引</span>
      </div>
      <div className="w-full h-1 bg-bg-elevated rounded-full overflow-hidden mb-2">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${progress}%`,
            background:
              'linear-gradient(90deg, var(--color-brand-primary), var(--color-brand-secondary))',
          }}
        />
      </div>
      <div className="text-xs font-mono text-text-muted tracking-wider">
        {chunkCount} 篇切片 · {backend}
      </div>
    </div>
  );
}
