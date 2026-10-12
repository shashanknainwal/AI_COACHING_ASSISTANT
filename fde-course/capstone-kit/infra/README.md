# Infra

- `Dockerfile`: builds the stdlib HTTP service in `app/server.py`. Build from the repo root: `docker build -f infra/Dockerfile -t capstone .`
- `terraform/`: a commented skeleton for a container service (written for Cloud Run, with the ECS mapping in comments). Run `terraform init && terraform validate` to check it. **Applying it creates billable resources**; the capstone only needs it to validate and to be explained.

What a reviewer will ask about: where the key lives (a secret manager, never the image or Terraform state), what identity the service runs as and what it may touch, how spend is bounded (max instances, the per-request budget in `app/server.py`, a Console spend limit), and what you log (no request bodies by default, because they may contain customer data).
