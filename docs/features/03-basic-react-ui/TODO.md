# Feature 03: Basic React UI - TODO

**Last Updated:** 2025-11-18

## Setup

- [ ] Choose UI library (Material-UI, Ant Design, Chakra, or custom)
- [ ] Install dependencies (React Query, UI library, etc.)
- [ ] Set up routing (React Router)

## Pages

### Tables Page
- [ ] Create `TablesPage.tsx`
- [ ] Fetch tables from `/tables` endpoint
- [ ] Display tables in grid/list
- [ ] Add loading state
- [ ] Add error handling
- [ ] Make tables clickable → navigate to table detail

### Table Detail Page
- [ ] Create `TableDetailPage.tsx`
- [ ] Fetch table rows from `/tables/{name}` endpoint
- [ ] Display rows in data grid
- [ ] Add pagination controls
- [ ] Add "Add Row" button
- [ ] Add "Edit" and "Delete" buttons per row
- [ ] Handle loading and error states

## Components

### Layout
- [ ] Create `Layout.tsx`
  - [ ] Header with app name and logout button
  - [ ] Navigation (if needed)
  - [ ] Footer (optional)

### Table Data Grid
- [ ] Create `TableDataGrid.tsx`
  - [ ] Dynamic columns based on table schema
  - [ ] Action buttons (Edit, Delete) per row
  - [ ] Responsive design

### CRUD Modals/Forms
- [ ] Create `CreateRowModal.tsx`
  - [ ] Dynamic form fields
  - [ ] Validation
  - [ ] Submit to `POST /tables/{name}`
  - [ ] Success/error handling
- [ ] Create `EditRowModal.tsx`
  - [ ] Pre-fill with current values
  - [ ] Submit to `PATCH /tables/{name}/{key}`
- [ ] Create `DeleteConfirmDialog.tsx`
  - [ ] Show row details
  - [ ] Confirm/cancel buttons
  - [ ] Submit to `DELETE /tables/{name}/{key}`

### UI Elements
- [ ] Create `Pagination.tsx` (prev/next, page numbers)
- [ ] Create `LoadingSpinner.tsx`
- [ ] Create `ErrorMessage.tsx`

## Hooks

- [ ] Create `hooks/useTables.ts` (fetch tables with React Query)
- [ ] Create `hooks/useTableData.ts` (fetch/mutate rows with React Query)

## API Integration

- [ ] Extend `services/api.ts` with table endpoints
  - [ ] `fetchTables()`
  - [ ] `fetchTableRows(tableName, limit, offset)`
  - [ ] `createRow(tableName, data)`
  - [ ] `updateRow(tableName, key, data)`
  - [ ] `deleteRow(tableName, key)`

## Routing

- [ ] Update `src/router.tsx`
  - [ ] Route: `/` → TablesPage (protected)
  - [ ] Route: `/tables/:tableName` → TableDetailPage (protected)
  - [ ] Wrap routes with ProtectedRoute component

## Testing

- [ ] Test TablesList component
- [ ] Test TableDetail component
- [ ] Test CRUD modals
- [ ] Manual testing with real tables

## Polish

- [ ] Responsive design (mobile-friendly)
- [ ] Accessible (keyboard navigation, ARIA labels)
- [ ] Loading skeletons (optional, nice-to-have)
- [ ] Toast notifications for success/error (optional)
