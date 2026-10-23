<div align="center">

# S3M Network Access Control (NAC)

### A RADIUS-based Network Access Control system: authenticate, authorize, account.

A containerized NAC built around FreeRADIUS and a FastAPI policy engine — PAP and MAC-based authentication, dynamic VLAN assignment, and session accounting backed by PostgreSQL and Redis.

![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![FreeRADIUS](https://img.shields.io/badge/AAA-FreeRADIUS-0A6CA6?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Cache-Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Deploy-Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## Overview

This project, built for the S3M internship assessment, is a foundational Network Access Control system using the RADIUS protocol. It demonstrates the full AAA cycle:

- **Authentication** — PAP (password-based) and MAB (MAC Authentication Bypass)
- **Authorization** — dynamic VLAN assignment based on user groups
- **Accounting** — session duration and transferred data (input/output octets) stored in PostgreSQL, with active sessions cached in Redis

---

## Architecture

The system has four main components:

| Component | Role |
|---|---|
| FreeRADIUS | Receives RADIUS requests from clients and forwards them to the policy engine via the `rlm_rest` module |
| FastAPI (Policy Engine) | REST API where the AAA business logic runs |
| PostgreSQL | Persistent store for users, groups, permissions, and session records |
| Redis | In-memory store for rate limiting (failed logins) and active-session tracking |

Everything is orchestrated with Docker Compose.

---

## Setup

```bash
# 1. Clone and enter the project directory
# 2. Create your environment file from the example
cp .env.example .env

# 3. Build and start all services
docker-compose up -d --build
```

On first run, database tables are created automatically from `db/init.sql` and via FastAPI's `Base.metadata.create_all`, and default test data (an admin user and a device MAC) is seeded.

---

## Test Scenarios

You need `radtest` and `radclient` installed locally, or you can run them from inside the FreeRADIUS container.

**1. PAP authentication**
```bash
radtest s3m_admin testing123 localhost:1812 0 testing123
```
Expected: `Access-Accept` with a `Tunnel-Private-Group-Id` (VLAN) assignment.

**2. MAB (MAC bypass) authentication**
```bash
echo "User-Name=AA:BB:CC:DD:EE:FF, Calling-Station-Id=AA:BB:CC:DD:EE:FF" | radclient -x localhost:1812 auth testing123
```
Expected: `Access-Accept` with a device-specific VLAN assignment.

**3. API endpoints**
Open the FastAPI Swagger docs at `http://localhost:8000/docs`, or list users and sessions directly:
```bash
curl http://localhost:8000/users
curl http://localhost:8000/sessions/active
```

---

## Security

- Secrets and passwords are managed via the `.env` file and are **not** committed to the repository.
- Redis-based rate limiting protects against brute force (5 attempts per minute).
