# Feature 03: Basic React UI (Community Edition)

**Phase:** 1 - MVP
**Priority:** High
**Status:** Complete
**Edition:** Community Edition (Read-Only)

## Overview

A functional web interface for viewing Laserfiche table data. Built with React and Material-UI, provides intuitive browsing, search, and export capabilities.

**Note:** The Community Edition is read-only. For write operations (Create, Edit, Delete, CSV Import), see LFDataView Managed.

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
5. Sees total row count
6. Sees loading indicator while fetching

### 3. Search and Filter
1. **Server-side search:** Use search bar for exact match queries
2. **Client-side filters:** Use column filters for partial matching on displayed rows
3. Both are case-insensitive

### 4. Export Data
1. User clicks "Download CSV"
2. Currently filtered/displayed rows are exported
3. CSV file downloads with table name and date

## Component Structure

```
src/
├── pages/
│   ├── TablesPage.tsx           # List of tables
│   ├── TableDetailPage.tsx      # Table rows + search/filter/export
│   ├── LoginPage.tsx            # (Feature 01)
│   └── CallbackPage.tsx         # (Feature 01)
│
├── components/
│   ├── Layout.tsx               # App shell (header, nav, footer)
│   └── ...                      # Shared components
│
├── hooks/
│   └── useAuth.ts               # (Feature 01)
│
└── services/
    └── api.ts                   # API client
```

## UI Components (Community Edition)

### Tables Page
- Header: "LFDataView"
- Table grid showing:
  - Table name
  - Display name (if available)
  - Click to view data
- Loading spinner while fetching
- Error message if fetch fails

### Table Detail Page
- Header: Table name with total row count
- Action buttons:
  - "Refresh" (reload data)
  - "Download CSV" (exports filtered data)
  - Help button (usage instructions)
- Search bar:
  - Column selector dropdown
  - Search input field
  - Search and Clear buttons
- Data grid:
  - Columns: Dynamic based on table schema
  - `_key` column is hidden (internal system field)
  - Column filters below each header for partial matching
  - Rows: Table data
- Pagination controls
- Loading indicator
- Error message display

#### Search Bar (Server-Side)
The search bar queries Laserfiche directly:
- **Exact match:** Searches for exact values (case-insensitive)
- **Column selector:** Search a specific column or all columns
- **OR mode:** When searching all columns, any match counts

#### Column Filters (Client-Side)
Filter fields below each column header:
- **Partial matching:** Typing "smith" matches "Smith", "Smithson", "Blacksmith"
- **Case-insensitive:** Matches regardless of case
- **AND logic:** All filters must match
- **Only affects displayed rows:** Works on current page data

#### CSV Export
The "Download CSV" button exports the currently displayed data:
- **Exports filtered data:** Only rows matching the current filters
- **Excludes `_key`:** Internal system field is not exported
- **Proper CSV formatting:** Values are properly escaped
- **Filename format:** `{tableName}_{date}.csv`
- **Disabled when empty:** Button disabled when no rows to export

### Help Dialog
Explains search and filter usage with a note about Community Edition being read-only.

## Routing

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | TablesPage | List of tables (default after login) |
| `/login` | LoginPage | Login page (Feature 01) |
| `/auth/callback` | CallbackPage | OAuth callback (Feature 01) |
| `/tables/:tableName` | TableDetailPage | Table data viewing |

## State Management

Uses React Query (@tanstack/react-query) for server state:

```typescript
// Fetch tables
const { data: tables, isLoading, error } = useQuery({
  queryKey: ['tables'],
  queryFn: fetchTables
});

// Fetch table rows with filters
const { data: rows } = useQuery({
  queryKey: ['tableRows', tableName, page, filters],
  queryFn: () => fetchTableRows(tableName, limit, offset, filters)
});

// Fetch row count
const { data: count } = useQuery({
  queryKey: ['tableRowCount', tableName],
  queryFn: () => fetchTableRowCount(tableName)
});
```

## Error Handling

- **Network errors:** "Failed to connect. Please check your internet connection."
- **401 Unauthorized:** Redirect to login
- **403 Forbidden:** "You don't have permission to access this resource."
- **404 Not Found:** "Table not found."
- **500 Server Error:** "Something went wrong. Please try again later."

## Styling

Built with Material-UI (MUI) for:
- Consistent design system
- Pre-built accessible components
- Responsive layout
- Dark mode support (future)

## Related Documentation

- [STATUS.md](STATUS.md)
- [TODO.md](TODO.md)
