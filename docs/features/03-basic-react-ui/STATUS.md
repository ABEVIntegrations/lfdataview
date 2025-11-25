# Feature: Basic React UI

**Status:** Complete
**Progress:** 100%
**Phase:** Community Edition
**Priority:** High
**Last Updated:** 2025-11-24

## Summary

Functional React SPA user interface for viewing and managing Laserfiche lookup table data. Provides table browsing, CRUD forms, filtering, CSV import/export, and error handling.

## Completion Checklist

- [x] Planning and design
  - [x] Component structure designed
  - [x] Routing structure implemented

- [x] Implementation
  - [x] Table list page (TablesPage.tsx)
  - [x] Table detail page with data grid (TableDetailPage.tsx)
  - [x] Create row modal
  - [x] Edit row modal
  - [x] Delete confirmation dialog
  - [x] Loading states (CircularProgress)
  - [x] Error displays (Alert components)
  - [x] Navigation/layout (Layout.tsx)
  - [x] Column filtering (exact match + wildcard)
  - [x] CSV export (filtered rows)
  - [x] CSV upload with full-table replace
  - [x] Pagination controls
  - [x] Help dialog for filter syntax

- [x] Testing
  - [x] Manual UI testing
  - [x] End-to-end workflow verified

- [x] Documentation
  - [x] Feature documentation

- [x] Production deployment
  - [x] Optimized build
  - [x] Deployed and operational

## Key Features Delivered

- Browse available tables
- View table data in grid format
- Create new rows via modal form
- Edit existing rows
- Delete rows with confirmation
- Pagination for large tables
- Error messages for failed operations
- Loading indicators
- **_key column handling** - Always displayed first, non-editable
- **Column filters** - Exact match by default, wildcard support with `*`
- **CSV download** - Export filtered data (excludes _key for Laserfiche compatibility)
- **CSV upload with replace** - Replaces all table rows with uploaded CSV data
- **Help dialog** - Instructions for filter syntax

## Component Structure

```
frontend/src/
├── pages/
│   ├── TablesPage.tsx           # List of tables
│   ├── TableDetailPage.tsx      # Table rows + CRUD + filtering + CSV
│   ├── LoginPage.tsx            # OAuth login
│   └── CallbackPage.tsx         # OAuth callback handler
├── components/
│   └── Layout.tsx               # App shell (header, nav)
├── services/
│   └── api.ts                   # API client
└── types/
    └── index.ts                 # TypeScript types
```

## CSV Upload Workflow

The CSV upload feature matches Laserfiche's native table management workflow:

1. **Download current table** - Click "Download CSV" to export current data (without _key column)
2. **Modify CSV** - Add, edit, or remove rows in the CSV file
3. **Upload CSV** - Click "Upload CSV" to replace ALL table data with the CSV contents

**Important:** This operation **deletes all existing rows** and replaces them with the uploaded data. A confirmation dialog warns users before proceeding.

## Dependencies

**Depends on:**
- Feature 01: OAuth (auth context, protected routes)
- Feature 02: CRUD API (endpoints to call)

## Related Documentation

- [README.md](README.md) - Feature overview
