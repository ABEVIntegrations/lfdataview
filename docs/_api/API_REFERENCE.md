# API Reference

**Last Updated:** 2025-11-18
**Base URL:** `http://localhost:8000` (development)

## Authentication Endpoints

See [Feature 01: OAuth Authentication](../features/01-oauth-authentication/README.md)

- `GET /auth/login` - Initiate OAuth flow
- `GET /auth/callback` - OAuth callback handler
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user info

## Table Endpoints

See [Feature 02: Table CRUD Operations](../features/02-table-crud-operations/API_DESIGN.md)

- `GET /tables` - List all tables
- `GET /tables/{table_name}` - Get table rows (paginated)
- `GET /tables/{table_name}/schema` - Get table column definitions
- `GET /tables/{table_name}/{key}` - Get single row
- `POST /tables/{table_name}` - Create row
- `POST /tables/{table_name}/batch` - Batch create rows
- `PATCH /tables/{table_name}/{key}` - Update row
- `DELETE /tables/{table_name}/{key}` - Delete row

### Batch Create Endpoint

`POST /tables/{table_name}/batch`

**Request Body:**
```json
{
  "rows": [
    {"Name": "Item 1", "Value": 100},
    {"Name": "Item 2", "Value": 200}
  ]
}
```

**Response:**
```json
{
  "total": 2,
  "succeeded": 2,
  "failed": 0,
  "results": [
    {"index": 0, "success": true, "data": {...}, "error": null},
    {"index": 1, "success": true, "data": {...}, "error": null}
  ]
}
```

### Schema Endpoint

`GET /tables/{table_name}/schema`

**Response:**
```json
{
  "table_name": "Holidays",
  "columns": [
    {"name": "_key", "type": "string", "required": true},
    {"name": "Name", "type": "string", "required": false},
    {"name": "Date", "type": "string", "required": false}
  ]
}
```

## Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
