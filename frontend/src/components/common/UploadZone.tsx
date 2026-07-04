// frontend/src/components/common/UploadZone.tsx
// 拖拽上传区（UI，不接后端）

interface UploadZoneProps {
  title: string;
  hint: string;
  icon?: React.ReactNode;
  onClick?: () => void;
}

export default function UploadZone({ title, hint, icon, onClick }: UploadZoneProps) {
  return (
    <div
      onClick={onClick}
      className="border-[1.5px] border-dashed border-border-default rounded-lg p-4 text-center transition-all cursor-pointer hover:border-brand-primary hover:bg-brand-primary-muted"
    >
      <div className="mb-2 opacity-50 flex justify-center text-text-muted">
        {icon ?? (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        )}
      </div>
      <div className="text-xs font-medium text-text-secondary mb-1">
        {title}
      </div>
      <div className="text-xs text-text-muted">
        {hint}
      </div>
    </div>
  );
}
