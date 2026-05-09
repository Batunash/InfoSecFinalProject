# DevSecOps Pipeline - Presentation & Testing Guide

## Presentation Structure (10-15 minutes)

### Slide 1: Title Slide
**Title:** Automated DevSecOps Pipeline Implementation
**Subtitle:** SENG 473 Information Security Final Project
**Your Name:** [Your Name]
**Date:** [Presentation Date]

---

### Slide 2: Problem Statement
**Key Points:**
- Security is often an afterthought in traditional DevOps
- Manual security checks are time-consuming and error-prone
- Vulnerabilities are discovered late in the development cycle
- Need for automated, continuous security integration

**Visual:** Traditional DevOps vs DevSecOps comparison

---

### Slide 3: Solution Overview
**Key Points:**
- Integrated CI/CD pipeline with security at every stage
- Automated security scanning (SAST, DAST, SCA, Container, IaC)
- Shift-left security approach
- Compliance with OWASP Top 10, CIS Benchmarks

**Visual:** Pipeline architecture diagram

---

### Slide 4: Architecture
**Key Points:**
- GitHub Actions for CI/CD automation
- Flask application with JWT authentication
- Kubernetes deployment with security contexts
- Terraform for infrastructure as code

**Visual:** System architecture diagram

---

### Slide 5: Security Tools
**Key Points:**
| Tool | Type | Purpose |
|------|------|---------|
| Bandit | SAST | Python code security |
| OWASP ZAP | DAST | Runtime security |
| Safety | SCA | Dependency vulnerabilities |
| Trivy | Container | Image scanning |
| Checkov | IaC | Infrastructure security |
| SonarQube | Quality | Code quality & security |

---

### Slide 6: CI Pipeline
**Key Points:**
- Triggers: Push to main/develop, Pull requests
- Stages: Lint → Tests → SAST → SCA → SonarQube → Build → Container Scan
- Security gates prevent vulnerable code from advancing
- Results uploaded as artifacts

**Visual:** CI pipeline flow diagram

---

### Slide 7: CD Pipeline
**Key Points:**
- Triggers: Push to main branch
- Stages: Build → Push to Docker Hub → Deploy to Kubernetes
- Terraform for infrastructure management
- Automatic rollback on failure

**Visual:** CD pipeline flow diagram

---

### Slide 8: Security Features
**Key Points:**
- **Application Level:**
  - JWT-based authentication
  - Password hashing with bcrypt
  - Input validation and sanitization
  - Output encoding

- **Container Level:**
  - Minimal base images
  - Non-root user execution
  - Read-only filesystem
  - Resource limits

- **Infrastructure Level:**
  - Network policies
  - RBAC configuration
  - Secrets management

---

### Slide 9: Demo Overview
**Key Points:**
- Project structure
- Application functionality
- Security scanning in action
- CI/CD pipeline execution

---

### Slide 10: Results & Conclusion
**Key Points:**
- All security requirements met
- Automated security checks integrated
- Compliance with industry standards
- Future enhancements

---

## Live Demo Script (5-10 minutes)

### Part 1: Project Structure (1 minute)
```bash
# Show the directory structure
tree -L 3
# or on Windows:
dir /B /S *.py *.yml *.yaml
```

**What to say:**
"Here's the project structure. We have the application code in `app/src/`, tests in `app/tests/`, CI/CD workflows in `.github/workflows/`, infrastructure configurations in `infrastructure/`, and security tool configurations in `security/`."

---

### Part 2: Application Demo (2 minutes)
```bash
# Start the application
docker-compose up -d app

# Test the health endpoint
curl http://localhost:5000/health

# Register a user
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"password123","email":"demo@test.com"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"password123"}'
```

**What to say:**
"Let me start the application and demonstrate the API. First, I'll check the health endpoint, then register a user, and finally login to get a JWT token. The application uses bcrypt for password hashing and JWT for authentication."

---

### Part 3: Security Scanning Demo (3 minutes)
```bash
# SAST with Bandit
cd app
bandit -r src/ -c ../security/bandit-config.yaml

# SCA with Safety
safety check

# Container scan with Trivy
docker build -t devsecops-app:test .
trivy image devsecops-app:test --severity HIGH,CRITICAL
```

**What to say:**
"Now let me run the security scans. Bandit performs static analysis on the Python code, Safety checks for vulnerabilities in dependencies, and Trivy scans the Docker image for security issues. These scans run automatically in the CI pipeline."

---

### Part 4: Testing Demo (2 minutes)
```bash
# Run unit tests
pytest tests/ -v --cov=src

# Show coverage report
```

**What to say:**
"Here are the unit tests. We have comprehensive test coverage for the application functionality and authentication. The tests run automatically in the CI pipeline and must pass before any code can be merged."

---

### Part 5: CI/CD Pipeline Demo (2 minutes)
**Show GitHub Actions:**
1. Navigate to GitHub repository
2. Show the Actions tab
3. Click on a recent workflow run
4. Show the different jobs and their results
5. Show security scan artifacts

**What to say:**
"Here's the CI/CD pipeline in action on GitHub. You can see the different jobs: linting, tests, SAST, SCA, SonarQube, and container scanning. Security scan results are uploaded as artifacts for review."

---

## Testing Checklist

### Pre-Presentation Checklist

- [ ] Docker is installed and running
- [ ] Docker Compose is installed
- [ ] Python 3.11 is installed
- [ ] All dependencies are installed (`pip install -r app/requirements.txt`)
- [ ] Application builds successfully (`docker build -t devsecops-app:test app/`)
- [ ] Tests pass (`pytest app/tests/`)
- [ ] Security tools are installed (bandit, safety, trivy)

### Demo Day Checklist

- [ ] Project structure is visible
- [ ] Application starts without errors
- [ ] Health endpoint returns 200
- [ ] User registration works
- [ ] Login works and returns JWT token
- [ ] Protected endpoint requires authentication
- [ ] Unit tests pass
- [ ] Code coverage is >80%
- [ ] Bandit scan completes
- [ ] Safety scan completes
- [ ] Trivy scan completes
- [ ] CI/CD pipeline is visible on GitHub

### Common Issues & Solutions

**Issue:** Docker build fails
**Solution:** Check Docker is running, verify Dockerfile syntax

**Issue:** Application won't start
**Solution:** Check port 5000 is not in use, verify dependencies

**Issue:** Tests fail
**Solution:** Run tests locally first, check test environment

**Issue:** Security tools not found
**Solution:** Install tools: `pip install bandit safety trivy`

**Issue:** GitHub Actions not running
**Solution:** Check workflow files are in `.github/workflows/`, verify YAML syntax

---

## Questions to Anticipate

### Q: Why did you choose these specific security tools?
**A:** I chose industry-standard tools that are widely used and well-maintained. Bandit for Python SAST, OWASP ZAP for DAST, Safety for SCA, Trivy for container scanning, and Checkov for IaC scanning. These tools provide comprehensive coverage and integrate well with GitHub Actions.

### Q: How do you handle false positives in security scans?
**A:** Security tools can produce false positives. In production, you would configure suppression rules and review findings manually. For this project, I've configured the tools to focus on high-severity issues and documented any intentional test vulnerabilities.

### Q: What happens if a security scan finds a vulnerability?
**A:** The CI pipeline will fail, preventing the code from being deployed. The developer must fix the vulnerability and resubmit. For critical vulnerabilities, automated alerts can be sent to the security team.

### Q: How do you ensure secrets are not leaked?
**A:** I use Gitleaks to scan for secrets in the codebase. Secrets are stored in environment variables and Kubernetes secrets. The `.gitignore` file excludes sensitive files, and pre-commit hooks can prevent accidental commits.

### Q: How do you handle dependency updates?
**A:** Safety and OWASP Dependency-Check scan for known vulnerabilities in dependencies. When a vulnerability is found, the dependency should be updated to a secure version. Dependabot can be configured to automatically create pull requests for dependency updates.

### Q: What's the difference between SAST and DAST?
**A:** SAST (Static Application Security Testing) analyzes source code for vulnerabilities without running the application. DAST (Dynamic Application Security Testing) tests the running application for vulnerabilities by sending requests and analyzing responses. Both are important for comprehensive security.

### Q: How do you measure the effectiveness of your security pipeline?
**A:** I track metrics such as:
- Mean time to detect vulnerabilities
- Mean time to remediate vulnerabilities
- Number of vulnerabilities found and fixed
- Code coverage
- Security test pass rate

### Q: What compliance standards does this pipeline meet?
**A:** The pipeline implements controls aligned with OWASP Top 10, CIS Benchmarks, NIST Cybersecurity Framework, and PCI DSS requirements. Each security tool addresses specific compliance requirements.

---

## Presentation Tips

1. **Practice the demo** - Run through the demo multiple times before the presentation
2. **Have a backup** - Screenshots of the pipeline in case live demo fails
3. **Keep it simple** - Focus on the key features, don't get bogged down in details
4. **Be prepared for questions** - Review the anticipated questions
5. **Show enthusiasm** - This is a cool project, show your passion for security
6. **Time management** - Keep the presentation within the allotted time
7. **Know your audience** - Tailor the technical depth to your audience

---

## Quick Start Commands

```bash
# Start everything
docker-compose up -d

# Run tests
cd app && pytest tests/ -v

# Run security scans
cd app && bandit -r src/
safety check
trivy image devsecops-app:latest

# Stop everything
docker-compose down
```

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
