# Feature 02: Table CRUD Operations - TODO

**Last Updated:** 2025-11-18

## Backend Implementation

### Laserfiche OData Client
- [ ] Extend `utils/laserfiche.py` with table methods
  - [ ] `list_tables(access_token: str) -> List[Dict]`
  - [ ] `get_table_rows(access_token, table_name, limit, offset) -> Dict`
  - [ ] `get_table_row(access_token, table_name, key) -> Dict`
  - [ ] `create_table_row(access_token, table_name, data) -> Dict`
  - [ ] `update_table_row(access_token, table_name, key, data) -> Dict`
  - [ ] `delete_table_row(access_token, table_name, key) -> None`

### Pydantic Schemas
- [ ] Create `schemas/table.py`
  - [ ] `TableListResponse` - List of tables
  - [ ] `TableRowsResponse` - Paginated rows
  - [ ] `CreateRowRequest` - Generic row creation
  - [ ] `UpdateRowRequest` - Generic row update

### API Endpoints
- [ ] Create `routers/tables.py`
  - [ ] `GET /tables` - List all tables
  - [ ] `GET /tables/{table_name}` - Get rows (with pagination)
  - [ ] `GET /tables/{table_name}/{key}` - Get single row
  - [ ] `POST /tables/{table_name}` - Create row
  - [ ] `PATCH /tables/{table_name}/{key}` - Update row
  - [ ] `DELETE /tables/{table_name}/{key}` - Delete row

### Error Handling
- [ ] Transform Laserfiche API errors to user-friendly messages
- [ ] Handle 403 errors (insufficient permissions)
- [ ] Handle 404 errors (table/row not found)
- [ ] Handle validation errors (invalid data)

### Testing
- [ ] Unit tests for all endpoints
- [ ] Mock Laserfiche API responses
- [ ] Test pagination logic
- [ ] Test error scenarios

## Documentation
- [x] STATUS.md
- [x] README.md
- [x] TODO.md
- [ ] API_DESIGN.md (detailed endpoint specs)
