# Deployment Documentation for Citizen Registration System

## 1. System Overview

The Citizen Registration System is a comprehensive platform designed for the Nigerian state government to capture, manage, and analyze citizen data. The system enables local government officials to register citizens, issue unique identification cards, and provides the state government with analytical tools to make informed decisions based on demographic information.

### 1.1 Key Features

- User authentication with role-based access control
- Citizen data capture and management
- Unique ID generation and verification
- Family relationship tracking
- Reporting and analytics dashboard
- Data export capabilities
- ID card generation and printing

### 1.2 System Architecture

The system follows a three-tier architecture:

1. **Frontend**: React-based web application
2. **Backend**: Django REST API
3. **Database**: PostgreSQL database

## 2. System Requirements

### 2.1 Hardware Requirements

#### Production Server
- **CPU**: Minimum 4 cores, recommended 8 cores
- **RAM**: Minimum 8GB, recommended 16GB
- **Storage**: Minimum 500GB SSD, recommended 1TB SSD
- **Network**: 1Gbps Ethernet, redundant connections recommended

#### Database Server
- **CPU**: Minimum 4 cores, recommended 8 cores
- **RAM**: Minimum 16GB, recommended 32GB
- **Storage**: Minimum 1TB SSD, recommended 2TB SSD with RAID configuration
- **Network**: 1Gbps Ethernet, redundant connections recommended

### 2.2 Software Requirements

#### Production Server
- **Operating System**: Ubuntu Server 22.04 LTS
- **Web Server**: Nginx 1.18 or higher
- **Application Server**: Gunicorn 20.0 or higher
- **Runtime Environment**: Python 3.10, Node.js 18.x

#### Database Server
- **Operating System**: Ubuntu Server 22.04 LTS
- **Database**: PostgreSQL 14.x
- **Backup Software**: pgBackRest

#### Additional Software
- **Redis**: For caching and task queue
- **Celery**: For background task processing
- **Certbot**: For SSL certificate management
- **Supervisor**: For process management

## 3. Installation Guide

### 3.1 Database Server Setup

1. **Install PostgreSQL**:
   ```bash
   sudo apt update
   sudo apt install -y postgresql postgresql-contrib
   ```

2. **Configure PostgreSQL**:
   ```bash
   sudo -u postgres psql -c "CREATE USER citizen_app WITH PASSWORD 'Postgres';"
   sudo -u postgres psql -c "CREATE DATABASE citizen_db OWNER citizen_app;"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE citizen_db TO citizen_app;"
   ```

3. **Configure PostgreSQL for remote access** (if needed):
   Edit `/etc/postgresql/16/main/postgresql.conf`:
   ```
   listen_addresses = '*'
   ```
   
   Edit `/etc/postgresql/16/main/pg_hba.conf` to add:
   ```
   host    citizen_db    citizen_app    <app_server_ip>/32    md5
   ```

4. **Restart PostgreSQL**:
   ```bash
   sudo systemctl restart postgresql
   ```

### 3.2 Application Server Setup

1. **Install required packages**:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv nginx supervisor redis-server certbot python3-certbot-nginx
   ```

2. **Install Node.js**:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

3. **Create application directory**:
   ```bash
   sudo mkdir -p /opt/citizen_registration
   sudo chown $(whoami):$(whoami) /opt/citizen_registration
   ```

4. **Clone the repository**:
   ```bash
   git clone https://github.com/your-organization/citizen_registration_system.git /opt/citizen_registration
   cd /opt/citizen_registration
   ```

5. **Set up Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

6. **Install frontend dependencies and build**:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

7. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```
   DEBUG=False
   SECRET_KEY=your_secure_secret_key
   DATABASE_URL=postgres://citizen_app:secure_password@localhost:5432/citizen_db
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   REDIS_URL=redis://localhost:6379/0
   ```

8. **Initialize the database**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --no-input
   ```

9. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

### 3.3 Web Server Configuration

1. **Configure Gunicorn**:
   Create `/etc/supervisor/conf.d/citizen_registration.conf`:
   ```
   [program:citizen_registration]
   command=/opt/citizen_registration/venv/bin/gunicorn --workers 4 --bind unix:/opt/citizen_registration/citizen_registration.sock citizen_registration.wsgi:application
   directory=/opt/citizen_registration
   user=www-data
   group=www-data
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/citizen_registration/gunicorn.log
   ```

2. **Configure Celery**:
   Create `/etc/supervisor/conf.d/citizen_registration_celery.conf`:
   ```
   [program:citizen_registration_celery]
   command=/opt/citizen_registration/venv/bin/celery -A citizen_registration worker -l info
   directory=/opt/citizen_registration
   user=www-data
   group=www-data
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/citizen_registration/celery.log
   
   [program:citizen_registration_celery_beat]
   command=/opt/citizen_registration/venv/bin/celery -A citizen_registration beat -l info
   directory=/opt/citizen_registration
   user=www-data
   group=www-data
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/citizen_registration/celery_beat.log
   ```

3. **Create log directory**:
   ```bash
   sudo mkdir -p /var/log/citizen_registration
   sudo chown www-data:www-data /var/log/citizen_registration
   ```

4. **Configure Nginx**:
   Create `/etc/nginx/sites-available/citizen_registration`:
   ```
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;
   
       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /opt/citizen_registration;
       }
   
       location /media/ {
           root /opt/citizen_registration;
       }
   
       location / {
           include proxy_params;
           proxy_pass http://unix:/opt/citizen_registration/citizen_registration.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           client_max_body_size 10M;
       }
   }
   ```

5. **Enable the site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/citizen_registration /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Set up SSL with Certbot**:
   ```bash
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

7. **Start the application**:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start all
   ```

## 4. Backup and Recovery

### 4.1 Database Backup

1. **Install pgBackRest**:
   ```bash
   sudo apt install -y pgbackrest
   ```

2. **Configure pgBackRest**:
   Create `/etc/pgbackrest/pgbackrest.conf`:
   ```
   [global]
   repo1-path=/var/lib/pgbackrest
   
   [citizen_db]
   db-path=/var/lib/postgresql/14/main
   ```

3. **Set up daily backups**:
   Add to crontab:
   ```
   0 1 * * * sudo -u postgres pgbackrest --stanza=citizen_db backup
   ```

4. **Test backup**:
   ```bash
   sudo -u postgres pgbackrest --stanza=citizen_db backup
   ```

### 4.2 Application Backup

1. **Set up application code backup**:
   ```bash
   sudo mkdir -p /var/backups/citizen_registration
   ```

2. **Create backup script**:
   Create `/opt/citizen_registration/backup.sh`:
   ```bash
   #!/bin/bash
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR=/var/backups/citizen_registration
   
   # Backup code
   tar -czf $BACKUP_DIR/code_$TIMESTAMP.tar.gz -C /opt citizen_registration
   
   # Backup media files
   tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz -C /opt/citizen_registration/media .
   
   # Backup environment variables
   cp /opt/citizen_registration/.env $BACKUP_DIR/env_$TIMESTAMP
   
   # Remove backups older than 30 days
   find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
   find $BACKUP_DIR -name "env_*" -mtime +30 -delete
   ```

3. **Make script executable**:
   ```bash
   chmod +x /opt/citizen_registration/backup.sh
   ```

4. **Schedule backup**:
   Add to crontab:
   ```
   0 2 * * * /opt/citizen_registration/backup.sh
   ```

### 4.3 Recovery Procedures

#### Database Recovery

1. **Restore from pgBackRest**:
   ```bash
   sudo systemctl stop postgresql
   sudo -u postgres pgbackrest --stanza=citizen_db restore
   sudo systemctl start postgresql
   ```

#### Application Recovery

1. **Restore code**:
   ```bash
   sudo rm -rf /opt/citizen_registration
   sudo mkdir -p /opt/citizen_registration
   sudo tar -xzf /var/backups/citizen_registration/code_TIMESTAMP.tar.gz -C /opt
   ```

2. **Restore media files**:
   ```bash
   sudo rm -rf /opt/citizen_registration/media
   sudo mkdir -p /opt/citizen_registration/media
   sudo tar -xzf /var/backups/citizen_registration/media_TIMESTAMP.tar.gz -C /opt/citizen_registration/media
   ```

3. **Restore environment variables**:
   ```bash
   sudo cp /var/backups/citizen_registration/env_TIMESTAMP /opt/citizen_registration/.env
   ```

4. **Restart services**:
   ```bash
   sudo supervisorctl restart all
   sudo systemctl restart nginx
   ```

## 5. Scaling and High Availability

### 5.1 Horizontal Scaling

For increased load handling, the system can be horizontally scaled by:

1. **Adding application servers**:
   - Set up additional application servers following the installation guide
   - Configure a load balancer (e.g., HAProxy or AWS ELB) in front of the application servers
   - Ensure all application servers connect to the same database and Redis instances

2. **Database read replicas**:
   - Set up PostgreSQL read replicas for read-heavy operations
   - Configure the application to use read replicas for reporting queries

### 5.2 High Availability Setup

For production environments requiring high availability:

1. **Database High Availability**:
   - Set up PostgreSQL with streaming replication
   - Use pgpool-II for automatic failover
   - Consider using managed database services like AWS RDS or Azure Database for PostgreSQL

2. **Application High Availability**:
   - Deploy multiple application servers across different availability zones
   - Use a load balancer with health checks
   - Implement session persistence with Redis

3. **Monitoring and Alerting**:
   - Set up Prometheus and Grafana for monitoring
   - Configure alerts for system metrics and application health
   - Implement automated recovery procedures

## 6. Security Considerations

### 6.1 Network Security

1. **Firewall Configuration**:
   ```bash
   sudo ufw allow ssh
   sudo ufw allow http
   sudo ufw allow https
   sudo ufw allow from <database_server_ip> to any port 5432
   sudo ufw enable
   ```

2. **VPN Access**:
   - Consider setting up a VPN for administrative access
   - Restrict SSH access to VPN users only

### 6.2 Application Security

1. **Regular Updates**:
   ```bash
   # Update system packages
   sudo apt update
   sudo apt upgrade -y
   
   # Update application dependencies
   cd /opt/citizen_registration
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   
   # Update frontend dependencies
   cd frontend
   npm update
   npm run build
   ```

2. **Security Headers**:
   Add to Nginx configuration:
   ```
   add_header X-Content-Type-Options nosniff;
   add_header X-Frame-Options DENY;
   add_header X-XSS-Protection "1; mode=block";
   add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;";
   ```

3. **SSL Configuration**:
   Ensure strong SSL settings in Nginx:
   ```
   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_prefer_server_ciphers on;
   ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
   ssl_session_timeout 1d;
   ssl_session_cache shared:SSL:10m;
   ssl_stapling on;
   ssl_stapling_verify on;
   ```

### 6.3 Data Security

1. **Database Encryption**:
   - Enable PostgreSQL data-at-rest encryption
   - Use encrypted backups

2. **Personal Data Protection**:
   - Implement data access logging
   - Set up data retention policies
   - Ensure compliance with Nigerian data protection regulations

## 7. Monitoring and Maintenance

### 7.1 Monitoring Setup

1. **Install Prometheus and Grafana**:
   ```bash
   # Install Prometheus
   sudo apt install -y prometheus prometheus-node-exporter
   
   # Install Grafana
   sudo apt-get install -y apt-transport-https software-properties-common
   wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
   echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
   sudo apt update
   sudo apt install -y grafana
   ```

2. **Configure Django Prometheus integration**:
   Add to `requirements.txt`:
   ```
   django-prometheus
   ```
   
   Add to `INSTALLED_APPS`:
   ```python
   'django_prometheus',
   ```
   
   Add to `urls.py`:
   ```python
   path('metrics/', include('django_prometheus.urls')),
   ```

3. **Set up Grafana dashboards**:
   - Import PostgreSQL dashboard
   - Import Node Exporter dashboard
   - Create custom application dashboard

### 7.2 Log Management

1. **Centralized Logging**:
   ```bash
   # Install ELK stack or use a service like Papertrail
   sudo apt install -y filebeat
   
   # Configure filebeat to collect logs
   sudo nano /etc/filebeat/filebeat.yml
   ```

2. **Log Rotation**:
   Create `/etc/logrotate.d/citizen_registration`:
   ```
   /var/log/citizen_registration/*.log {
       daily
       missingok
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 www-data www-data
       sharedscripts
       postrotate
           supervisorctl restart citizen_registration citizen_registration_celery citizen_registration_celery_beat
       endscript
   }
   ```

### 7.3 Regular Maintenance Tasks

1. **Database Maintenance**:
   ```bash
   # Schedule VACUUM ANALYZE
   sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS pg_cron;"
   sudo -u postgres psql -c "SELECT cron.schedule('0 3 * * *', 'VACUUM ANALYZE citizen_db');"
   ```

2. **System Updates**:
   ```bash
   # Create update script
   cat > /opt/citizen_registration/update.sh << 'EOF'
   #!/bin/bash
   
   # Update system packages
   apt update
   apt upgrade -y
   
   # Update application
   cd /opt/citizen_registration
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --no-input
   
   # Restart services
   supervisorctl restart all
   EOF
   
   chmod +x /opt/citizen_registration/update.sh
   ```

3. **SSL Certificate Renewal**:
   ```bash
   # Certbot auto-renewal is installed by default
   # Test renewal process
   sudo certbot renew --dry-run
   ```

## 8. Troubleshooting

### 8.1 Common Issues and Solutions

#### Application Not Starting

1. **Check logs**:
   ```bash
   sudo tail -f /var/log/citizen_registration/gunicorn.log
   ```

2. **Check supervisor status**:
   ```bash
   sudo supervisorctl status
   ```

3. **Check permissions**:
   ```bash
   sudo chown -R www-data:www-data /opt/citizen_registration
   sudo chmod -R 755 /opt/citizen_registration
   ```

#### Database Connection Issues

1. **Check PostgreSQL status**:
   ```bash
   sudo systemctl status postgresql
   ```

2. **Check connection parameters**:
   ```bash
   sudo -u postgres psql -c "\l"
   ```

3. **Check firewall rules**:
   ```bash
   sudo ufw status
   ```

#### Slow Performance

1. **Check system resources**:
   ```bash
   htop
   ```

2. **Check database performance**:
   ```bash
   sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
   ```

3. **Check slow queries**:
   ```bash
   sudo -u postgres psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   ```

### 8.2 Support Contacts

- **Technical Support**: support@citizenregistration.gov.ng
- **Emergency Contact**: +234 800 123 4567
- **System Administrator**: admin@citizenregistration.gov.ng

## 9. User Training

### 9.1 Administrator Training

1. **System Administration**:
   - User management
   - Role and permission configuration
   - System monitoring
   - Backup and recovery procedures

2. **Data Management**:
   - Data import and export
   - Data validation
   - Data correction procedures

### 9.2 Data Entry Staff Training

1. **Citizen Registration**:
   - Data capture process
   - Document verification
   - ID card issuance
   - Data update procedures

2. **System Navigation**:
   - Dashboard usage
   - Search functionality
   - Report generation

### 9.3 Training Materials

- Administrator manual
- User manual
- Video tutorials
- Quick reference guides

## 10. Compliance and Regulations

### 10.1 Data Protection

The system complies with the Nigerian Data Protection Regulation (NDPR) by:

1. **Data Minimization**:
   - Only collecting necessary personal information
   - Implementing purpose limitation

2. **Security Measures**:
   - Encryption of sensitive data
   - Access controls and audit logging
   - Regular security assessments

3. **Data Subject Rights**:
   - Access to personal data
   - Correction of inaccurate data
   - Data portability

### 10.2 Audit Requirements

The system maintains comprehensive audit logs for:

1. **User Actions**:
   - Login/logout events
   - Data creation, modification, and deletion
   - Report generation and exports

2. **System Events**:
   - Configuration changes
   - Backup and recovery operations
   - Security-related events

## 11. Appendices

### 11.1 Database Schema

The database schema documentation is available in the project repository:
`/docs/database_schema.md`

### 11.2 API Documentation

API documentation is available at:
`https://your-domain.com/api/docs/`

### 11.3 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| DEBUG | Enable debug mode | False |
| SECRET_KEY | Django secret key | random_string_here |
| DATABASE_URL | Database connection string | postgres://user:pass@host:port/db |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts | example.com,www.example.com |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| EMAIL_HOST | SMTP server host | smtp.gmail.com |
| EMAIL_PORT | SMTP server port | 587 |
| EMAIL_HOST_USER | SMTP username | noreply@example.com |
| EMAIL_HOST_PASSWORD | SMTP password | password_here |
| EMAIL_USE_TLS | Use TLS for email | True |
