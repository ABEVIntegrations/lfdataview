# LF DataView - Application Overview

## What is LF DataView?

LF DataView is a web application for managing Laserfiche Cloud lookup tables. It provides a user-friendly interface for viewing, editing, and bulk-managing table data that would otherwise require direct access to Laserfiche administration tools.

## Key Capabilities

### Data Management
- **View Tables** - Browse all accessible Laserfiche lookup tables
- **CRUD Operations** - Create, read, update, and delete individual rows
- **Bulk Replace** - Upload CSV files to replace entire table contents
- **CSV Export** - Download table data (with filters applied) as CSV

### User Experience
- **Column Filtering** - Filter data with exact match or wildcard patterns
- **Pagination** - Navigate large tables efficiently
- **Inline Editing** - Edit rows directly in a modal dialog
- **Primary Key Protection** - The `_key` column is always visible but non-editable

### Security
- **OAuth 2.0 Authentication** - Secure login via Laserfiche Cloud
- **Session Management** - Token refresh and secure cookie handling
- **User Permissions** - Respects Laserfiche table access permissions

## Target Users

- **Laserfiche Administrators** - Managing lookup table data
- **Business Users** - Viewing and updating reference data
- **Data Managers** - Bulk importing/exporting table data
- **Developers** - Building on top of the Laserfiche Table API

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Material-UI, React Query |
| Backend | Python 3.11, FastAPI, Pydantic |
| Authentication | OAuth 2.0 (Laserfiche Cloud) |
| Deployment | Docker, Docker Compose |
| API | Laserfiche OData Table API |

## Current Features

| Feature | Status | Description |
|---------|--------|-------------|
| OAuth Authentication | Complete | Secure login via Laserfiche Cloud |
| Table CRUD Operations | Complete | Full create, read, update, delete support |
| Basic React UI | Complete | Table browsing, filtering, CSV import/export |
| Multi-Tenancy | Planned | Support for multiple Laserfiche accounts |
| Advanced UI | Planned | Sorting, advanced search, bulk operations |
| DigitalOcean Deployment | Planned | One-click cloud deployment |

## Workflow Example

1. **Login** - Authenticate with Laserfiche Cloud credentials
2. **Browse** - View list of available lookup tables
3. **Select** - Open a table to view its data
4. **Filter** - Use column filters to find specific rows
5. **Edit** - Modify individual rows or bulk replace via CSV
6. **Export** - Download filtered data as CSV

## CSV Import/Export Workflow

The application mirrors Laserfiche's native table management:

1. **Download** current table as CSV (excludes `_key` column)
2. **Modify** the CSV file (add, edit, or remove rows)
3. **Upload** the CSV to replace all table data

**Note:** CSV upload replaces ALL existing rows. This is an intentional design matching Laserfiche's behavior.

## Links

- [Architecture](/_core/architecture.md)
- [Tech Stack](/_core/tech_stack.md)
- [API Reference](/_api/API_REFERENCE.md)
- [Docker Deployment](/_deployment/DOCKER.md)
- [Security Analysis](/_security/SECURITY_ANALYSIS.md)

## Quick Start

```bash
# Clone and start with Docker
git clone <repository-url>
cd lfdataview
cp .env.example .env
# Edit .env with your Laserfiche OAuth credentials
docker-compose up -d
```

Access the application at `http://localhost:5173`
