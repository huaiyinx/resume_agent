// frontend/src/lib/api.ts
// API 调用封装（fetch wrapper），统一处理 ok/data/error 格式

import type { ApiResponse } from '@/types/tree';

const BASE_URL = '/api';

/**
 * 统一 fetch 封装，自动解析 ApiResponse envelope。
 * 返回 data 部分（ok=true 时），或抛出 Error（ok=false 时）。
 */
export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }

  const json: ApiResponse<T> = await res.json();

  if (!json.ok) {
    throw new Error(json.error?.message ?? 'Unknown error');
  }

  return json.data as T;
}

/** 便捷方法 */
export const api = {
  get: <T>(endpoint: string) =>
    apiRequest<T>(endpoint, { method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  upload: <T>(endpoint: string, formData: FormData) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: formData,
      // 不设置 Content-Type，让浏览器自动设置 multipart boundary
    }),
};
