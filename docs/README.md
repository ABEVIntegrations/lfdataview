# Laserfiche Data View - Documentation

**Welcome to the Laserfiche Data View documentation!**

This application provides a web interface for viewing and managing Laserfiche lookup table data using OAuth 2.0 authentication and the OData Table API.

---

## 🎯 Start Here

**New to this project?** Start with these documents in order:

1. **[00-RESUME-HERE.md](00-RESUME-HERE.md)** - Current project status, where to begin
2. **[Architecture Overview](_core/architecture.md)** - System design and tech stack
3. **[Feature 01: OAuth Authentication](features/01-oauth-authentication/)** - First feature to implement

**Returning to the project?** Go directly to:
- **[00-RESUME-HERE.md](00-RESUME-HERE.md)** - Pick up where you left off

---

## 📁 Documentation Structure

```
docs/
├── 00-RESUME-HERE.md          ← 🎯 START HERE (current status, resumption guide)
├── README.md                   ← 📖 YOU ARE HERE (navigation guide)
│
├── _core/                      ← Core technical documentation
│   ├── architecture.md         → System architecture, tech stack
│   ├── data_models.md          → Database schema, data structures
│   └── tech_stack.md           → Technology choices and rationale
│
├── _security/                  ← Security documentation
│   └── SECURITY_ANALYSIS.md    → OAuth, CSRF, secrets, CORS, encryption
│
├── _deployment/                ← Deployment guides
│   ├── DOCKER.md               → Docker Compose development setup
│   └── SELF_HOSTING_GUIDE.md   → Single-tenant installation guide
│
├── _api/                       ← API documentation
│   └── API_REFERENCE.md        → FastAPI endpoint specifications
│
├── _testing/                   ← Testing documentation
│   └── TESTING_STRATEGY.md     → Test approach, tools, coverage
│
├── _planning/                  ← Project planning
│   └── TODO.md                 → Project-wide tasks and roadmap
│
└── features/                   ← 🎯 Feature-specific documentation
    ├── 01-oauth-authentication/      [📋 PLANNED - Phase 1 - Critical]
    │   ├── STATUS.md           → Feature status at a glance
    │   ├── TODO.md             → Detailed task breakdown
    │   ├── README.md           → Feature overview
    │   └── IMPLEMENTATION_PLAN.md → Technical implementation details
    │
    ├── 02-table-crud-operations/     [📋 PLANNED - Phase 1 - Critical]
    │   ├── STATUS.md
    │   ├── TODO.md
    │   ├── README.md
    │   └── API_DESIGN.md       → Endpoint design for CRUD operations
    │
    ├── 03-basic-react-ui/            [📋 PLANNED - Phase 1 - High]
    │   ├── STATUS.md
    │   ├── TODO.md
    │   └── README.md
    │
    ├── 04-multi-tenancy/             [📋 PLANNED - Phase 2 - Medium]
    │   ├── STATUS.md
    │   ├── TODO.md
    │   └── README.md
    │
    └── 05-advanced-ui/               [📋 PLANNED - Phase 3 - Low]
        ├── STATUS.md
        ├── TODO.md
        └── README.md
```

---

## 📊 Feature Status Table

| # | Feature | Status | Progress | Phase | Priority | Docs Link |
|---|---------|--------|----------|-------|----------|-----------|
| 01 | OAuth Authentication | 📋 PLANNED | 0% | Phase 1 | Critical | [View](features/01-oauth-authentication/) |
| 02 | Table CRUD Operations | 📋 PLANNED | 0% | Phase 1 | Critical | [View](features/02-table-crud-operations/) |
| 03 | Basic React UI | 📋 PLANNED | 0% | Phase 1 | High | [View](features/03-basic-react-ui/) |
| 04 | Multi-Tenancy | 📋 PLANNED | 0% | Phase 2 | Medium | [View](features/04-multi-tenancy/) |
| 05 | Advanced UI Features | 📋 PLANNED | 0% | Phase 3 | Low | [View](features/05-advanced-ui/) |

**Overall Project Status:** ~0% Complete (Planning phase)

---

## 🔍 Finding Documentation

### By Task

- **"I want to understand the system"** → [_core/architecture.md](_core/architecture.md)
- **"I want to implement authentication"** → [features/01-oauth-authentication/](features/01-oauth-authentication/)
- **"I want to implement CRUD operations"** → [features/02-table-crud-operations/](features/02-table-crud-operations/)
- **"I want to build the UI"** → [features/03-basic-react-ui/](features/03-basic-react-ui/)
- **"I want to deploy this"** → [_deployment/SELF_HOSTING_GUIDE.md](_deployment/SELF_HOSTING_GUIDE.md)
- **"I want to set up local dev"** → [_deployment/DOCKER.md](_deployment/DOCKER.md)
- **"I want to understand security"** → [_security/SECURITY_ANALYSIS.md](_security/SECURITY_ANALYSIS.md)
- **"I want to see the API endpoints"** → [_api/API_REFERENCE.md](_api/API_REFERENCE.md)
- **"I want to know what's next"** → [00-RESUME-HERE.md](00-RESUME-HERE.md)

### By Role

**Developer (Backend):**
1. [_core/architecture.md](_core/architecture.md) - Understand system design
2. [features/01-oauth-authentication/](features/01-oauth-authentication/) - Implement OAuth
3. [features/02-table-crud-operations/](features/02-table-crud-operations/) - Implement CRUD API
4. [_api/API_REFERENCE.md](_api/API_REFERENCE.md) - API endpoint specs
5. [_testing/TESTING_STRATEGY.md](_testing/TESTING_STRATEGY.md) - Test approach

**Developer (Frontend):**
1. [_core/architecture.md](_core/architecture.md) - Understand system design
2. [features/03-basic-react-ui/](features/03-basic-react-ui/) - Build UI
3. [_api/API_REFERENCE.md](_api/API_REFERENCE.md) - Backend API to consume

**DevOps/Infrastructure:**
1. [_deployment/DOCKER.md](_deployment/DOCKER.md) - Local dev setup
2. [_deployment/SELF_HOSTING_GUIDE.md](_deployment/SELF_HOSTING_GUIDE.md) - Production deployment
3. [_security/SECURITY_ANALYSIS.md](_security/SECURITY_ANALYSIS.md) - Security requirements

**Project Manager:**
1. [00-RESUME-HERE.md](00-RESUME-HERE.md) - Current status
2. Feature folders - Individual feature status via STATUS.md files

---

## 🚀 Quick Start Guides

### For Developers Starting Work

1. Read [00-RESUME-HERE.md](00-RESUME-HERE.md) for current status
2. Review [_core/architecture.md](_core/architecture.md) to understand the system
3. Set up local environment using [_deployment/DOCKER.md](_deployment/DOCKER.md)
4. Pick up the next task from the current feature's TODO.md file

### For New Team Members

1. Start with this README (you're here!)
2. Read [_core/architecture.md](_core/architecture.md) for technical overview
3. Review [features/01-oauth-authentication/README.md](features/01-oauth-authentication/README.md) to understand auth flow
4. Check [00-RESUME-HERE.md](00-RESUME-HERE.md) to see current project status

### For Deploying the Application

1. Read [_deployment/SELF_HOSTING_GUIDE.md](_deployment/SELF_HOSTING_GUIDE.md)
2. Ensure you have:
   - Laserfiche Developer Console app registration (Web App type)
   - PostgreSQL database
   - Server with Docker support
3. Follow step-by-step installation instructions

---

## 📚 Documentation Standards

### File Organization

- **Files starting with `_`** = Documentation type (not a feature)
  - `_core/` - Architecture, design, data models
  - `_security/` - Security documentation
  - `_deployment/` - Deployment guides
  - `_api/` - API specifications
  - `_testing/` - Testing documentation

- **Numbered folders** = Features (chronological implementation order)
  - `01-oauth-authentication/` - Built first
  - `02-table-crud-operations/` - Built second
  - `03-basic-react-ui/` - Built third
  - etc.

### Required Files Per Feature

Each feature folder MUST contain:
1. **STATUS.md** - High-level status (REQUIRED)
2. **TODO.md** - Detailed task breakdown (REQUIRED)
3. **README.md** - Feature overview (REQUIRED)
4. Additional implementation docs as needed

### Status Indicators

- ✅ **COMPLETE** - Deployed to production, fully tested
- ⚠️ **IN PROGRESS** - Currently being worked on
- 📋 **PLANNED** - Designed but not implemented
- 🔴 **BLOCKED** - Waiting on dependencies

### Update Frequency

- Update **00-RESUME-HERE.md** at end of each work session
- Update feature **STATUS.md** when progress changes
- Update **TODO.md** daily as tasks complete
- Keep dates current (Last Updated: YYYY-MM-DD)

---

## 🔗 External Resources

### Laserfiche Documentation
- [Laserfiche Developer Console](https://developers.laserfiche.com/)
- [OAuth 2.0 Authorization Guide](https://developers.laserfiche.com/guides/guide_oauth-2.0-authorization.html)
- [OData Table API Reference](https://developers.laserfiche.com/guides/guide_odata-table-api.html)

### Technology Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 📞 Questions?

This documentation system works best when:
- ✅ You have multiple features to track
- ✅ You need to step away and resume easily
- ✅ You want clear status visibility
- ✅ You value consistent documentation

**When updating documentation:**
- Always update dates (`Last Updated: YYYY-MM-DD`)
- Keep 00-RESUME-HERE.md current (single source of truth)
- Update feature STATUS.md when progress changes
- Mark TODOs as complete with `[x]` when done

---

**Documentation System Version:** 1.0
**Last Updated:** 2025-11-18
**Project:** Laserfiche Data View
**Tech Stack:** FastAPI + React + PostgreSQL + Laserfiche API
