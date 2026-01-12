# AI Resume Analyzer

A full-stack AI-powered resume analysis platform with NLP capabilities.

## Architecture

```
├── frontend/          # Next.js 14+ client (TailwindCSS, TypeScript)
├── backend/           # NestJS API Gateway (Prisma, JWT, Multer)
├── ml_service/        # Python FastAPI ML Engine (spaCy, Sentence-Transformers)
├── uploads/           # Shared volume for file uploads
└── Documentation/     # Project documentation
```

## Quick Start

```bash
# Start all services with Docker
docker-compose up --build

# Or run individually:
# Frontend: http://localhost:3001
cd frontend && npm run dev

# Backend: http://localhost:3000
cd backend && npm run start:dev

# ML Service: http://localhost:8000
cd ml_service && uvicorn main:app --reload
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, TailwindCSS, TypeScript |
| Backend | NestJS, Prisma, PostgreSQL |
| ML Service | FastAPI, spaCy, Sentence-Transformers |
| DevOps | Docker Compose |