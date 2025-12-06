import {
  AuthStatus,
  LoginResponse,
  TableListResponse,
  TableRowsResponse,
  RowResponse,
  TableSchemaResponse,
  BatchCreateResponse,
  ReplaceAllResponse,
  TableCountResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

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
  offset: number = 0,
  filters?: Record<string, string>,
  filterMode: 'and' | 'or' = 'and'
): Promise<TableRowsResponse> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });

  // Add filters if any non-empty values exist
  if (filters) {
    const activeFilters = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => value && value.trim())
    );
    if (Object.keys(activeFilters).length > 0) {
      params.set('filters', JSON.stringify(activeFilters));
      params.set('filter_mode', filterMode);
    }
  }

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

export async function fetchTableSchema(
  tableName: string
): Promise<TableSchemaResponse> {
  return fetchWithCredentials(`${API_BASE}/tables/${tableName}/schema`);
}

export async function fetchTableRowCount(
  tableName: string
): Promise<TableCountResponse> {
  return fetchWithCredentials(`${API_BASE}/tables/${tableName}/count`);
}

export async function batchCreateRows(
  tableName: string,
  rows: Record<string, unknown>[]
): Promise<BatchCreateResponse> {
  return fetchWithCredentials(`${API_BASE}/tables/${tableName}/batch`, {
    method: 'POST',
    body: JSON.stringify({ rows }),
  });
}

export async function replaceAllRows(
  tableName: string,
  rows: Record<string, unknown>[]
): Promise<ReplaceAllResponse> {
  return fetchWithCredentials(`${API_BASE}/tables/${tableName}/replace`, {
    method: 'POST',
    body: JSON.stringify({ rows }),
  });
}
