// frontend/src/components/common/Breadcrumb.tsx
// 路径面包屑（master / security / tencent-rs）

interface BreadcrumbProps {
  segments?: string[];
}

const DEFAULT_SEGMENTS = ['master', 'security', 'tencent-researcher'];

export default function Breadcrumb({ segments = DEFAULT_SEGMENTS }: BreadcrumbProps) {
  return (
    <nav className="flex items-center gap-2 text-sm">
      {segments.map((seg, i) => (
        <span key={seg} className="flex items-center gap-2">
          {i > 0 && <span className="text-text-muted text-xs">/</span>}
          <span
            className={
              i === segments.length - 1
                ? 'text-text-primary font-medium cursor-pointer'
                : 'text-text-secondary cursor-pointer hover:text-brand-primary transition-colors'
            }
          >
            {seg}
          </span>
        </span>
      ))}
    </nav>
  );
}
