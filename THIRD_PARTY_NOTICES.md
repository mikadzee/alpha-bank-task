# Third-party notices

Direct application dependencies and their licenses at the time of this MVP. The frontend lockfile (`frontend/package-lock.json`) contains exact versions and license metadata for transitive npm packages. Backend direct versions are pinned in `backend/requirements.txt`; the Python base image supplies Python and operating-system packages.

| Component | Version source | License |
|---|---|---|
| Nuxt | `frontend/package-lock.json` | MIT |
| Vue | `frontend/package-lock.json` | MIT |
| Pinia | `frontend/package-lock.json` | MIT |
| `@pinia/nuxt` | `frontend/package-lock.json` | MIT |
| Axios | `frontend/package-lock.json` | MIT |
| Less | `frontend/package-lock.json` | Apache-2.0 |
| FastAPI | `backend/requirements.txt` (0.116.1) | MIT |
| Uvicorn | `backend/requirements.txt` (0.35.0) | BSD-3-Clause |
| Psycopg | `backend/requirements.txt` (3.2.9) | LGPL-3.0-or-later |
| PyJWT | `backend/requirements.txt` (2.10.1) | MIT |
| pwdlib | `backend/requirements.txt` (0.2.1) | BSD-3-Clause |
| email-validator | `backend/requirements.txt` (2.2.0) | MIT |
| python-multipart | `backend/requirements.txt` (0.0.20) | Apache-2.0 |
| PostgreSQL | `docker-compose.yaml` | PostgreSQL License |
| Python | `backend/Dockerfile` | PSF License |
| Node.js | `frontend/Dockerfile` | MIT License |

Transitive dependencies retain the license metadata and package notices shipped with the corresponding npm package or Python distribution. The runtime does not call a third-party AI model or hosted inference service and does not bundle model weights. It does not use an external news dataset or proprietary document corpus. Demo company/product data and the sample PDFs are synthetic and authored for this project.

For redistribution, retain the notices required by each dependency and review the full transitive package inventory from the lockfile and installed Python environment for the release build.
