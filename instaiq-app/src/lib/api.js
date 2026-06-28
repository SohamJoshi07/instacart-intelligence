import { API_BASE } from "./constants";

export async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      let detail = `Error ${res.status}`;
      try { const b = await res.json(); detail = b.detail || b.message || detail; } catch {}
      return { ok: false, error: detail };
    }
    return { ok: true, data: await res.json() };
  } catch (err) {
    return {
      ok: false,
      error: err instanceof TypeError
        ? "Cannot reach the API — is the backend running? Is CORS enabled?"
        : err.message,
    };
  }
}

export const getHealth          = ()            => apiFetch("/health");
export const getSegment         = (uid)         => apiFetch(`/segment/${encodeURIComponent(uid)}`);
export const getRecommendations = (uid, n = 10) => apiFetch(`/recommendations/${encodeURIComponent(uid)}?n=${n}`);
export const getSimilarItems    = (pid, n = 5)  => apiFetch(`/similar-items/${encodeURIComponent(pid)}?n=${n}`);
export const askQuestion        = (q)           => apiFetch("/ask", { method: "POST", body: JSON.stringify({ question: q }) });

export function extractAnswer(data) {
  if (typeof data === "string") return data;
  return data?.answer || data?.response || data?.text || data?.result || JSON.stringify(data, null, 2);
}
