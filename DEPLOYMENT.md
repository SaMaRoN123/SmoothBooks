# SmoothBooks Deployment Guide

This guide covers different deployment options for SmoothBooks, from local development to production environments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Considerations](#production-considerations)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [SSL/HTTPS Setup](#sslhttps-setup)
- [Monitoring and Logging](#monitoring-and-logging)

## Local Development

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/samaron123/SmoothBooks.git
   cd SmoothBooks
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Start the application**:
   ```bash
   # Windows
   start.bat
   
   # Unix/Linux/macOS
   ./start.sh
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/samaron123/SmoothBooks.git
   cd SmoothBooks
   ```

2. **Set environment variables**:
   ```bash
   cp backend/env.example .env
   # Edit .env with your production values
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:5000

### Manual Docker Build

1. **Build the backend image**:
   ```bash
   docker build -t smoothbooks-backend .
   ```

2. **Build the frontend image**:
   ```bash
   cd frontend
   docker build -t smoothbooks-frontend .
   ```

3. **Run the containers**:
   ```bash
   # Backend
   docker run -d -p 5000:5000 --name smoothbooks-backend smoothbooks-backend
   
   # Frontend
   docker run -d -p 80:80 --name smoothbooks-frontend smoothbooks-frontend
   ```

## Cloud Deployment

### Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create smoothbooks-app
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set JWT_SECRET_KEY=your-jwt-secret
   heroku config:set DATABASE_URL=postgresql://...
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

### AWS (EC2 + RDS)

1. **Launch EC2 instance**:
   - Use Ubuntu 20.04 LTS
   - Configure security groups for ports 22, 80, 443, 5000

2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose nginx
   ```

3. **Clone and deploy**:
   ```bash
   git clone https://github.com/samaron123/SmoothBooks.git
   cd SmoothBooks
   docker-compose up -d
   ```

4. **Configure Nginx** (optional):
   ```bash
   sudo nano /etc/nginx/sites-available/smoothbooks
   sudo ln -s /etc/nginx/sites-available/smoothbooks /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

### Google Cloud Platform

1. **Create a project** and enable APIs:
   ```bash
   gcloud config set project smoothbooks-project
   gcloud services enable compute.googleapis.com
   ```

2. **Deploy with Cloud Run**:
   ```bash
   # Backend
   gcloud run deploy smoothbooks-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   
   # Frontend
   cd frontend
   gcloud run deploy smoothbooks-frontend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Production Considerations

### Security

1. **Environment Variables**:
   - Use strong, unique secret keys
   - Store sensitive data in environment variables
   - Never commit `.env` files to version control

2. **Database Security**:
   - Use strong passwords
   - Enable SSL connections
   - Restrict database access

3. **HTTPS/SSL**:
   - Always use HTTPS in production
   - Configure SSL certificates (Let's Encrypt)
   - Enable HSTS headers

### Performance

1. **Database Optimization**:
   - Use connection pooling
   - Implement database indexing
   - Consider read replicas for high traffic

2. **Caching**:
   - Implement Redis for session storage
   - Use CDN for static assets
   - Enable browser caching

3. **Load Balancing**:
   - Use multiple application instances
   - Configure health checks
   - Implement auto-scaling

### Monitoring

1. **Application Monitoring**:
   - Set up error tracking (Sentry)
   - Monitor application performance
   - Track user metrics

2. **Infrastructure Monitoring**:
   - Monitor server resources
   - Set up alerts for critical issues
   - Track database performance

## Environment Configuration

### Backend Environment Variables

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_ENV=production
FLASK_DEBUG=False

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/smoothbooks

# CORS Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration (for future features)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Frontend Environment Variables

```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
```

## Database Setup

### SQLite (Development)

SQLite is used by default for development. The database file is created automatically.

### PostgreSQL (Production)

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create database and user**:
   ```sql
   CREATE DATABASE smoothbooks;
   CREATE USER smoothbooks_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE smoothbooks TO smoothbooks_user;
   ```

3. **Update DATABASE_URL**:
   ```env
   DATABASE_URL=postgresql://smoothbooks_user:your_password@localhost/smoothbooks
   ```

### Database Migration

For production database migrations:

1. **Install Alembic**:
   ```bash
   pip install alembic
   ```

2. **Initialize Alembic**:
   ```bash
   cd backend
   alembic init migrations
   ```

3. **Create and run migrations**:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

## SSL/HTTPS Setup

### Let's Encrypt (Free SSL)

1. **Install Certbot**:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain SSL certificate**:
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

3. **Auto-renewal**:
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Logging

### Application Logging

Configure logging in your Flask application:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/smoothbooks.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SmoothBooks startup')
```

### Health Checks

Implement health check endpoints:

```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

### Backup Strategy

1. **Database Backups**:
   ```bash
   # PostgreSQL
   pg_dump smoothbooks > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # SQLite
   cp smoothbooks.db backup_$(date +%Y%m%d_%H%M%S).db
   ```

2. **Automated Backups**:
   ```bash
   # Add to crontab
   0 2 * * * /path/to/backup-script.sh
   ```

---

For more information, see the [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md) files.
