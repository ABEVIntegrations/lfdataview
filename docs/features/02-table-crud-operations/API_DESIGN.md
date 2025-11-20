# Table CRUD API Design

**Last Updated:** 2025-11-18

## FastAPI Endpoints

All endpoints require authentication (session cookie).

### GET /tables
List all accessible tables.

**Request:**
```http
GET /tables
Cookie: session_token=xxx
```

**Response 200:**
```json
{
  "tables": [
    {"name": "Customers", "displayName": "Customer Database"},
    {"name": "Orders", "displayName": "Order Tracking"}
  ]
}
```

---

### GET /tables/{table_name}
Get rows from a table with pagination.

**Query Parameters:**
- `limit` (optional, default: 50, max: 1000): Number of rows to return
- `offset` (optional, default: 0): Number of rows to skip

**Request:**
```http
GET /tables/Customers?limit=50&offset=0
Cookie: session_token=xxx
```

**Response 200:**
```json
{
  "rows": [
    {"CustomerID": "001", "Name": "Acme Corp"},
    {"CustomerID": "002", "Name": "Initech"}
  ],
  "total": 127,
  "limit": 50,
  "offset": 0
}
```

---

### GET /tables/{table_name}/{key}
Get a single row by primary key.

**Request:**
```http
GET /tables/Customers/001
Cookie: session_token=xxx
```

**Response 200:**
```json
{
  "CustomerID": "001",
  "Name": "Acme Corp",
  "Email": "contact@acme.com"
}
```

**Response 404:**
```json
{
  "detail": "Row not found"
}
```

---

### POST /tables/{table_name}
Create a new row.

**Request:**
```http
POST /tables/Customers
Content-Type: application/json
Cookie: session_token=xxx

{
  "CustomerID": "003",
  "Name": "Umbrella Corp",
  "Email": "contact@umbrella.com"
}
```

**Response 201:**
```json
{
  "CustomerID": "003",
  "Name": "Umbrella Corp",
  "Email": "contact@umbrella.com"
}
```

**Response 409 (Duplicate Key):**
```json
{
  "detail": "Row with this key already exists"
}
```

---

### PATCH /tables/{table_name}/{key}
Update an existing row.

**Request:**
```http
PATCH /tables/Customers/003
Content-Type: application/json
Cookie: session_token=xxx

{
  "Email": "new-email@umbrella.com"
}
```

**Response 200:**
```json
{
  "CustomerID": "003",
  "Name": "Umbrella Corp",
  "Email": "new-email@umbrella.com"
}
```

---

### DELETE /tables/{table_name}/{key}
Delete a row.

**Request:**
```http
DELETE /tables/Customers/003
Cookie: session_token=xxx
```

**Response 204 No Content**

**Response 404:**
```json
{
  "detail": "Row not found"
}
```

---

### GET /tables/{table_name}/schema
Get table column definitions.

**Request:**
```http
GET /tables/Customers/schema
Cookie: session_token=xxx
```

**Response 200:**
```json
{
  "table_name": "Customers",
  "columns": [
    {"name": "_key", "type": "string", "required": true},
    {"name": "Name", "type": "string", "required": true},
    {"name": "Email", "type": "string", "required": false}
  ]
}
```

---

### POST /tables/{table_name}/replace
Replace all rows in a table with new data.

**WARNING:** This deletes ALL existing rows and replaces them with the provided data.

**Request:**
```http
POST /tables/Customers/replace
Content-Type: application/json
Cookie: session_token=xxx

{
  "rows": [
    {"Name": "Acme Corp", "Email": "contact@acme.com"},
    {"Name": "Initech", "Email": "info@initech.com"}
  ]
}
```

**Response 200:**
```json
{
  "success": true,
  "rows_replaced": 2
}
```

**Response 504 (Timeout):**
```json
{
  "detail": "Replace operation timed out after 300 seconds"
}
```

**Notes:**
- The `_key` column should NOT be included in the rows (auto-generated)
- This is an atomic operation using Laserfiche's ReplaceAllRowsAsync
- Operation may timeout for very large datasets (default: 300 seconds)

---

## Error Responses

All endpoints may return:

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions. Requires table.Write scope."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error. Please contact support."
}
```
