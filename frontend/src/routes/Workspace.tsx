// frontend/src/routes/Workspace.tsx
// 工作台主页面，组合 GlobalToolbar + MainLayout

import GlobalToolbar from '@/components/layout/GlobalToolbar';
import MainLayout from '@/components/layout/MainLayout';

export default function Workspace() {
  return (
    <div className="h-screen overflow-hidden bg-bg-primary">
      <GlobalToolbar />
      <MainLayout />
    </div>
  );
}
