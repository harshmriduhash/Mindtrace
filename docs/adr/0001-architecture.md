# ADR 0001 — Launch architecture

**Date:** 2026-11-07  
**Status:** Accepted

## Decision
Modular monolith: Next.js App Router frontend + FastAPI API + PostgreSQL + Redis queue + S3-compatible object storage. One worker process for ingestion/evaluation.

## Alternatives
- All-in-Next.js server actions → weaker AI/document processing boundary
- Microservices → premature operational cost

## Revisit when
Measured queue isolation needs, team ownership boundaries, or API/worker scaling diverge.
