# LFDataView Community Edition - Application Overview

**Last Updated:** 2025-12-09
**Version:** 1.0 (Community Edition)

## What is LFDataView?

LFDataView Community Edition is a free, open-source web application for viewing Laserfiche Cloud lookup tables. It provides a user-friendly interface for browsing and searching table data that would otherwise require direct access to Laserfiche administration tools.

**Key Design:** The Community Edition is read-only with stateless authentication and no database required.

## Key Capabilities

### Data Viewing
- **View Tables** - Browse all accessible Laserfiche lookup tables
- **Read Data** - View table rows with pagination (beyond Laserfiche UI limits)
- **CSV Export** - Download table data (with filters applied) as CSV

### User Experience
- **Server-Side Search** - Exact match search across columns
- **Column Filtering** - Client-side filtering with partial match support
- **Pagination** - Navigate large tables efficiently
- **Primary Key Visibility** - The `_key` column is hidden (internal system field)

### Security
- **OAuth 2.0 Authentication** - Secure login via Laserfiche Cloud
- **Encrypted Cookies** - Tokens encrypted with Fernet before storage
- **User Permissions** - Respects Laserfiche table access permissions

## Target Users

- **Laserfiche Administrators** - Viewing lookup table data
- **Business Users** - Browsing and searching reference data
- **Data Analysts** - Exporting table data for analysis
- **Developers** - Exploring the Laserfiche Table API

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Material-UI, React Query |
| Backend | Python 3.11, FastAPI, Pydantic |
| Authentication | OAuth 2.0 (Laserfiche Cloud), Stateless cookies |
| Deployment | Docker, Docker Compose |
| API | Laserfiche OData Table API |

## Product Editions

| Feature | Community Edition | Managed Edition |
|---------|-------------------|-----------------|
| View tables | Yes | Yes |
| Search & filter | Yes | Yes |
| Pagination | Yes | Yes |
| CSV export | Yes | Yes |
| Add/Edit/Delete rows | No | Yes |
| CSV import | No | Yes |
| Bulk operations | No | Yes |
| Caching | No | Yes |
| Notifications | No | Yes |
| Support | Community | Professional |

## Current Features (Community Edition)

| Feature | Status | Description |
|---------|--------|-------------|
| OAuth Authentication | Complete | Secure login via Laserfiche Cloud |
| Table Read Operations | Complete | View tables, rows, and metadata |
| Search & Filtering | Complete | Server-side and client-side filtering |
| CSV Export | Complete | Download filtered data as CSV |

## Workflow Example

1. **Login** - Authenticate with Laserfiche Cloud credentials
2. **Browse** - View list of available lookup tables
3. **Select** - Open a table to view its data
4. **Search** - Use server-side search for exact matches
5. **Filter** - Use column filters for partial matching on displayed rows
6. **Export** - Download filtered data as CSV

## Links

- [Architecture](_core/architecture.md)
- [Tech Stack](_core/tech_stack.md)
- [API Reference](_api/API_REFERENCE.md)
- [Docker Deployment](_deployment/DOCKER.md)
- [Self-Hosting Guide](_deployment/SELF_HOSTING_GUIDE.md)

## Quick Start

```bash
# Clone and start with Docker
git clone https://github.com/ABEVIntegrations/lfdataview.git
cd lfdataview
cp backend/.env.example backend/.env
# Edit backend/.env with your Laserfiche OAuth credentials
docker-compose up -d
```

Access the application at `http://localhost:3000`
