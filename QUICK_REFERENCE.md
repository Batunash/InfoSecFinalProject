# DevSecOps Pipeline - Quick Reference Card

## Quick Commands

### Start Application
```bash
docker-compose up -d
```

### Stop Application
```bash
docker-compose down
```

### Run Tests
```bash
cd app
pytest tests/ -v --cov=src
```

### Security Scans
```bash
# SAST
cd app && bandit -r src/

# SCA
cd app && safety check

# Container Scan
trivy image devsecops-app:latest
```

### Build Docker Image
```bash
docker build -t devsecops-app:test app/
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/health` | Health check |
| POST | `/api/register` | Register user |
| POST | `/api/login` | Login |
| GET | `/api/protected` | Protected (needs auth) |
| GET | `/api/user/info` | User info (needs auth) |

## Test Credentials

- Username: `demouser`
- Password: `password123`
- Email: `demo@test.com`

## Security Tools Summary

| Tool | Command | Purpose |
|------|---------|---------|
| Bandit | `bandit -r src/` | SAST |
| Safety | `safety check` | SCA |
| Trivy | `trivy image <image>` | Container scan |
| Black | `black --check src/` | Code formatting |
| Flake8 | `flake8 src/` | Code style |
| Pytest | `pytest tests/` | Unit tests |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | Change port in docker-compose.yml |
| Docker not running | Start Docker Desktop |
| Tests fail | Check dependencies installed |
| Security tools not found | `pip install bandit safety trivy` |

## Presentation Flow

1. **Introduction** (1 min)
   - Problem statement
   - Solution overview

2. **Architecture** (2 min)
   - System design
   - Security tools

3. **Demo** (5 min)
   - Project structure
   - Application
   - Security scans
   - Tests

4. **CI/CD** (2 min)
   - GitHub Actions
   - Pipeline results

5. **Conclusion** (1 min)
   - Results
   - Future work

## Key Points to Mention

- ✓ Automated security at every stage
- ✓ Shift-left security approach
- ✓ Compliance with OWASP Top 10
- ✓ Industry-standard tools
- ✓ Comprehensive testing
- ✓ Secure deployment

## Emergency Backup

If live demo fails:
1. Show screenshots (prepare beforehand)
2. Explain what would happen
3. Focus on architecture and design
4. Answer questions about implementation

## Contact

For questions during presentation:
- Take time to think
- If unsure, say "That's a great question, let me think about it"
- Be honest about limitations
