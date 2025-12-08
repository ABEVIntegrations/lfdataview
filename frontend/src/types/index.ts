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

export interface ColumnInfo {
  name: string;
  type: string;  // OData types: Edm.String, Edm.Int32, Edm.Int64, Edm.Decimal, Edm.Double, Edm.Boolean, Edm.DateTime, etc.
  required: boolean;
}

// Validation helper for OData types
export function validateODataType(value: string, type: string): { valid: boolean; message?: string } {
  if (value === '' || value === null || value === undefined) {
    return { valid: true }; // Empty is allowed (validation for required is separate)
  }

  const lowerType = type.toLowerCase();

  // Integer types
  if (lowerType.includes('int')) {
    if (!/^-?\d+$/.test(value)) {
      return { valid: false, message: 'Must be a whole number' };
    }
    const num = parseInt(value, 10);
    if (lowerType.includes('int16') && (num < -32768 || num > 32767)) {
      return { valid: false, message: 'Value out of range for Int16' };
    }
    if (lowerType.includes('int32') && (num < -2147483648 || num > 2147483647)) {
      return { valid: false, message: 'Value out of range for Int32' };
    }
    return { valid: true };
  }

  // Decimal/Double types
  if (lowerType.includes('decimal') || lowerType.includes('double') || lowerType.includes('single')) {
    if (!/^-?\d*\.?\d+$/.test(value)) {
      return { valid: false, message: 'Must be a number' };
    }
    return { valid: true };
  }

  // Boolean
  if (lowerType.includes('boolean')) {
    if (!['true', 'false', '1', '0', 'yes', 'no'].includes(value.toLowerCase())) {
      return { valid: false, message: 'Must be true or false' };
    }
    return { valid: true };
  }

  // DateTime
  if (lowerType.includes('datetime') || lowerType.includes('date')) {
    // Allow ISO format or common date formats
    const date = new Date(value);
    if (isNaN(date.getTime())) {
      return { valid: false, message: 'Must be a valid date' };
    }
    return { valid: true };
  }

  // String and other types - no validation
  return { valid: true };
}

export interface TableSchemaResponse {
  table_name: string;
  columns: ColumnInfo[];
}

export interface RowResult {
  index: number;
  success: boolean;
  data?: Record<string, unknown>;
  error?: string;
}

export interface BatchCreateResponse {
  total: number;
  succeeded: number;
  failed: number;
  results: RowResult[];
}

export interface ReplaceAllResponse {
  success: boolean;
  rows_replaced: number;
  error?: string;
}

export interface TableCountResponse {
  table_name: string;
  row_count: number;
}

/**
 * Convert OData type to user-friendly display name
 */
export function getDisplayType(odataType: string): string {
  const lowerType = odataType.toLowerCase();

  if (lowerType.includes('int')) {
    return 'Integer';
  }
  if (lowerType.includes('decimal') || lowerType.includes('double') || lowerType.includes('single')) {
    return 'Decimal';
  }
  if (lowerType.includes('boolean')) {
    return 'Yes/No';
  }
  if (lowerType.includes('datetime')) {
    return 'Date/Time';
  }
  if (lowerType.includes('date')) {
    return 'Date';
  }
  // Default to Text for Edm.String and anything else
  return 'Text';
}

/**
 * Convert a string value to the appropriate JavaScript type based on OData type.
 * This is needed because Laserfiche API requires proper types (numbers, not strings).
 */
export function convertValueForApi(value: string, odataType: string): string | number | boolean | null {
  // Handle empty values
  if (value === '' || value === null || value === undefined) {
    return null;
  }

  const lowerType = odataType.toLowerCase();

  // Integer types - convert to number
  if (lowerType.includes('int')) {
    const num = parseInt(value, 10);
    return isNaN(num) ? value : num;
  }

  // Decimal/Double types - convert to number
  if (lowerType.includes('decimal') || lowerType.includes('double') || lowerType.includes('single')) {
    const num = parseFloat(value);
    return isNaN(num) ? value : num;
  }

  // Boolean types
  if (lowerType.includes('boolean')) {
    const lower = value.toLowerCase();
    if (['true', '1', 'yes'].includes(lower)) return true;
    if (['false', '0', 'no'].includes(lower)) return false;
    return value;
  }

  // String and other types - return as-is
  return value;
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
