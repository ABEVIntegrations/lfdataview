# Feature 02: Table CRUD Operations - Testing Guide

**Status:** Implementation Complete - Ready for Testing ✅
**Date:** November 19, 2025

---

## What Was Built

### 🎯 Complete Implementation

✅ **Extended Laserfiche API Client** (`backend/app/utils/laserfiche.py`)
- `list_tables()` - List all accessible tables
- `get_table_rows()` - Get paginated rows from a table
- `get_table_row()` - Get single row by key
- `create_table_row()` - Create new row
- `update_table_row()` - Update existing row (PATCH)
- `delete_table_row()` - Delete row

✅ **Created Pydantic Schemas** (`backend/app/schemas/table.py`)
- `TableInfo` - Table metadata
- `TableListResponse` - List of tables response
- `TableRowsResponse` - Paginated rows response
- `CreateRowRequest` - Row creation request
- `UpdateRowRequest` - Row update request
- `RowResponse` - Single row response
- `ErrorResponse` - Error response

✅ **Created API Endpoints** (`backend/app/routers/tables.py`)
- `GET /tables` - List all tables
- `GET /tables/{table_name}` - Get rows with pagination
- `GET /tables/{table_name}/{key}` - Get single row
- `POST /tables/{table_name}` - Create row
- `PATCH /tables/{table_name}/{key}` - Update row
- `DELETE /tables/{table_name}/{key}` - Delete row

✅ **Added Authentication**
- All endpoints require authentication (session cookie)
- Automatic token refresh if expired
- Proper error handling for auth failures

✅ **Registered Router** (`backend/app/main.py`)
- Table router registered with `/tables` prefix

---

## How to Test

### Step 1: Restart Backend Service

The backend needs to be restarted to load the new code.

**PowerShell (Windows):**
```powershell
cd D:\anthony\projects\lfdataview
docker restart lfdataview-backend

# Check logs
docker logs -f lfdataview-backend
```

**Expected Output:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Verify API Documentation

Open your browser to see the new endpoints:

**Swagger UI:** http://localhost:8000/docs

You should see a new "Tables" section with 6 endpoints:
- GET /tables
- GET /tables/{table_name}
- GET /tables/{table_name}/{key}
- POST /tables/{table_name}
- PATCH /tables/{table_name}/{key}
- DELETE /tables/{table_name}/{key}

### Step 3: Authenticate First

Before testing table endpoints, you must be authenticated:

1. Go to: http://localhost:8000/test
2. Click "Login with Laserfiche"
3. Complete OAuth flow
4. Verify you see: "✅ You are authenticated!"

### Step 4: Test Table Endpoints

#### Option A: Using Swagger UI (Easiest)

1. Open http://localhost:8000/docs
2. Click on any endpoint under "Tables"
3. Click "Try it out"
4. Fill in parameters (if needed)
5. Click "Execute"

**Note:** Swagger UI should automatically include your session cookie.

#### Option B: Using cURL

**List Tables:**
```bash
curl -X GET "http://localhost:8000/tables" \
  -H "Cookie: session_token=YOUR_SESSION_TOKEN" \
  -H "accept: application/json"
```

**Get Table Rows:**
```bash
curl -X GET "http://localhost:8000/tables/YourTableName?limit=10&offset=0" \
  -H "Cookie: session_token=YOUR_SESSION_TOKEN" \
  -H "accept: application/json"
```

**Create Row:**
```bash
curl -X POST "http://localhost:8000/tables/YourTableName" \
  -H "Cookie: session_token=YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "Column1": "Value1",
      "Column2": "Value2"
    }
  }'
```

**Update Row:**
```bash
curl -X PATCH "http://localhost:8000/tables/YourTableName/row_key" \
  -H "Cookie: session_token=YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "Column1": "UpdatedValue"
    }
  }'
```

**Delete Row:**
```bash
curl -X DELETE "http://localhost:8000/tables/YourTableName/row_key" \
  -H "Cookie: session_token=YOUR_SESSION_TOKEN"
```

#### Option C: Using Browser Console

Open http://localhost:8000/test and run in console:

```javascript
// List tables
fetch('/tables', {credentials: 'include'})
  .then(r => r.json())
  .then(console.log)

// Get table rows
fetch('/tables/YourTableName?limit=10', {credentials: 'include'})
  .then(r => r.json())
  .then(console.log)

// Create row
fetch('/tables/YourTableName', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    data: {
      Column1: 'Value1',
      Column2: 'Value2'
    }
  })
})
  .then(r => r.json())
  .then(console.log)
```

---

## Expected Responses

### List Tables - Success (200)
```json
{
  "tables": [
    {
      "name": "Customers",
      "displayName": "Customer Database",
      "description": "Customer records"
    },
    {
      "name": "Orders",
      "displayName": "Order Tracking",
      "description": null
    }
  ]
}
```

### Get Table Rows - Success (200)
```json
{
  "rows": [
    {
      "CustomerID": "001",
      "Name": "Acme Corp",
      "Email": "contact@acme.com"
    },
    {
      "CustomerID": "002",
      "Name": "Initech",
      "Email": "info@initech.com"
    }
  ],
  "total": 127,
  "limit": 50,
  "offset": 0
}
```

### Create Row - Success (201)
```json
{
  "data": {
    "CustomerID": "003",
    "Name": "Umbrella Corp",
    "Email": "contact@umbrella.com"
  }
}
```

### Update Row - Success (200)
```json
{
  "data": {
    "CustomerID": "003",
    "Name": "Umbrella Corp",
    "Email": "new-email@umbrella.com"
  }
}
```

### Delete Row - Success (204)
No content returned.

---

## Error Scenarios to Test

### Not Authenticated (401)
```json
{
  "detail": "Not authenticated. Please log in."
}
```

**How to test:** Clear cookies and try any endpoint.

### Insufficient Permissions (403)
```json
{
  "detail": "Insufficient permissions. Check your OAuth scopes."
}
```

**How to test:** Try to create/update/delete without `table.Write` scope.

### Table Not Found (404)
```json
{
  "detail": "Resource not found: Table 'NonExistent' not found"
}
```

**How to test:** Request a table that doesn't exist.

### Row Not Found (404)
```json
{
  "detail": "Resource not found: Row with key 'invalid' not found"
}
```

**How to test:** Request a row with an invalid key.

---

## Troubleshooting

### Issue: "Not authenticated"
**Solution:**
1. Go to http://localhost:8000/test
2. Click "Login with Laserfiche"
3. Complete OAuth flow
4. Try again

### Issue: "Table not found"
**Solution:**
1. First run `GET /tables` to see available tables
2. Use exact table name (case-sensitive)

### Issue: "Insufficient permissions"
**Solution:**
1. Check your Laserfiche app has `table.Read` and `table.Write` scopes
2. Log out and log in again to refresh scopes

### Issue: Connection refused
**Solution:**
1. Check backend is running: `docker ps`
2. Restart if needed: `docker restart lfdataview-backend`
3. Check logs: `docker logs lfdataview-backend`

---

## Testing Checklist

Use this checklist to verify all functionality:

- [ ] **Authentication**
  - [ ] Can authenticate via OAuth
  - [ ] Session persists across requests

- [ ] **List Tables**
  - [ ] Returns list of tables
  - [ ] Requires authentication

- [ ] **Get Table Rows**
  - [ ] Returns rows with pagination
  - [ ] Pagination works (limit/offset)
  - [ ] Total count is accurate

- [ ] **Get Single Row**
  - [ ] Returns correct row data
  - [ ] Returns 404 for invalid key

- [ ] **Create Row**
  - [ ] Creates new row successfully
  - [ ] Returns created row data
  - [ ] Requires table.Write scope

- [ ] **Update Row**
  - [ ] Updates existing row
  - [ ] Partial update works (PATCH)
  - [ ] Returns updated row data

- [ ] **Delete Row**
  - [ ] Deletes row successfully
  - [ ] Returns 204 No Content
  - [ ] Row is actually deleted (verify with GET)

- [ ] **Error Handling**
  - [ ] 401 when not authenticated
  - [ ] 403 when insufficient permissions
  - [ ] 404 when table/row not found
  - [ ] Proper error messages

---

## Next Steps After Testing

Once all endpoints are verified:

1. ✅ Mark Feature 02 as COMPLETE
2. ✅ Update documentation
3. ✅ Celebrate! 🎉
4. 🚀 Move to Feature 03: Basic React UI

---

## Quick Commands

```powershell
# Restart backend
docker restart lfdataview-backend

# View logs
docker logs -f lfdataview-backend

# Check status
docker ps

# Test authentication
curl http://localhost:8000/auth/status

# Test table list
curl http://localhost:8000/tables -H "Cookie: session_token=YOUR_TOKEN"
```

---

**Ready to test!** 🚀

Start with Step 1 above and work through the testing checklist.
