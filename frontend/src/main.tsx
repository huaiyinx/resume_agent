// frontend/src/main.tsx
// React 入口，导入 tokens.css 和 @xyflow/react/dist/style.css

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

import '@/styles/tokens.css';
import '@xyflow/react/dist/style.css';

const routerBase = import.meta.env.BASE_URL.replace(/\/$/, '') || '/';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter basename={routerBase}>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
