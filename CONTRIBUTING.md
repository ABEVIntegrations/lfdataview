# Contributing to LF DataView

Thank you for your interest in contributing to LF DataView!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/lfdataview.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for backend development)
- Node.js 18+ (for frontend development)
- Laserfiche Cloud developer account

### Running Locally

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with your Laserfiche credentials
# See README.md for required values

# Start with Docker
docker-compose up -d

# Or run backend directly for development
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Or run frontend directly
cd frontend
npm install
npm run dev
```

## Code Style

### Backend (Python)

- Follow PEP 8
- Use Black for formatting: `black app/`
- Use Ruff for linting: `ruff app/`
- Type hints are encouraged

### Frontend (TypeScript/React)

- Use ESLint configuration provided
- Use Prettier for formatting
- Prefer functional components with hooks

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation if needed
3. Test your changes locally
4. Create a pull request with a clear description

## Reporting Issues

When reporting issues, please include:

- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Docker version, etc.)

## Questions?

Open an issue with the "question" label.
