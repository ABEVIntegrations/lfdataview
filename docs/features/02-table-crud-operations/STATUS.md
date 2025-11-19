# Feature: Table CRUD Operations

**Status:** ⚠️ IMPLEMENTED - NEEDS TESTING
**Progress:** 95%
**Phase:** Phase 1 - MVP
**Priority:** Critical
**Last Updated:** 2025-11-19

## Summary

Implement complete CRUD (Create, Read, Update, Delete) operations for Laserfiche lookup tables using the OData Table API. This feature provides the core functionality of the application: viewing, creating, updating, and deleting table data.

## Completion Checklist

- [x] Planning and design
  - [x] OData API operations documented
  - [x] FastAPI endpoint design completed
  - [x] Error handling strategy defined

- [x] Implementation
  - [x] FastAPI endpoints for table operations (6 endpoints)
  - [x] Laserfiche OData API wrapper functions (6 methods)
  - [x] Pagination support (limit/offset with $top/$skip)
  - [x] Error handling and transformation (httpx errors → HTTPException)
  - [x] Request validation with Pydantic (7 schemas)

- [ ] Testing (Needs User Testing)
  - [ ] Manual testing with real Laserfiche tables
  - [ ] Verify all CRUD operations work
  - [ ] Test pagination
  - [ ] Test error scenarios

- [x] Documentation
  - [x] Feature documentation
  - [x] API documentation (OpenAPI auto-generated)
  - [x] Code documentation (docstrings)
  - [x] Test guide created (FEATURE_02_TEST_GUIDE.md)

- [ ] Production deployment
  - [ ] Backend restart required
  - [ ] User testing needed
  - [ ] Mark as complete after testing

## Key Features Delivered

- ✅ List all accessible tables
- ✅ Read table rows with pagination (limit/offset)
- ✅ Read single row by key
- ✅ Create new table rows
- ✅ Update existing table rows (PATCH)
- ✅ Delete table rows
- ✅ Authentication required for all endpoints
- ✅ Automatic token refresh
- ✅ Error handling for all scenarios (401, 403, 404, 409, 500)

## Implementation Details

### Backend Components

**Extended Laserfiche Client** (`backend/app/utils/laserfiche.py`)
- Added 6 OData Table API methods
- Proper OAuth Bearer token authentication
- OData query parameter support ($top, $skip, $count)
- Full error propagation

**Pydantic Schemas** (`backend/app/schemas/table.py`)
- `TableInfo` - Table metadata structure
- `TableListResponse` - List endpoint response
- `TableRowsResponse` - Paginated rows response
- `CreateRowRequest` - Row creation validation
- `UpdateRowRequest` - Row update validation
- `RowResponse` - Single row response
- `ErrorResponse` - Standard error format

**API Endpoints** (`backend/app/routers/tables.py`)
1. `GET /tables` - List all tables
2. `GET /tables/{table_name}` - Get rows (paginated)
3. `GET /tables/{table_name}/{key}` - Get single row
4. `POST /tables/{table_name}` - Create row
5. `PATCH /tables/{table_name}/{key}` - Update row
6. `DELETE /tables/{table_name}/{key}` - Delete row

**Authentication** (`backend/app/dependencies.py`)
- Added `get_user_access_token()` dependency
- Automatically refreshes expired tokens
- Returns decrypted access token for API calls

**Router Registration** (`backend/app/main.py`)
- Tables router registered with `/tables` prefix
- Auto-generated OpenAPI documentation

### API Features

- **Pagination:** Query parameters `limit` (1-1000) and `offset` (0+)
- **Authentication:** All endpoints require valid session cookie
- **Token Refresh:** Automatic and transparent to user
- **Error Transformation:** Laserfiche errors mapped to HTTP status codes
- **Validation:** Pydantic models validate all requests
- **Documentation:** Auto-generated Swagger UI at `/docs`

## Next Steps

1. **Restart Backend:** `docker restart lfdataview-backend`
2. **Test Endpoints:** Follow [FEATURE_02_TEST_GUIDE.md](../../../FEATURE_02_TEST_GUIDE.md)
3. **Verify CRUD Operations:** Test with real Laserfiche tables
4. **Mark Complete:** Update status once testing passes

## Dependencies

**Blocks:** Feature 03 (UI needs these endpoints)

**Depends on:** Feature 01 (OAuth authentication required)

## Related Documentation

- [README.md](README.md) - Feature overview
- [TODO.md](TODO.md) - Task breakdown
- [API_DESIGN.md](API_DESIGN.md) - Endpoint specifications
