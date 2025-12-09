# API Reference

**Last Updated:** 2025-12-09
**Base URL:** `http://localhost:8000` (development)
**Version:** 1.0 (Community Edition - Read-Only)

## Authentication Endpoints

- `GET /auth/login` - Initiate OAuth flow (returns redirect URL, sets state cookie)
- `GET /auth/callback` - OAuth callback handler (exchanges code, sets token cookie)
- `POST /auth/logout` - Logout user (clears cookies)
- `GET /auth/status` - Check if user is authenticated

## Table Endpoints (Read-Only)

- `GET /tables` - List all tables
- `GET /tables/{table_name}` - Get table rows (paginated, with optional filtering)
- `GET /tables/{table_name}/schema` - Get table column definitions
- `GET /tables/{table_name}/count` - Get table row count
- `GET /tables/{table_name}/{key}` - Get single row by key

### List Tables

`GET /tables`

**Response:**
```json
{
  "tables": [
    {"name": "Holidays", "displayName": "Holidays", "description": null},
    {"name": "Customers", "displayName": "Customers", "description": null}
  ]
}
```

### Get Table Rows

`GET /tables/{table_name}?limit=50&offset=0`

**Query Parameters:**
- `limit` (int, default: 50, max: 1000) - Number of rows per page
- `offset` (int, default: 0) - Number of rows to skip
- `filters` (JSON string) - Filter object, e.g., `{"Name": "test"}`
- `filter_mode` (string, default: "and") - Filter logic: "and" or "or"

**Response:**
```json
{
  "rows": [
    {"_key": "1", "Name": "New Year's Day", "Date": "2025-01-01"},
    {"_key": "2", "Name": "Memorial Day", "Date": "2025-05-26"}
  ],
  "total": 12,
  "limit": 50,
  "offset": 0
}
```

### Get Table Row Count

`GET /tables/{table_name}/count`

**Response:**
```json
{
  "table_name": "Holidays",
  "row_count": 12
}
```

### Get Table Schema

`GET /tables/{table_name}/schema`

**Response:**
```json
{
  "table_name": "Holidays",
  "columns": [
    {"name": "_key", "type": "Edm.String", "required": true},
    {"name": "Name", "type": "Edm.String", "required": false},
    {"name": "Date", "type": "Edm.String", "required": false}
  ]
}
```

### Get Single Row

`GET /tables/{table_name}/{key}`

**Response:**
```json
{
  "data": {"_key": "1", "Name": "New Year's Day", "Date": "2025-01-01"}
}
```

## Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OAuth Test Page:** http://localhost:8000/test

**Note:** The Swagger UI shows the API structure but cannot authenticate directly. To test authenticated endpoints:

1. Login via the frontend at `http://localhost:3000` first
2. Then visit `http://localhost:8000/docs` in the same browser
3. The auth cookie will be included with requests

Alternatively, use the OAuth test page at `http://localhost:8000/test` to login and test auth status directly from the backend.

## Community Edition Limitations

This is a read-only edition. The following operations are **not available**:

- `POST /tables/{table_name}` - Create row
- `POST /tables/{table_name}/batch` - Batch create rows
- `POST /tables/{table_name}/replace` - Replace all rows
- `PATCH /tables/{table_name}/{key}` - Update row
- `DELETE /tables/{table_name}/{key}` - Delete row

For write capabilities, see **LFDataView Managed**.
