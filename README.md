# 🛍️ Sokoni — E‑Commerce Web App with End‑to‑End DevOps Pipeline

**Sokoni** (Swahili for "marketplace") is a production-ready Django e‑commerce application demonstrating a complete DevOps lifecycle: containerization, CI/CD automation, Infrastructure as Code, monitoring & observability, and comprehensive DevSecOps practices.

This project serves as the practical capstone for my 12-week Starter DevOps Program at the Nairobi DevOps Community, showcasing the transition from learning to hands-on application of industry-standard DevOps tools and practices.

---

## 📚 Table of Contents

- [Project Overview](#project-overview)
- [Architecture Diagram](#architecture-diagram)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Local Development](#local-development)
- [Configuration (Environment Variables)](#configuration-environment-variables)
- [CI/CD Pipeline](#cicd-pipeline)
- [Containerization & Docker Registry](#containerization--docker-registry)
- [Infrastructure as Code (Terraform)](#infrastructure-as-code-terraform)
- [Monitoring & Observability](#monitoring--observability)
- [DevSecOps](#devsecops)
- [Live Demo](#live-demo)
- [Deliverables Checklist](#deliverables-checklist)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## 🎯 Project Overview

**Features:**
- User authentication & authorization
- Product catalog with categories, tags, and search
- Shopping cart with session management
- Coupon & discount system
- Order processing & tracking
- Payment integration (Paystack)
- Wishlist functionality
- Admin dashboard for inventory management

**DevOps Highlights:**
- Multi-stage Docker builds with security best practices
- GitHub Actions CI/CD with automated testing, security scanning, and deployment
- Terraform-managed AWS infrastructure (ECS Fargate, RDS, ALB, VPC)
- AWS Managed Prometheus + Grafana for monitoring
- Comprehensive security scanning (Trivy, CodeQL, SonarQube, OWASP ZAP)
- Secret management via AWS Secrets Manager & SSM Parameter Store

---

## 🏗️ Architecture Diagram
#### Production Environment Architecture
![Production Architecture](./docs/prod.png)

#### Staging Environment Architecture
![Production Architecture](./docs/staging.png)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.2, Python 3.12, Gunicorn |
| **Database** | PostgreSQL (RDS in production) |
| **Containerization** | Docker (multi-stage builds), Docker Compose |
| **Orchestration** | AWS ECS Fargate |
| **Infrastructure** | Terraform (Terraform Cloud workflow) |
| **CI/CD** | GitHub Actions |
| **Monitoring** | django-prometheus, AWS Managed Prometheus, AWS OTel Collector, Grafana |
| **Security Scanning** | Trivy, CodeQL, SonarQube, OWASP ZAP, detect-secrets, GitLeaks |
| **Secret Management** | AWS Secrets Manager, SSM Parameter Store, detect-secrets |
| **Load Balancing** | AWS Application Load Balancer (ALB) |
| **Logging** | CloudWatch Logs |
| **Payments** | Paystack API |

---

## 📁 Repository Structure

```
sokoni/
├── .github/
│   ├── workflows/          # GitHub Actions CI/CD pipelines
│   │   ├── pipeline.yml    # Main deployment pipeline
│   │   ├── sast.yml        # Static Application Security Testing
│   │   ├── dast.yml        # Dynamic Application Security Testing
│   │   ├── trivy.yml       # Container vulnerability scanning
│   │   ├── lint.yml        # Code linting
│   │   └── branch-rules.yml # Branch protection enforcement
│   └── infra/              # Terraform Infrastructure as Code
│       ├── prod/           # Production environment
│       └── staging/        # Staging environment
├── accounts/               # User authentication app
├── cart/                   # Shopping cart app
├── coupons/                # Discount coupons app
├── docs/                   # Additional documentation
├── orders/                 # Order processing app
├── payments/               # Payment integration app
├── products/               # Product catalog app
├── sokoni/                 # Django project settings
├── static/                 # Static assets
├── templates/              # Django templates
├── wishlist/               # Wishlist app
├── .dockerignore
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml # Linting config file
├── .secrets.baseline       # Baseline for secret detection
├── compose.yaml            # Docker Compose for local dev
├── Dockerfile              # Multi-stage production image
├── entrypoint.sh           # Container entrypoint script
├── LICENSE
├── manage.py
├── README.md
├── requirements.txt        # Python dependencies
└── sonar-project.properties # SonarQube config file
```

---

## 💻 Local Development

### Option A: Python Virtual Environment

**Prerequisites:**
- Python 3.12+
- PostgreSQL 14+

**Setup:**

```bash
# 1. Clone the repository
git clone https://github.com/victorgpt0/sokoni.git
cd sokoni

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your database credentials and API keys

# 5. Run database migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. (Optional) Seed database with sample data
python manage.py seed_dev          # Full dataset
python manage.py seed_dev --small  # Smaller dataset

# 8. Run tests
python manage.py test

# 9. Start development server
python manage.py runserver
```

**Access:**
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin
- Metrics endpoint: http://localhost:8000/metrics

---

### Option B: Docker Compose

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+

**Setup:**

```bash
# 1. Clone the repository
git clone https://github.com/victorgpt0/sokoni.git
cd sokoni

# 2. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 3. Start services
docker compose up --build

# 4. Run migrations (first time only)
docker compose exec server python manage.py migrate

# 5. Create superuser (first time only)
docker compose exec server python manage.py createsuperuser

# 6. (Optional) Seed database
docker compose exec server python manage.py seed_dev
```

**Access:**
- Application: http://localhost:8000

**Note:** To enable multi-service setup with PostgreSQL, uncomment the database service in `compose.yaml`.

---

## ⚙️ Configuration (Environment Variables)

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sokoni

# Django Security
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Paystack Payment Gateway
PAYSTACK_PUBLIC_KEY=pk_xxxxxx
PAYSTACK_SECRET_KEY=sk_xxxxxx
```

**Production (AWS):**
- `DATABASE_URL` is stored in **SSM Parameter Store** (`/sokoni/{env}/database_url`)
- Grafana admin password is stored in **AWS Secrets Manager**
- All secrets are injected into ECS tasks via IAM roles

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **pipeline.yml** | Push to `main`, `staging` | Run Django Tests, Build, Scan and Push Docker Image to AWS ECR, Terraform Cloud deployment |
| **sast.yml** | Push/PR to `main`, `staging`; Weekly schedule | CodeQL, SonarQube, GitLeaks scanning |
| **dast.yml** | Push/PR to `main`, `staging`; Weekly schedule | OWASP ZAP dynamic security testing |
| **trivy.yml** | Weekly schedule | Docker image vulnerability scanning |
| **lint.yml** | PRs to `main`, `staging` | Code formatting & linting checks |
| **branch-rules.yml** | PRs to `main` | Enforce PRs from `staging` only |

### Pipeline Stages (pipeline.yml)

```mermaid
graph LR
    A[Code Push] --> B[Run Tests]
    B --> C[Build Docker Image]
    C --> D[Trivy Scan]
    D --> E[Push to Registry]
    E --> F[Update TF Variable]
    F --> G[Terraform Plan]
    G --> H[Terraform Apply]
    H --> I[Deploy to ECS]
```

**Required GitHub Secrets:**
- `TF_API_TOKEN` — Terraform Cloud API token
- `SONAR_ORG` — SonarQube organization name
- `SONAR_TOKEN` — SonarQube authentication
- `SONAR_PROJECT_KEY` — SonarQube Project Key
- `TEST_DB_URL` — Test database connection string
- `AWS_ECR_ROLE_ARN` — IAM role for ECR access
- `AWS_TF_ROLE_ARN` — IAM role for TF access
- `TF_MAIN_IMAGE_VAR_ID` — Terraform Cloud Production Docker Image Variable ID
- `TF_MAIN_WORKSPACE_ID` — Terraform Cloud Production Workspace ID
- `TF_STAGING_IMAGE_VAR_ID` — Terraform Cloud Staging Docker Image Variable ID
- `TF_STAGING_WORKSPACE_ID` — Terraform Cloud Staging Workspace ID

---

## 🐳 Containerization & Docker Registry

### Dockerfile Highlights
[View Dockerfile](./Dockerfile)


- **Multi-stage build** for optimized image size
- **Non-root user** (`appuser`) for security
- **Health checks** on port 8000
- **Gunicorn** WSGI server with 4 workers
- **Static file collection** via `entrypoint.sh`

### Build & Push

```bash
# Build locally
docker build -t victorgpt0/sokoni:latest .

# Run locally
docker run -p 8000:8000 --env-file .env victorgpt0/sokoni:latest

# Push to DockerHub
docker login
docker push victorgpt0/sokoni:latest

# Or push to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag victorgpt0/sokoni:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/sokoni:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/sokoni:latest
```

---

## Infrastructure as Code (Terraform)

### Overview

Infrastructure is defined in `.github/infra/` with separate environments for **staging** and **production**.

### Terraform Cloud Workflow

- **Organization:** `victorgpt0`
- **Workspaces:**
  - `sokoni-production` (main branch)
  - `sokoni-staging` (staging branch)
- **Execution:** Remote execution via Terraform Cloud
- **State:** Managed remotely in Terraform Cloud

### Provisioned Resources

**Networking:**
- VPC with public and private subnets across 2 AZs
- Internet Gateway
- Security Groups for ALB, ECS, RDS, Grafana

**Compute:**
- ECS Fargate cluster
- ECS service for Django app (with auto-scaling capability)
- Application Load Balancer (ALB) with HTTPS support

**Database:**
- RDS PostgreSQL instance (Multi-AZ optional)
- Automated backups

**Monitoring:**
- AWS Managed Prometheus (AMP) workspace
- AWS OTel Collector sidecar for metrics collection
- Grafana on ECS with IAM permissions to query AMP

**Secrets & Configuration:**
- SSM Parameter Store for `DATABASE_URL`
- Secrets Manager for Grafana admin password
- IAM roles with least-privilege policies

**Logging:**
- CloudWatch Log Groups for ECS tasks

### Terraform Variables

Key variable in `variables.tf`:
- `container_image` — Docker image URI (set via Terraform Cloud workspace variable)

### Apply Infrastructure

```bash
# Local apply (requires AWS credentials)
cd .github/infra/prod
terraform init
terraform plan -var="container_image=<your-image-uri>"
terraform apply -var="container_image=<your-image-uri>"

# CI/CD applies automatically via GitHub Actions + Terraform Cloud
```

---

## 📊 Monitoring & Observability

### Application Metrics

**Django Prometheus Integration:**
- Middleware: `django_prometheus.middleware.PrometheusBeforeMiddleware` & `PrometheusAfterMiddleware`
- Metrics endpoint: `/metrics`
- Custom metrics: `sokoni/metrics.py`

**Exposed Metrics:**
- HTTP request duration & count
- Database query performance
- Cache hit/miss rates
- Custom business metrics

### Infrastructure Metrics

**AWS OTel Collector Sidecar:**
- Collects metrics from Django app
- Pushes to AWS Managed Prometheus via remote_write
- IAM role: `sokoni-production-amp-remote-write-role`

**AWS Managed Prometheus:**
- Workspace: `sokoni-prometheus-production-workspace`
- Query endpoint exposed for Grafana

**Grafana:**
- Runs on ECS Fargate
- Connects to AMP with IAM authentication
- Admin credentials in Secrets Manager
- Access via ECS service public IP on port 3000

### Logging

**CloudWatch Logs:**
- Log group: `/ecs/sokoni-{env}`
- Streams:
  - `ecs` — Django application logs
  - `adot` — OTel collector logs
  - `grafana` — Grafana logs
  - `migrations` — Database migration logs

---

## 🔒 DevSecOps

### Vulnerability Scanning

**Trivy (Container Images):**
- Scheduled weekly scans
- Scans for OS packages and application dependencies
- Severity levels: CRITICAL, HIGH
- Results uploaded as SARIF artifacts

**CodeQL (SAST):**
- Static analysis for Python code
- Detects security vulnerabilities and code quality issues
- Runs on push/PR to `main` and `staging`

**SonarQube (SAST):**
- Code quality and security analysis
- Configured via `sonar-project.properties`
- Organization: `victorgpt0`

**OWASP ZAP (DAST):**
- Dynamic security testing against running container
- Baseline scan for common web vulnerabilities
- Reports uploaded as artifacts

**GitLeaks:**
- Scans commit history for leaked secrets
- Runs in CI on every push

### Secret Management

**Pre-commit Hooks:**
- `detect-secrets` scans for hardcoded secrets before commit
- Baseline file: `.secrets.baseline`
- Also checks for AWS credentials

**Runtime Secrets:**
- AWS Secrets Manager for sensitive credentials
- SSM Parameter Store for configuration
- No secrets in environment variables or code

### Security Best Practices

✅ Non-root container user  
✅ Multi-stage Docker builds  
✅ Minimal base images (`python:3.12-slim`)  
✅ Security group rules with least privilege  
✅ HTTPS enforcement via ALB  
✅ Database encryption at rest (RDS)  
✅ IAM roles with scoped policies  
✅ Regular dependency updates  
✅ Automated security scanning in CI/CD  

---

## 🌐 Live Demo

**Production URL:** [sokoni.dev](https://sokoni.dev)

---

## ✅ Deliverables Checklist

| Deliverable | Status | Location |
|------------|--------|----------|
| ✅ **Django E-commerce App** | Complete | Root directory |
| ✅ **Source Control (GitHub)** | Complete | https://github.com/victorgpt0/sokoni |
| ✅ **Branching Strategy** | Complete | `main` ← `staging` ← `development` |
| ✅ **Dockerfile** | Complete | `Dockerfile` |
| ✅ **Docker Compose** | Complete | `compose.yaml` (Postgres commented) |
| ✅ **CI/CD Pipeline** | Complete | `.github/workflows/pipeline.yml` |
| ✅ **Run Tests in CI** | Complete | `.github/workflows/pipeline.yml` |
| ✅ **Build & Push Image** | Complete | `.github/workflows/pipeline.yml` |
| ✅ **Trivy Security Scan** | Complete | `.github/workflows/trivy.yml` |
| ✅ **Terraform IaC** | Complete | `.github/infra/` |
| ✅ **AWS Infrastructure** | Complete | ECS, RDS, ALB, VPC, Security Groups |
| ✅ **Prometheus Integration** | Complete | django-prometheus + AMP |
| ✅ **Grafana Dashboard** | Complete | ECS service in `monitoring.tf` |
| ✅ **Secret Management** | Complete | Secrets Manager, SSM, detect-secrets |
| ✅ **SAST (CodeQL, SonarQube)** | Complete | `.github/workflows/sast.yml` |
| ✅ **DAST (OWASP ZAP)** | Complete | `.github/workflows/dast.yml` |
| ✅ **Comprehensive README** | Complete | This file |
| ✅ **Architecture Diagram** | Complete | See above |
| ✅ **Live Demo Link** | Complete | https://sokoni.dev |
| ⚠️ **Monitoring Screenshots** | Pending |  |

**Legend:**
- ✅ Complete
- ⚠️ Partial / Pending

---

## 🤝 Contributing

### Branching Strategy

```
main (production)
  ↑
staging (pre-production)
  ↑
development (active development)
  ↑
feature/* (feature branches)
```

### Contribution Workflow

1. **Fork** the repository
2. **Create** a feature branch from `development`:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Install** pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```
4. **Make** your changes and commit:
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push** to your fork:
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open** a Pull Request to `development`

### Code Quality Standards

- All code must pass `pre-commit` hooks (Black, isort, detect-secrets)
- Write tests for new features
- Maintain test coverage above 80%
- Follow Django best practices
- Document complex logic

---

## 🙏 Acknowledgments

- **Nairobi DevOps Community** - For the 12-week Starter DevOps Program
- **Django Community** - For the excellent web framework
- **Tailwind CSS** - For the utility-first CSS framework
- **Paystack** - For awesome payment integration
- **AWS** - For well documented cloud infrastructure
- **HashiCorp** - For Terraform Cloud
- **Aqua Security** - For Trivy
- **OWASP** - For ZAP security scanner

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

## 📞 Support

For questions or issues:
- **GitHub Issues:** https://github.com/victorgpt0/sokoni/issues
- **Documentation:** See `docs/` directory
- **Seeding Guide:** `docs/SEEDING.md`
- **Docker Guide:** `docs/DOCKER.md`

---

**Built with ❤️ for the Kenyan e-commerce ecosystem**

*Demonstrating production-ready DevOps practices from code to cloud.*
