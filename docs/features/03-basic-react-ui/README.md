# Feature 03: Basic React UI

**Phase:** 1 - MVP
**Priority:** High
**Status:** 📋 Planned

## Overview

A functional web interface for viewing and managing Laserfiche table data. Built with React, provides intuitive CRUD operations and error handling.

## User Workflows

### 1. View Tables
1. User logs in (Feature 01)
2. Lands on table list page
3. Sees all accessible tables
4. Clicks on a table to view data

### 2. View Table Rows
1. User clicks on a table
2. Table detail page loads
3. Sees rows in table/grid format
4. Can paginate through data
5. Sees loading indicator while fetching

### 3. Create Row
1. User clicks "Add Row" button
2. Form/modal appears
3. User fills in fields
4. Clicks "Save"
5. Row created, table refreshes

### 4. Edit Row
1. User clicks "Edit" on a row
2. Form/modal appears with current values
3. User modifies fields
4. Clicks "Save"
5. Row updated, table refreshes

### 5. Delete Row
1. User clicks "Delete" on a row
2. Confirmation dialog appears
3. User confirms
4. Row deleted, table refreshes

## Component Structure

```
src/
├── pages/
│   ├── TablesPage.tsx           # List of tables
│   ├── TableDetailPage.tsx      # Table rows + CRUD actions
│   ├── LoginPage.tsx            # (Feature 01)
│   └── CallbackPage.tsx         # (Feature 01)
│
├── components/
│   ├── Layout.tsx               # App shell (header, nav, footer)
│   ├── TableList.tsx            # Table list grid
│   ├── TableDataGrid.tsx        # Data grid for rows
│   ├── CreateRowModal.tsx       # Create row form
│   ├── EditRowModal.tsx         # Edit row form
│   ├── DeleteConfirmDialog.tsx  # Delete confirmation
│   ├── Pagination.tsx           # Pagination controls
│   ├── ErrorMessage.tsx         # Error display
│   └── LoadingSpinner.tsx       # Loading indicator
│
├── hooks/
│   ├── useAuth.ts               # (Feature 01)
│   ├── useTables.ts             # Fetch tables
│   └── useTableData.ts          # Fetch/mutate table rows
│
└── services/
    └── api.ts                   # API client (Feature 01 + Feature 02 endpoints)
```

## UI Components (MVP)

### Tables Page
- Header: "Laserfiche Table Viewer"
- Table grid showing:
  - Table name
  - Display name (if available)
  - Click to view data
- Loading spinner while fetching
- Error message if fetch fails

### Table Detail Page
- Header: Table name
- Action buttons:
  - "Add Row" (opens create modal)
  - "Refresh" (reload data)
  - "Download CSV" (exports filtered data)
- Data grid:
  - Columns: Dynamic based on table schema
  - **`_key` column is always displayed first** (leftmost position)
  - **Column filters:** Filter input field below each column header (except `_key`)
  - Rows: Table data (filtered if filters are active)
  - Actions per row: Edit, Delete
- Pagination controls (if > 50 rows)
- Loading indicator
- Error message display

#### Primary Key Behavior
All Laserfiche tables have a `_key` column that serves as the primary key:
- **Always displayed first:** The `_key` column is always shown in the leftmost position
- **Auto-generated:** When creating a new row, the `_key` field is not shown (Laserfiche generates it automatically)
- **Non-editable:** When editing a row, the `_key` field is displayed but disabled (cannot be modified)
- **Used for operations:** Edit and delete operations use the `_key` value to identify the row

#### Column Filtering
Each column (except `_key`) has a filter input field:
- **Case-insensitive:** Filters match regardless of case
- **Exact match by default:** Typing "2" matches only "2", not "102"
- **Wildcard support:** Use `*` for fuzzy matching:
  - `*2*` = contains "2"
  - `2*` = starts with "2"
  - `*2` = ends with "2"
  - `*val*` = contains "val"
- **Multiple filters:** Filters can be applied to multiple columns simultaneously (AND logic)
- **Empty state:** Shows "No rows match the filter" when filters exclude all rows

#### CSV Export
The "Download CSV" button exports the currently displayed data:
- **Exports filtered data:** Only rows matching the current filters are exported
- **Includes all columns:** All columns including `_key` are exported
- **Proper CSV formatting:** Values with commas, quotes, or newlines are properly escaped
- **Filename format:** `{tableName}_{date}.csv` (e.g., `Holidays_2025-11-19.csv`)
- **Disabled when empty:** Button is disabled when no rows to export

### Create/Edit Modal
- Form fields (dynamic based on table columns)
- "Save" and "Cancel" buttons
- Validation errors displayed
- Loading state during save

### Delete Confirmation
- "Are you sure you want to delete this row?"
- Row details shown
- "Delete" and "Cancel" buttons

## Routing

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | TablesPage | List of tables (default after login) |
| `/login` | LoginPage | Login page (Feature 01) |
| `/auth/callback` | CallbackPage | OAuth callback (Feature 01) |
| `/tables/:tableName` | TableDetailPage | Table data and CRUD operations |

## State Management

Use React Query (@tanstack/react-query) for server state:

```typescript
// Fetch tables
const { data: tables, isLoading, error } = useQuery({
  queryKey: ['tables'],
  queryFn: fetchTables
});

// Fetch table rows
const { data: rows } = useQuery({
  queryKey: ['table', tableName, page],
  queryFn: () => fetchTableRows(tableName, page)
});

// Mutations
const createMutation = useMutation({
  mutationFn: createRow,
  onSuccess: () => queryClient.invalidateQueries(['table', tableName])
});
```

## Error Handling

- **Network errors:** "Failed to connect. Please check your internet connection."
- **401 Unauthorized:** Redirect to login
- **403 Forbidden:** "You don't have permission to perform this action."
- **404 Not Found:** "Table or row not found."
- **500 Server Error:** "Something went wrong. Please try again later."

## Styling

Options (to be decided during implementation):
1. **Material-UI (MUI):** Pre-built components, consistent design
2. **Ant Design:** Enterprise-grade components
3. **Chakra UI:** Accessible, composable components
4. **Custom CSS + TailwindCSS:** Full control, smaller bundle

**Recommendation:** Material-UI for rapid MVP development.

## Related Documentation

- [STATUS.md](STATUS.md)
- [TODO.md](TODO.md)
