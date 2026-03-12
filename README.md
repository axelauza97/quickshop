# quickshop

## Docker: see backend code changes

### 1) Start backend in dev mode (hot reload)

```bash
docker compose up -d db backend
docker compose logs -f backend
```

### 2) Force restart backend container

```bash
docker compose restart backend
```

### 3) Rebuild backend image (required after Dockerfile/dependency changes)

```bash
docker compose up -d --build backend
```

### 4) Hard refresh backend container + image

```bash
docker compose rm -sf backend
docker compose up -d --build backend
```

### 5) Full clean rebuild of the whole stack

```bash
docker compose down -v
docker compose up -d --build
```

## Environment note

Backend requires Auth0 env vars. If they are missing, backend will fail at startup.

```bash
cp .env.example .env
```

Then set:
- `AUTH0_DOMAIN`
- `AUTH0_API_AUDIENCE`
- `AUTH0_ISSUER`
- `AUTH0_CLIENT_ID`
