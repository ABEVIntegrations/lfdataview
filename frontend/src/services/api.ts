import {
  AuthStatus,
  LoginResponse,
  TableListResponse,
  TableRowsResponse,
  RowResponse,
} from '../types';

const API_BASE = 'http://localhost:8000';

async function fetchWithCredentials(url: string, options: RequestInit = {}) {
  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Include cookies for session auth
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null;
  }

  return response.json();
}

// Auth API

export async function getAuthStatus(): Promise<AuthStatus> {
  return fetchWithCredentials(`${API_BASE}/auth/status`);
}

export async function initiateLogin(): Promise<LoginResponse> {
  return fetchWithCredentials(`${API_BASE}/auth/login`);
}

export async function logout(): Promise<void> {
  await fetchWithCredentials(`${API_BASE}/auth/logout`, { method: 'POST' });
}

// Tables API

export async function fetchTables(): Promise<TableListResponse> {
  return fetchWithCredentials(`${API_BASE}/tables`);
}

export async function fetchTableRows(
  tableName: string,
  limit: number = 50,
  offset: number = 0
): Promise<TableRowsResponse> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });
  return fetchWithCredentials(`${API_BASE}/tables/${tableName}?${params}`);
}

export async function fetchTableRow(
  tableName: string,
  key: string
): Promise<RowResponse> {
  return fetchWithCredentials(`${API_BASE}/tables/${tableName}/${key}`);
}

export async function createTableRow(
  tableName: string,
  data: Record<string, unknown>
): Promise<RowResponse> {
  return fetchWithCredentials(`${API_BASE}/tables/${tableName}`, {
    method: 'POST',
    body: JSON.stringify({ data }),
  });
}

export async function updateTableRow(
  tableName: string,
  key: string,
  data: Record<string, unknown>
): Promise<RowResponse> {
  return fetchWithCredentials(`${API_BASE}/tables/${tableName}/${key}`, {
    method: 'PATCH',
    body: JSON.stringify({ data }),
  });
}

export async function deleteTableRow(
  tableName: string,
  key: string
): Promise<void> {
  await fetchWithCredentials(`${API_BASE}/tables/${tableName}/${key}`, {
    method: 'DELETE',
  });
}
