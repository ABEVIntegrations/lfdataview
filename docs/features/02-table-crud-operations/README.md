# Feature 02: Table Read Operations (Community Edition)

**Phase:** 1 - MVP
**Priority:** Critical
**Status:** Complete
**Edition:** Community Edition (Read-Only)

## Overview

This feature wraps the Laserfiche OData Table API to provide read operations on lookup table data. The FastAPI backend acts as a proxy between the React frontend and Laserfiche, adding authentication, error handling, and data transformation.

**Note:** The Community Edition is read-only. For write operations (Create, Update, Delete), see LFDataView Managed.

## OData Table API Operations

### Base URL
`https://api.laserfiche.com/odata4`

### Supported Operations (Community Edition)

| Operation | HTTP Method | Laserfiche Endpoint | Required Scope |
|-----------|-------------|---------------------|----------------|
| List Tables | GET | `/table` | `table.Read` |
| Read Rows | GET | `/table/{tableName}` | `table.Read` |
| Read Single Row | GET | `/table/{tableName}('{key}')` | `table.Read` |
| Get Row Count | GET | `/table/{tableName}?$apply=aggregate($count as rowCount)` | `table.Read` |
| Get Schema | GET | `/table/$metadata` | `table.Read` |

### Our API Endpoints (FastAPI)

| Operation | HTTP Method | Our Endpoint | Description |
|-----------|-------------|--------------|-------------|
| List Tables | GET | `/tables` | List all accessible tables |
| Read Rows | GET | `/tables/{tableName}` | Get rows from table (paginated, filtered) |
| Read Single Row | GET | `/tables/{tableName}/{key}` | Get single row by key |
| Get Row Count | GET | `/tables/{tableName}/count` | Get total row count |
| Get Schema | GET | `/tables/{tableName}/schema` | Get table column definitions |

## Request/Response Examples

### List Tables
```http
GET /tables
Authorization: Cookie lf_token={ENCRYPTED_TOKEN}

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
Authorization: Cookie lf_token={ENCRYPTED_TOKEN}

Response 200:
{
  "rows": [
    {"_key": "1", "CustomerID": "001", "Name": "Acme Corp", "Email": "contact@acme.com"},
    {"_key": "2", "CustomerID": "002", "Name": "Initech", "Email": "info@initech.com"}
  ],
  "total": 127,
  "limit": 50,
  "offset": 0
}
```

### Read Rows with Filtering
```http
GET /tables/Customers?filters={"Name":"Acme"}&filter_mode=and
Authorization: Cookie lf_token={ENCRYPTED_TOKEN}

Response 200:
{
  "rows": [
    {"_key": "1", "CustomerID": "001", "Name": "Acme Corp", "Email": "contact@acme.com"}
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### Get Row Count
```http
GET /tables/Customers/count
Authorization: Cookie lf_token={ENCRYPTED_TOKEN}

Response 200:
{
  "table_name": "Customers",
  "row_count": 127
}
```

### Get Table Schema
```http
GET /tables/Customers/schema
Authorization: Cookie lf_token={ENCRYPTED_TOKEN}

Response 200:
{
  "table_name": "Customers",
  "columns": [
    {"name": "_key", "type": "Edm.String", "required": true},
    {"name": "CustomerID", "type": "Edm.String", "required": false},
    {"name": "Name", "type": "Edm.String", "required": false},
    {"name": "Email", "type": "Edm.String", "required": false}
  ]
}
```

## Error Handling

| Status Code | Meaning | Response |
|-------------|---------|----------|
| 400 | Bad Request | Invalid query parameters |
| 401 | Unauthorized | Not authenticated, session expired |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Table or row doesn't exist |
| 500 | Internal Server Error | Unexpected error, check logs |

## Pagination

For large tables, pagination is required:

```http
GET /tables/LargeTable?limit=100&offset=200

Query Parameters:
- limit: Number of rows per page (default: 50, max: 1000)
- offset: Number of rows to skip (default: 0)
```

## Filtering

Server-side filtering is supported with exact match:

```http
GET /tables/Customers?filters={"Status":"Active"}&filter_mode=and

Query Parameters:
- filters: JSON-encoded filter object
- filter_mode: "and" (all must match) or "or" (any must match)
```

## Related Documentation

- [STATUS.md](STATUS.md) - Feature status
- [TODO.md](TODO.md) - Implementation tasks
- [API_DESIGN.md](API_DESIGN.md) - Detailed API design
