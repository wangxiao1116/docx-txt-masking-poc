import type { ApiResponse, EntityRecord, FileListPayload, FileTask, FileTaskDetail } from "@/types/api";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    cache: "no-store",
  });
  const payload = (await response.json()) as ApiResponse<T>;
  if (!response.ok || payload.code !== 0) {
    throw new Error(payload.message || "请求失败");
  }
  return payload.data;
}

export function listFiles(params: URLSearchParams) {
  const query = params.toString();
  return request<FileListPayload>(`/files${query ? `?${query}` : ""}`);
}

export async function uploadFile(formData: FormData) {
  return request<FileTask>("/files", {
    method: "POST",
    body: formData,
  });
}

export function getFileDetail(id: string) {
  return request<FileTaskDetail>(`/files/${id}`);
}

export function getPreview(id: string, kind: "original" | "masked") {
  return request<{ text: string }>(`/files/${id}/preview/${kind}`);
}

export function getEntities(id: string) {
  return request<EntityRecord[]>(`/files/${id}/entities`);
}

export async function deleteFile(id: string) {
  return request<{ deleted: string }>(`/files/${id}`, { method: "DELETE" });
}

export function downloadUrl(id: string) {
  return `${API_BASE}/files/${id}/download`;
}

export function manifestUrl() {
  return `${API_BASE}/exports/manifest.csv`;
}

export function zipUrl() {
  return `${API_BASE}/exports/results.zip`;
}
