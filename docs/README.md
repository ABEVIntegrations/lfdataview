# LF DataView - Documentation

**Last Updated:** 2025-11-24

A web application for managing Laserfiche Cloud lookup tables via OAuth 2.0 and OData Table API.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [00-RESUME-HERE.md](00-RESUME-HERE.md) | Current status, next steps |
| [OVERVIEW.md](OVERVIEW.md) | What the app does |
| [_planning/PRODUCT_STRATEGY.md](_planning/PRODUCT_STRATEGY.md) | Two-tier product plan |
| [_deployment/SELF_HOSTING_GUIDE.md](_deployment/SELF_HOSTING_GUIDE.md) | How to deploy |

---

## Product Editions

| Edition | Description | Status |
|---------|-------------|--------|
| **Community** | Free, self-hosted, single-tenant | MVP Complete |
| **Managed** | Paid SaaS, multi-tenant | Planned |

See [PRODUCT_STRATEGY.md](_planning/PRODUCT_STRATEGY.md) for details.

---

## Feature Status

| # | Feature | Status | Edition |
|---|---------|--------|---------|
| 01 | [OAuth Authentication](features/01-oauth-authentication/) | Complete | Community |
| 02 | [Table CRUD Operations](features/02-table-crud-operations/) | Complete | Community |
| 03 | [Basic React UI](features/03-basic-react-ui/) | Complete | Community |
| 04 | [Multi-Tenancy](features/04-multi-tenancy/) | Planned | Managed |
| 05 | [Advanced UI](features/05-advanced-ui/) | Planned | Managed |
| 06 | [CapRover Deployment](features/06-digitalocean-deployment/) | Planned | Managed |

---

## Documentation Structure

```
docs/
├── 00-RESUME-HERE.md          <- Start here
├── OVERVIEW.md                 <- App capabilities
├── README.md                   <- You are here
│
├── _planning/
│   └── PRODUCT_STRATEGY.md    <- Two-tier product plan
│
├── _core/
│   ├── architecture.md        <- System design
│   ├── data_models.md         <- Database schema
│   └── tech_stack.md          <- Technology choices
│
├── _security/
│   └── SECURITY_ANALYSIS.md   <- Security considerations
│
├── _deployment/
│   ├── DOCKER.md              <- Local dev setup
│   └── SELF_HOSTING_GUIDE.md  <- Production deployment
│
├── _api/
│   └── API_REFERENCE.md       <- API endpoints
│
└── features/
    ├── 01-oauth-authentication/   [Complete]
    ├── 02-table-crud-operations/  [Complete]
    ├── 03-basic-react-ui/         [Complete]
    ├── 04-multi-tenancy/          [Planned - Managed]
    ├── 05-advanced-ui/            [Planned - Managed]
    └── 06-digitalocean-deployment/ [Planned - Managed]
```

---

## By Role

### Developer
1. [_core/architecture.md](_core/architecture.md) - System design
2. [_api/API_REFERENCE.md](_api/API_REFERENCE.md) - API endpoints
3. Feature folders for implementation details

### Self-Hoster (Community Edition)
1. [_deployment/SELF_HOSTING_GUIDE.md](_deployment/SELF_HOSTING_GUIDE.md) - Deployment guide
2. [_security/SECURITY_ANALYSIS.md](_security/SECURITY_ANALYSIS.md) - Security setup

### Project Manager
1. [00-RESUME-HERE.md](00-RESUME-HERE.md) - Current status
2. [_planning/PRODUCT_STRATEGY.md](_planning/PRODUCT_STRATEGY.md) - Product roadmap

---

## External Resources

### Laserfiche Documentation
- [Laserfiche Developer Console](https://developers.laserfiche.com/)
- [OAuth 2.0 Guide](https://developers.laserfiche.com/guides/guide_oauth-2.0-authorization.html)
- [OData Table API](https://developers.laserfiche.com/guides/guide_odata-table-api.html)

### Technology Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Material-UI](https://mui.com/)
