# Handover Document

## Automated DevSecOps Pipeline — SENG 473 Information Security Final Project

---

## 1. Project Overview

### Purpose
This project implements an automated DevSecOps pipeline that integrates security at every stage of the software development lifecycle. It was built as the final project for SENG 473 Information Security.

### Objective
Demonstrate a fully functional CI/CD pipeline with automated security scanning (SAST, DAST, SCA, container scanning, IaC scanning) deployed via GitHub Actions, targeting a Kubernetes cluster provisioned with Terraform.

---

## 2. Project Structure

```
InfoSecFinalProject/
├── .github/
│   └── workflows/
│       ├── ci-pipeline.yml          # CI: lint, test, SAST, SCA, build, container scan
│       ├── cd-pipeline.yml          # CD: push image, deploy K8s + Terraform
│       └── security-scan.yml        # Scheduled: DAST, IaC, dependency, secret, license scans
├── app/
│   ├── src/
│   │   ├── main.py                  # Flask application with JWT auth & API endpoints
│   │   ├── auth.py                  # Password hashing (bcrypt), input validation, token utils
│   │   └── utils.py                 # Output sanitization, security logging, helpers
│   ├── tests/
│   │   ├── test_main.py             # Application endpoint tests (registration, login, auth)
│   │   └── test_auth.py             # Auth utility tests (hashing, validation, tokens)
│   ├── requirements.txt             # Python dependencies + security/quality tools
│   └── Dockerfile                   # Secure container image (non-root, health check)
├── infrastructure/
│   ├── kubernetes/
│   │   ├── deployment.yaml          # Deployment, HPA, PDB, NetworkPolicy, SA, Secret
│   │   └── service.yaml             # Service (LoadBalancer + ClusterIP), Ingress, ConfigMap
│   └── terraform/
│       └── main.tf                  # Full K8s resource provisioning via Terraform
├── security/
│   ├── bandit-config.yaml           # Bandit SAST rule configuration
│   └── zap-config.yaml              # OWASP ZAP DAST scan profile
├── docs/
│   ├── README.md                    # Project documentation, setup, API reference
│   ├── ARCHITECTURE.md              # System architecture, pipeline details, compliance mapping
│   └── SECURITY.md                  # Security controls, vulnerability management, incident response
├── demo.bat                         # Windows demo script
├── demo.sh                          # Linux/Mac demo script
├── verify.py                        # Pre-presentation verification script
├── PRESENTATION_GUIDE.md            # Detailed presentation guide with slides and Q&A
├── QUICK_REFERENCE.md               # One-page command cheat sheet
├── PRESENTATION_README.md           # Presentation summary
├── docker-compose.yml               # Local dev environment (app, SonarQube, ZAP, Prometheus, Grafana)
└── HANDOVER.md                      # This file
```

---

## 3. Technology Stack

### Application
| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11 |
| Framework | Flask | 3.0.0 |
| Authentication | Flask-JWT-Extended | 4.6.0 |
| Password Hashing | bcrypt | 4.1.2 |
| Container Runtime | Docker | 24+ |
| Container Orchestration | Kubernetes | 1.28+ |
| IaC | Terraform | 1.6+ |

### Security Tools
| Tool | Type | Version | Purpose |
|------|------|---------|---------|
| Bandit | SAST | 1.7.6 | Static code analysis for Python |
| OWASP ZAP | DAST | stable | Runtime vulnerability scanning |
| Safety | SCA | 2.3.5 | Dependency vulnerability check |
| Trivy | Container | latest | Docker image vulnerability scan |
| Checkov | IaC | latest | Terraform/K8s security check |
| SonarQube | Quality | community | Code quality & security analysis |
| Gitleaks | Secret | v2 | Hardcoded secret detection |
| pip-audit | License | latest | License compliance scanning |

### CI/CD
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Pipeline | GitHub Actions | CI/CD automation |
| Registry | Docker Hub | Container image storage |
| Deployment | Kubernetes | Application hosting |
| Monitoring | Prometheus + Grafana | Metrics & dashboards |

---

## 4. Pipeline Details

### 4.1 CI Pipeline (`ci-pipeline.yml`)

**Trigger:** Push to `main`/`develop`, Pull Request to `main`

**Jobs (parallel where possible):**

| Job | Tool | Purpose | Blocking |
|-----|------|---------|----------|
| lint | Black, isort, Flake8 | Code formatting & style | Yes |
| unit-tests | Pytest | Unit tests + coverage report | Yes |
| sast | Bandit | Static security analysis | Yes |
| sca | Safety | Dependency vulnerability scan | Yes |
| sonarqube | SonarQube | Code quality & security gate | No (advisory) |
| build | Docker, Trivy | Image build + container scan | Yes (depends on lint, tests, sast, sca) |
| security-summary | — | Aggregated scan summary | No |

**Flow:**
```
Push/PR → lint ──┐
         tests ──┤
         sast ───┤──→ build (Docker + Trivy) → security-summary
         sca ────┘
         sonarqube (advisory, parallel)
```

### 4.2 CD Pipeline (`cd-pipeline.yml`)

**Trigger:** Push to `main` branch, Manual dispatch

**Jobs:**

| Job | Purpose |
|-----|---------|
| build-and-push | Build image, tag (latest + git-sha), push to Docker Hub, Trivy scan |
| deploy-kubernetes | kubectl set image, rollout, verify, logs on failure |
| deploy-terraform | terraform init → plan → apply |
| notify | Deployment success/failure notification |

### 4.3 Security Scan Pipeline (`security-scan.yml`)

**Trigger:** Daily at 02:00 UTC, Manual dispatch

**Jobs:**

| Job | Tool | Purpose |
|-----|------|---------|
| dast | OWASP ZAP | Baseline scan of running application |
| iac-scan | Checkov | Terraform + Kubernetes manifest security |
| dependency-scan | OWASP Dependency-Check, Snyk | Known CVEs in dependencies |
| secret-scan | Gitleaks | Hardcoded secrets in git history |
| license-scan | pip-audit | License compliance |
| security-summary | — | Aggregated report, auto-create GitHub issue on failure |

---

## 5. Application Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Home page with API documentation |
| GET | `/health` | No | Health check (used by K8s probes) |
| POST | `/api/register` | No | Register user (username, password, email) |
| POST | `/api/login` | No | Login, returns JWT access token |
| GET | `/api/protected` | Yes | Demo protected endpoint |
| GET | `/api/user/info` | Yes | Get current user info (email, created_at) |
| POST | `/api/user/update` | Yes | Update user email |

**Authentication flow:**
1. `POST /api/register` → creates user (bcrypt-hashed password)
2. `POST /api/login` → returns JWT Bearer token
3. Subsequent requests include `Authorization: Bearer <token>`

---

## 6. Security Controls

### Application Level
- **Authentication:** JWT with 1-hour expiry, configurable secret
- **Password Storage:** bcrypt with auto-generated salt
- **Input Validation:** Regex-based validation for username, email, password
- **Output Encoding:** `html.escape()` for XSS prevention
- **Security Logging:** All auth events logged with timestamps
- **Max Upload Size:** 16MB enforced by Flask config

### Container Level
- **Base Image:** `python:3.11-slim` (minimal attack surface)
- **Non-root User:** `appuser` (UID 1000)
- **Read-only Filesystem:** Root filesystem is read-only
- **Health Check:** Built-in Docker HEALTHCHECK + K8s probes
- **Resource Limits:** CPU 500m, Memory 512Mi per container
- **Capability Drop:** All Linux capabilities dropped (`drop: ALL`)

### Infrastructure Level
- **Network Policies:** Ingress only from ingress-nginx namespace, egress limited to DNS + DB
- **Pod Anti-Affinity:** Pods spread across nodes for availability
- **Horizontal Pod Autoscaler:** 3–10 replicas, CPU/memory thresholds
- **Pod Disruption Budget:** Min 2 available during disruptions
- **RBAC:** Dedicated ServiceAccount per deployment
- **Secrets Management:** Kubernetes Secrets (base64), should use external vault in production
- **TLS:** Ingress configured with cert-manager + Let's Encrypt

---

## 7. GitHub Secrets Required

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Required | Description |
|--------|----------|-------------|
| `DOCKER_USERNAME` | Yes | Docker Hub username |
| `DOCKER_PASSWORD` | Yes | Docker Hub access token |
| `SONAR_TOKEN` | No | SonarQube authentication token |
| `SONAR_HOST_URL` | No | SonarQube server URL |
| `KUBE_CONFIG` | Yes (CD) | Base64-encoded kubeconfig |
| `SNYK_TOKEN` | No | Snyk authentication token |
| `GITLEAKS_LICENSE` | No | Gitleaks enterprise license |

---

## 8. Local Development Setup

### Prerequisites
- Docker Desktop (running)
- Python 3.11+
- pip

### Steps

```bash
# 1. Clone repository
git clone <repo-url>
cd InfoSecFinalProject

# 2. Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r app/requirements.txt

# 4. Start local environment (app + SonarQube + ZAP + monitoring)
docker-compose up -d

# 5. Run application directly (without Docker)
cd app
python src/main.py

# 6. Run tests
pytest tests/ -v --cov=src

# 7. Run security scans locally
bandit -r src/ -c ../security/bandit-config.yaml
safety check

# 8. Build and scan container image
docker build -t devsecops-app:test app/
trivy image devsecops-app:test

# 9. Stop local environment
docker-compose down
```

### Accessing Local Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Application | http://localhost:5000 | — |
| SonarQube | http://localhost:9000 | admin / admin |
| OWASP ZAP | http://localhost:8080 | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / admin |

---

## 9. Testing Guide

### Unit Tests
```bash
cd app
pytest tests/ -v --cov=src --cov-report=term-missing
```

**Test coverage:**
- `test_main.py`: Health check, home page, registration (valid/invalid/duplicate), login (valid/invalid/missing), protected endpoints (with/without auth), user info/update, error handling (404/405), security features (max upload, content type)
- `test_auth.py`: Password hashing/verification, bcrypt salt uniqueness, input validation (username/email/password), strong password requirements, token generation/verification/expiry/tampering

### Security Scans
```bash
# SAST
cd app && bandit -r src/ -c ../security/bandit-config.yaml

# SCA
cd app && safety check

# Container scan
trivy image devsecops-app:test --severity HIGH,CRITICAL

# IaC scan
checkov -d infrastructure/ --framework terraform,kubernetes

# Secret scan
gitleaks detect --source . --config security/gitleaks-config.toml
```

### Demo Scripts
```bash
# Windows
demo.bat

# Linux/Mac
bash demo.sh

# Or verify everything at once
python verify.py
```

---

## 10. Deployment Guide

### Kubernetes (Manual)
```bash
# 1. Update image reference in deployment.yaml
# Replace YOUR_USERNAME with your Docker Hub username

# 2. Create namespace
kubectl create namespace production

# 3. Apply manifests
kubectl apply -f infrastructure/kubernetes/

# 4. Verify
kubectl get pods -n production
kubectl get deployment devsecops-app -n production
kubectl port-forward svc/devsecops-app-service 5000:80 -n production
```

### Terraform
```bash
cd infrastructure/terraform

# 1. Initialize
terraform init

# 2. Plan
terraform plan -out=tfplan

# 3. Apply
terraform apply tfplan

# 4. Check outputs
terraform output
```

### Rolling Back
```bash
# Kubernetes rollback
kubectl rollout undo deployment/devsecops-app -n production

# Terraform rollback
terraform workspace select production
terraform apply -target=kubernetes_deployment.app -var="docker_image=<previous-image>"
```

---

## 11. Known Issues & Limitations

| Issue | Impact | Workaround |
|-------|--------|------------|
| In-memory user storage | Data lost on restart | Use a real database in production |
| Hardcoded JWT secret fallback | Potential secret leak | Always set `JWT_SECRET_KEY` env var |
| ZAP DAST may not find all endpoints | Incomplete coverage | Add OpenAPI spec for full scan |
| Docker Hub credentials required | CD pipeline blocked without them | Use GitHub Container Registry as alternative |
| SonarQube requires separate server | Quality gate not enforced | Set up SonarQube server or use SonarCloud |
| No rate limiting implemented | Brute-force attack possible | Add Flask-Limiter in production |
| K8s Secret values are base64 only | Not truly encrypted at rest | Use external secrets manager (Vault, AWS SM) |
| Terraform state stored locally | No state locking | Configure remote backend (S3 + DynamoDB) |

---

## 12. Future Enhancements

| Priority | Enhancement | Description |
|----------|------------|-------------|
| High | External Secrets Manager | HashiCorp Vault or AWS Secrets Manager |
| High | Rate Limiting | Flask-Limiter or API Gateway rate limits |
| High | Database Integration | PostgreSQL with SQLAlchemy, replace in-memory storage |
| Medium | Signed Container Images | Cosign/image signing for supply chain security |
| Medium | Policy as Code | OPA/Gatekeeper for K8s admission control |
| Medium | SBOM Generation | Syft for Software Bill of Materials |
| Medium | E2E Testing | Playwright or Selenium for full UI flow testing |
| Low | Distributed Tracing | Jaeger or OpenTelemetry integration |
| Low | Service Mesh | Istio for mTLS and traffic management |
| Low | Chaos Engineering | Litmus or Chaos Mesh for resilience testing |

---

## 13. Compliance Mapping

| Standard | Control | Implementation |
|----------|---------|----------------|
| OWASP A01 | Broken Access Control | JWT auth, RBAC, protected endpoints |
| OWASP A02 | Cryptographic Failures | bcrypt hashing, TLS via Ingress |
| OWASP A03 | Injection | Input validation, html.escape() |
| OWASP A05 | Security Misconfiguration | Security contexts, network policies, non-root |
| OWASP A07 | Auth Failures | JWT expiry, bcrypt, strong password checks |
| OWASP A08 | Data Integrity Failures | SCA scanning, Trivy image scanning |
| CIS Docker | Container Security | Minimal image, non-root, read-only FS |
| CIS Kubernetes | Cluster Security | Network policies, RBAC, resource limits |
| NIST CSF ID.AM | Asset Management | IaC versioned in Git |
| NIST CSF PR.AC | Access Control | JWT, RBAC, secrets management |
| NIST CSF DE.CM | Security Monitoring | Prometheus, security event logging |
| NIST CSF RS.MI | Incident Response | Automated alerts, GitHub issues on scan failure |

---

## 14. Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `docker-compose up` fails | Docker not running | Start Docker Desktop |
| Port 5000 already in use | Another process on port | `netstat -ano | findstr :5000` then kill process or change port |
| `pytest` not found | venv not activated | Activate venv: `venv\Scripts\activate` |
| `bandit` not found | Tool not installed | `pip install bandit[toml]` |
| `safety check` returns errors | Known CVE in dependency | Update the vulnerable package |
| `trivy` not found | Tool not installed | Download from github.com/aquasecurity/trivy |
| Docker build fails | Syntax error in Dockerfile | Verify Dockerfile, check logs |
| K8s deployment not ready | Image pull error | Verify image exists, check `kubectl describe pod` |
| Terraform apply fails | Backend not configured | Configure S3 backend or use local backend |
| GitHub Actions not triggering | Wrong branch or path | Verify workflow triggers and file paths |

---

## 15. Contact & References

### Key References
- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [Trivy Documentation](https://trivy.dev/)
- [Checkov Documentation](https://www.checkov.io/)
- [SonarQube Documentation](https://docs.sonarqube.org/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
- [Terraform Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)

### Project Artifacts
- CI Pipeline results: GitHub → Actions → CI Pipeline
- Security scan reports: GitHub → Actions → Artifacts
- Code coverage: GitHub → Actions → Artifacts (or Codecov if configured)
- Container images: Docker Hub → `YOUR_USERNAME/devsecops-app`

---

## 16. Acceptance Criteria Checklist

- [x] Automated CI pipeline with linting, testing, and security scanning
- [x] SAST integrated (Bandit) with configurable rules
- [x] DAST integrated (OWASP ZAP) with scan profiles
- [x] SCA integrated (Safety) for dependency vulnerability detection
- [x] Container image scanning (Trivy) in CI and CD pipelines
- [x] IaC scanning (Checkov) for Terraform and Kubernetes manifests
- [x] Secret scanning (Gitleaks) in scheduled pipeline
- [x] Code quality analysis (SonarQube) integration
- [x] Secure Docker image (non-root, read-only FS, health check)
- [x] Kubernetes deployment with security contexts and network policies
- [x] Terraform infrastructure as code
- [x] Horizontal Pod Autoscaling and Pod Disruption Budgets
- [x] HTTPS ingress with cert-manager
- [x] Unit tests with coverage reporting
- [x] Documentation (README, ARCHITECTURE, SECURITY)
- [x] Local development environment (docker-compose)
- [x] Demo and verification scripts
- [x] Presentation guide and Q&A preparation
- [x] OWASP Top 10 compliance mapping
- [x] NIST CSF compliance mapping
