# The Glow Mission

Dockerized website and CMS for The Glow Mission.

## Stack

- Django, Django REST Framework, PostgreSQL
- S3-backed media through `django-storages`
- Next.js App Router, TypeScript, Tailwind
- nginx reverse proxy
- Docker Compose services: `postgres`, `backend`, `frontend`, `nginx`

## S3 Is Required

This project intentionally uses real S3-compatible storage from the beginning. There is no LocalStack setup and no normal-runtime local media fallback.

Before starting Docker, copy `.env.example` to `.env` and fill:

```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=ap-south-1
AWS_MEDIA_LOCATION=media
AWS_SEED_ASSET_LOCATION=seed-assets
AWS_PRESIGNED_URL_EXPIRE_SECONDS=900
NEXT_PUBLIC_SITE_URL=https://theglowmission.com
ADMIN_EMAIL=admin@theglowmission.local
ADMIN_PASSWORD=change-me-now
```

`AWS_S3_ENDPOINT_URL` is only for real production S3-compatible storage. Do not point it at LocalStack for this project.

## Run

```bash
cp .env.example .env
# edit .env with real PostgreSQL/S3/admin settings
docker compose up --build
```

Backend startup runs:

1. S3 validation with a real bucket write/delete smoke test.
2. Database migrations.
3. `seed_site`, which creates the admin user, CMS content, campaign form, and uploads the provided brand assets to S3.
4. Gunicorn.

Open:

- Public site: `http://localhost/`
- CMS: `http://localhost/admin/login`
- API health: `http://localhost/api/v1/health/`
- Deep health with S3: `http://localhost/api/v1/health/deep/`

## Main API Surface

Public:

- `GET /api/v1/public/brand-settings/`
- `GET /api/v1/public/pages/{slug}/`
- `GET /api/v1/public/services/`
- `GET /api/v1/public/services/{slug}/`
- `GET /api/v1/public/seo-index/`
- `GET /api/v1/public/gallery/`
- `GET /api/v1/public/campaign-forms/{slug}/`
- `POST /api/v1/public/campaign-forms/{slug}/responses/`

Admin:

- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`
- `/api/v1/admin/brand-settings/`
- `/api/v1/admin/pages/`
- `/api/v1/admin/page-sections/`
- `/api/v1/admin/services/`
- `/api/v1/admin/faqs/`
- `/api/v1/admin/gallery/`
- `/api/v1/admin/media-assets/`
- `/api/v1/admin/campaign-forms/`
- `/api/v1/admin/campaign-fields/`
- `/api/v1/admin/campaign-responses/`
- `GET /api/v1/admin/campaign-forms/{id}/responses/export/`

Admin APIs use DRF token auth. The CMS stores the token in browser local storage after login.

## Development Checks

Frontend:

```bash
cd apps/frontend
npm install
npm run typecheck
npm run build
```

Backend syntax-only check without live dependencies:

```bash
python3 -m compileall apps/backend
```

Full backend runtime checks require installing Python dependencies and setting a live PostgreSQL and S3 environment. The Docker path is the source of truth.
