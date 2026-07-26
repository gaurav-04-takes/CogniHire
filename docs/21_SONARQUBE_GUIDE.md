# 21 — SonarQube Guide

CogniHire uses SonarQube for static code analysis, code quality checks, and tracking test coverage.

**Configuration File**: `sonar-project.properties`

## SonarQube Properties

```properties
sonar.projectKey=cognihire
sonar.projectName=CogniHire
sonar.projectVersion=1.0
sonar.sourceEncoding=UTF-8

sonar.sources=backend,frontend
sonar.tests=backend/tests

sonar.python.version=3.11
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml
```

## Running Local Analysis

1. **Start a local SonarQube instance** (requires Docker):
   ```bash
   docker run -d --name sonarqube -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true -p 9000:9000 sonarqube:latest
   ```

2. **Generate the coverage report**:
   ```bash
   pytest --cov=backend --cov-report=xml --junitxml=test-results.xml
   ```

3. **Run the SonarScanner**:
   *(Requires SonarScanner CLI to be installed on your machine)*
   ```bash
   sonar-scanner \
     -Dsonar.login="your_project_token" \
     -Dsonar.host.url="http://localhost:9000"
   ```

## Exclusions
The following paths are excluded from coverage and analysis to prevent false positives:
- `backend/tests/**`
- `**/migrations/**`
- `venv/**`, `.venv/**`
- `data/**`, `uploads/**`, `chroma_db/**`
- Cache directories (`__pycache__`, `.pytest_cache`, `.mypy_cache`)

---

> **Next**: [Performance Guide](22_PERFORMANCE_GUIDE.md)
