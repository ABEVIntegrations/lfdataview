# Feature 02: Table CRUD Operations

**Phase:** 1 - MVP
**Priority:** Critical
**Status:** 📋 Planned

## Overview

This feature wraps the Laserfiche OData Table API to provide CRUD (Create, Read, Update, Delete) operations on lookup table data. The FastAPI backend acts as a proxy between the React frontend and Laserfiche, adding authentication, error handling, and data transformation.

## OData Table API Operations

### Base URL
`https://api.laserfiche.com/odata4`

### Supported Operations

| Operation | HTTP Method | Laserfiche Endpoint | Required Scope |
|-----------|-------------|---------------------|----------------|
| List Tables | GET | `/table` | `table.Read` |
| Read Rows | GET | `/table/{tableName}` | `table.Read` |
| Read Single Row | GET | `/table/{tableName}('{key}')` | `table.Read` |
| Create Row | POST | `/table/{tableName}` | `table.Write` |
| Update Row | PATCH | `/table/{tableName}('{key}')` | `table.Write` |
| Delete Row | DELETE | `/table/{tableName}('{key}')` | `table.Write` |

### Our API Endpoints (FastAPI)

| Operation | HTTP Method | Our Endpoint | Description |
|-----------|-------------|--------------|-------------|
| List Tables | GET | `/tables` | List all accessible tables |
| Read Rows | GET | `/tables/{tableName}` | Get rows from table (paginated) |
| Read Single Row | GET | `/tables/{tableName}/{key}` | Get single row by key |
| Create Row | POST | `/tables/{tableName}` | Create new row |
| Update Row | PATCH | `/tables/{tableName}/{key}` | Update existing row |
| Upsert Row | PUT | `/tables/{tableName}/{key}` | Create or update row |
| Delete Row | DELETE | `/tables/{tableName}/{key}` | Delete row by key |

## Request/Response Examples

### List Tables
```http
GET /tables
Authorization: Cookie session_token={TOKEN}

Response 200:
{
  "tables": [
    {"name": "Customers", "displayName": "Customer Database"},
    {"name": "Orders", "displayName": "Order Tracking"}
  ]
}
```

### Read Table Rows
```http
GET /tables/Customers?limit=50&offset=0
Authorization: Cookie session_token={TOKEN}

Response 200:
{
  "rows": [
    {"CustomerID": "001", "Name": "Acme Corp", "Email": "contact@acme.com"},
    {"CustomerID": "002", "Name": "Initech", "Email": "info@initech.com"}
  ],
  "total": 127,
  "limit": 50,
  "offset": 0
}
```

### Create Row
```http
POST /tables/Customers
Content-Type: application/json
Authorization: Cookie session_token={TOKEN}

Body:
{
  "CustomerID": "003",
  "Name": "Umbrella Corp",
  "Email": "contact@umbrella.com"
}

Response 201:
{
  "CustomerID": "003",
  "Name": "Umbrella Corp",
  "Email": "contact@umbrella.com"
}
```

### Update Row
```http
PATCH /tables/Customers/003
Content-Type: application/json
Authorization: Cookie session_token={TOKEN}

Body:
{
  "Email": "new-email@umbrella.com"
}

Response 200:
{
  "CustomerID": "003",
  "Name": "Umbrella Corp",
  "Email": "new-email@umbrella.com"
}
```

### Delete Row
```http
DELETE /tables/Customers/003
Authorization: Cookie session_token={TOKEN}

Response 204 No Content
```

## Error Handling

| Status Code | Meaning | Response |
|-------------|---------|----------|
| 400 | Bad Request | Invalid input data, validation failed |
| 401 | Unauthorized | Not authenticated, session expired |
| 403 | Forbidden | Insufficient permissions (missing table.Write scope) |
| 404 | Not Found | Table or row doesn't exist |
| 409 | Conflict | Duplicate key on create |
| 500 | Internal Server Error | Unexpected error, check logs |

## Pagination

For large tables, pagination is required:

```http
GET /tables/LargeTable?limit=100&offset=200

Query Parameters:
- limit: Number of rows per page (default: 50, max: 1000)
- offset: Number of rows to skip (default: 0)
```

## Filtering & Sorting (Future Enhancement)

Phase 2 will add OData query parameters:

```http
GET /tables/Customers?$filter=Name eq 'Acme'&$orderby=CustomerID desc
```

## Related Documentation

- [STATUS.md](STATUS.md) - Feature status
- [TODO.md](TODO.md) - Implementation tasks
- [API_DESIGN.md](API_DESIGN.md) - Detailed API design
