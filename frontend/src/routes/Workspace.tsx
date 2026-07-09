// frontend/src/routes/Workspace.tsx
// 工作台主页面，组合 GlobalToolbar + MainLayout
//
// US-21：activeView 提升到此层，同时传递给 GlobalToolbar 和 MainLayout

import { useCallback, useState } from 'react';
import GlobalToolbar from '@/components/layout/GlobalToolbar';
import MainLayout from '@/components/layout/MainLayout';
import type { ActiveView } from '@/types/knowledge';

export default function Workspace() {
  const [activeView, setActiveView] = useState<ActiveView>('version-tree');

  const handleNavigate = useCallback((view: ActiveView) => {
    setActiveView(view);
  }, []);

  return (
    <div className="h-screen overflow-hidden bg-bg-primary page-enter">
      <GlobalToolbar activeView={activeView} onNavigate={handleNavigate} />
      <MainLayout activeView={activeView} onNavigate={handleNavigate} />
    </div>
  );
}
