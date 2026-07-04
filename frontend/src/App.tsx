// frontend/src/App.tsx
// 路由根（参考 design.md 第 7.4 节）

import { Routes, Route } from 'react-router-dom';
import Workspace from '@/routes/Workspace';
import Onboarding from '@/routes/Onboarding';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Workspace />} />
      <Route path="/onboarding" element={<Onboarding />} />
    </Routes>
  );
}
