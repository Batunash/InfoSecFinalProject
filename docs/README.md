# DevSecOps Pipeline Project

This project implements an automated DevSecOps pipeline for SENG 473 Information Security final project. The pipeline integrates multiple security tools (SAST, DAST, SCA, container scanning, IaC scanning) into a GitHub Actions CI/CD workflow with automated testing, code quality checks, and security remediation.

## Features

- **Automated CI/CD Pipeline** with GitHub Actions
- **Static Application Security Testing (SAST)** with Bandit
- **Dynamic Application Security Testing (DAST)** with OWASP ZAP
- **Software Composition Analysis (SCA)** with Safety
- **Container Image Scanning** with Trivy
- **Infrastructure as Code Scanning** with Checkov
- **Code Quality Analysis** with SonarQube
- **Kubernetes Deployment** with security best practices
- **Terraform Infrastructure** as Code

## Project Structure

```
InfoSecFinalProject/
├── .github/
│   └── workflows/
│       ├── ci-pipeline.yml      # CI pipeline with security scans
│       ├── cd-pipeline.yml      # CD pipeline for deployment
│       └── security-scan.yml    # Scheduled security scans
├── app/
│   ├── src/
│   │   ├── main.py              # Flask application
│   │   ├── auth.py              # Authentication utilities
│   │   └── utils.py             # Utility functions
│   ├── tests/
│   │   ├── test_main.py         # Main application tests
│   │   └── test_auth.py         # Authentication tests
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile              # Container image definition
├── infrastructure/
│   ├── kubernetes/
│   │   ├── deployment.yaml      # Kubernetes deployment
│   │   └── service.yaml         # Kubernetes service
│   └── terraform/
│       └── main.tf              # Terraform configuration
├── security/
│   ├── bandit-config.yaml       # Bandit SAST configuration
│   └── zap-config.yaml          # OWASP ZAP DAST configuration
├── docs/
│   ├── ARCHITECTURE.md          # Architecture documentation
│   ├── SECURITY.md              # Security documentation
│   └── README.md                # This file
└── docker-compose.yml          # Local development setup
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.11
- kubectl (for Kubernetes deployment)
- Terraform (optional)
- GitHub account (for CI/CD)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd InfoSecFinalProject
   ```

2. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

3. **Access the services**
   - Application: http://localhost:5000
   - SonarQube: http://localhost:9000 (admin/admin)
   - OWASP ZAP: http://localhost:8080
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)

### Running Tests

```bash
cd app
pytest tests/ -v --cov=src
```

### Security Scanning

```bash
# SAST with Bandit
bandit -r src/ -c ../security/bandit-config.yaml

# SCA with Safety
safety check

# Container scan with Trivy
trivy image devsecops-app:latest
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Home page with API documentation | No |
| GET | `/health` | Health check endpoint | No |
| POST | `/api/register` | Register a new user | No |
| POST | `/api/login` | Login and get JWT token | No |
| GET | `/api/protected` | Protected endpoint | Yes |
| GET | `/api/user/info` | Get user information | Yes |
| POST | `/api/user/update` | Update user information | Yes |

### Example API Usage

**Register a user:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123","email":"test@example.com"}'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

**Access protected endpoint:**
```bash
curl -X GET http://localhost:5000/api/protected \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Pipeline Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Code Push │────▶│   CI Pipeline│────▶│  Build &   │
└─────────────┘     └─────────────┘     │  Test      │
                                        └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Security   │◀────│  Security   │◀────│  Security   │
│  Scanning   │     │  Scanning   │     │  Scanning   │
└─────────────┘     └─────────────┘     └─────────────┘
     SAST                SCA               Container
     DAST                IaC               Image

                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Deploy to  │────▶│  Monitor &  │────▶│  Alert &    │
│ Kubernetes  │     │  Log        │     │  Remediate  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Security Tools

| Tool | Purpose | Integration |
|------|---------|-------------|
| Bandit | SAST for Python | GitHub Actions |
| Safety | SCA for Python dependencies | GitHub Actions |
| Trivy | Container image scanning | GitHub Actions |
| OWASP ZAP | DAST for web applications | GitHub Actions |
| Checkov | IaC security scanning | GitHub Actions |
| SonarQube | Code quality and security | GitHub Actions |
| OWASP Dependency-Check | Dependency vulnerability scanning | GitHub Actions |
| Gitleaks | Secret scanning | GitHub Actions |

## Security Best Practices Implemented

### Application Level
- JWT-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- Output encoding
- Security event logging
- Rate limiting (recommended)

### Container Level
- Minimal base images (python:3.11-slim)
- Non-root user execution
- Read-only filesystem
- Resource limits
- Security contexts
- Health checks

### Infrastructure Level
- Network policies
- RBAC configuration
- Secrets management
- Pod security policies
- Horizontal Pod Autoscaling
- Pod Disruption Budgets

## GitHub Secrets Configuration

To use the CI/CD pipeline, configure the following secrets in your GitHub repository:

| Secret | Description |
|--------|-------------|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password/token |
| `SONAR_TOKEN` | SonarQube authentication token |
| `SONAR_HOST_URL` | SonarQube server URL |
| `KUBE_CONFIG` | Base64-encoded Kubernetes config |
| `SNYK_TOKEN` | Snyk authentication token |
| `GITLEAKS_LICENSE` | Gitleaks license (optional) |

## Deployment

### Kubernetes Deployment

1. Update the image name in `infrastructure/kubernetes/deployment.yaml`
2. Apply the manifests:
   ```bash
   kubectl apply -f infrastructure/kubernetes/
   ```

### Terraform Deployment

1. Configure your Terraform backend
2. Run:
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform plan
   terraform apply
   ```

## Monitoring and Alerting

### Metrics
- Application performance
- Security scan results
- Build success rate
- Deployment frequency

### Logging
- Application logs
- Security scan logs
- Pipeline execution logs
- System logs

### Alerts
- Security vulnerabilities detected
- Build failures
- Deployment issues
- Anomalous behavior

## Compliance

This pipeline implements security controls aligned with:
- OWASP Top 10
- CIS Benchmarks
- NIST Cybersecurity Framework
- PCI DSS requirements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License

## Contact

For questions or issues, please open an issue in the repository.
