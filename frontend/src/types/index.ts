// API Response Types

export interface TableInfo {
  name: string;
  displayName?: string;
  description?: string;
}

export interface TableListResponse {
  tables: TableInfo[];
}

export interface TableRowsResponse {
  rows: Record<string, unknown>[];
  total: number;
  limit: number;
  offset: number;
}

export interface RowResponse {
  data: Record<string, unknown>;
}

export interface AuthStatus {
  authenticated: boolean;
  user?: {
    id: string;
    username: string;
  };
}

export interface LoginResponse {
  redirect_url: string;
  state: string;
}

// UI Types

export interface PaginationState {
  page: number;
  limit: number;
}
