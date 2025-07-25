# 🚀 VPS Deployment Guide

Automated deployment using GitHub Actions + DockerHub + Docker.

## 📋 Prerequisites

- VPS with SSH access and sudo privileges
- GitHub repository with this code
- DockerHub account
- SSH key pair for VPS access

## 🔧 Setup

### 1. DockerHub Setup
- Create repository: `work-logger` at [hub.docker.com](https://hub.docker.com)
- Generate access token: Account Settings → Security → Access Tokens

### 2. SSH Setup
```bash
# Generate key (if needed)
ssh-keygen -t ed25519 -C "github-actions@work-logger"

# Add to VPS
ssh-copy-id user@your-vps-ip

# Test connection
ssh user@your-vps-ip
```

### 3. GitHub Secrets
Add these secrets in: Repository → Settings → Secrets and variables → Actions

| Secret | Description | Example |
|--------|-------------|---------|
| `DOCKERHUB_USERNAME` | DockerHub username | `your-username` |
| `DOCKERHUB_TOKEN` | DockerHub access token | `dckr_pat_1234...` |
| `VPS_HOST` | VPS IP/domain | `192.168.1.100` |
| `VPS_USER` | VPS username | `ubuntu` |
| `VPS_SSH_KEY` | SSH private key | *Full ED25519 private key* |
| `JIRA_URL` | Jira instance URL | `https://company.atlassian.net` |
| `JIRA_USERNAME` | Jira username | `your.email@company.com` |
| `JIRA_SVC_ACCOUNT` | Service account | `service.account@company.com` |
| `JIRA_API_TOKEN` | API token | `ATATT3xFfGF0...` |
| `JIRA_PROJECT` | Project key | `PROJECT_KEY` |
| `SYSTEM_USERNAME` | System username | `your_username` |
| `SYSTEM_PASSWORD` | System password | `your_password` |

## 🚀 Deploy

```bash
git add .
git commit -m "PROJECT_KEY-XXX: Add GitHub CI/CD deployment"
git push origin main
```

Monitor deployment in GitHub Actions tab.

## 📊 Management

### VPS Commands
```bash
# SSH to VPS
ssh user@your-vps-ip
cd /opt/work-logger

# Container operations
docker compose ps                    # Status
docker compose logs -f               # Logs
docker compose restart               # Restart
docker compose pull && docker compose up -d  # Update

# Manual execution
docker exec work-logger python src/loghours.py --today

# Check cron jobs
docker exec work-logger crontab -l

# Application logs
docker exec work-logger tail -f /app/logs/cronjob.log
```

### Local Testing
```bash
# Test locally
python src/loghours.py --today

# Test with Docker
docker build -t work-logger .
docker run --rm -it work-logger python src/loghours.py --today
```

## 🛠️ Troubleshooting

### Common Issues

**SSH connection fails:**
- Check `VPS_SSH_KEY` contains complete private key
- Verify `VPS_HOST` and `VPS_USER` are correct
- Test: `ssh user@vps-ip`

**Docker image pull fails:**
- Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`
- Check DockerHub repository exists

**Container fails to start:**
- Check VPS resources (RAM, disk)
- Verify Docker/Docker Compose installed
- Check logs: `docker logs work-logger`

**Cron not working:**
- Check: `docker exec work-logger crontab -l`
- Verify container running: `docker ps | grep work-logger`
- Check logs: `docker exec work-logger tail -f /app/logs/cronjob.log`

### Debug Commands
```bash
# SSH to VPS and check status
ssh user@your-vps-ip
cd /opt/work-logger
docker logs work-logger --tail=50
docker inspect work-logger | jq '.[0].State.Health'
docker exec work-logger python src/loghours.py --today
```

## 🔄 CI/CD Pipeline

**Triggers:** Push to main, PRs, manual dispatch

**Stages:**
1. **Test:** Python + Playwright setup, import testing
2. **Build:** Multi-platform Docker build, push to DockerHub
3. **Deploy:** SSH to VPS, pull image, deploy with docker compose

**Features:**
- Multi-platform images (AMD64 + ARM64)
- Automatic container health monitoring
- JSON log rotation
- Cron job runs Fridays at 10 AM

## 🔒 Security

- SSH access only (no public ports)
- Container isolation with non-root user
- Encrypted secrets via GitHub
- Secure SSH + HTTPS transmission

## 📈 Updates

**Code changes:** Push to main → automatic deployment
**Environment:** Update GitHub Secrets, restart container
**Manual update:** `docker compose pull && docker compose up -d`

---

**Stack:** VPS + Docker + DockerHub + GitHub Actions