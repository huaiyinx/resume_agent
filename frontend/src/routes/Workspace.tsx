// frontend/src/routes/Workspace.tsx
// 工作台主页面，组合 GlobalToolbar + MainLayout
//
// US-21：activeView 提升到此层，同时传递给 GlobalToolbar 和 MainLayout
// v1.4: rightPanelCollapsed — 点击"简历版本分支"时收起右栏
//       navKey — 每次导航点击递增，强制 CenterPanel 重置 activeTab 到"版本树"

import { useCallback, useEffect, useState } from 'react';
import GlobalToolbar from '@/components/layout/GlobalToolbar';
import MainLayout from '@/components/layout/MainLayout';
import type { ActiveView } from '@/types/knowledge';
import type { MobileAction, MobilePane } from '@/types/layout';

export default function Workspace() {
  const [activeView, setActiveView] = useState<ActiveView>('version-tree');
  const [rightPanelCollapsed, setRightPanelCollapsed] = useState(false);
  const [mobilePane, setMobilePane] = useState<MobilePane>('workspace');
  // 导航计数器：每次点击导航项都递增，即使 activeView 没变也能强制重置
  const [navKey, setNavKey] = useState(0);

  useEffect(() => {
    window.__careerAppReady?.();
  }, []);

  const handleNavigate = useCallback((view: ActiveView) => {
    setActiveView(view);
    setMobilePane('workspace');
    setNavKey((k) => k + 1);
    // 切换到知识库时展开右栏（需要 JD 分析）
    if (view === 'knowledge') {
      setRightPanelCollapsed(false);
    }
  }, []);

  const handleMobileAction = useCallback((action: MobileAction) => {
    if (action === 'materials') {
      setMobilePane('materials');
      return;
    }
    if (action === 'career') {
      setRightPanelCollapsed(false);
      setMobilePane('career');
      return;
    }

    setActiveView(action === 'knowledge' ? 'knowledge' : 'version-tree');
    setMobilePane('workspace');
    setNavKey((key) => key + 1);
  }, []);

  return (
    <div className="h-screen overflow-hidden bg-bg-primary career-workspace-shell">
      <GlobalToolbar
        activeView={activeView}
        onNavigate={handleNavigate}
        onToggleRightPanel={setRightPanelCollapsed}
        rightPanelCollapsed={rightPanelCollapsed}
        mobilePane={mobilePane}
        onMobileAction={handleMobileAction}
      />
      <MainLayout
        activeView={activeView}
        onNavigate={handleNavigate}
        rightPanelCollapsed={rightPanelCollapsed}
        onToggleRightPanel={setRightPanelCollapsed}
        navKey={navKey}
        mobilePane={mobilePane}
      />
    </div>
  );
}
