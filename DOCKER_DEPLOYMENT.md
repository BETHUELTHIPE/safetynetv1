# Docker Deployment Guide for CPF Crime Reporting System

This guide provides step-by-step instructions for deploying the CPF Crime Reporting System using Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your server
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your server
- Basic knowledge of Docker and containerization
- A domain name (optional, for production deployment)

## Deployment Steps

### 1. Set Up Environment Variables

First, create a `.env` file by copying the example file:

```bash
cp .env.example .env
```

Edit the `.env` file and update the following variables:
- `SECRET_KEY`: Change to a secure random string
- `DJANGO_ALLOWED_HOSTS`: Add your domain name or IP address
- `POSTGRES_PASSWORD`: Set a secure database password
- `EMAIL_*` settings: Configure with your SMTP provider details
- `DJANGO_SUPERUSER_*`: Set secure credentials for the admin user
- `PGADMIN_DEFAULT_*`: Set secure credentials for pgAdmin

### 2. Build and Start the Docker Containers

```bash
# Build the images
docker-compose build

# Start all services in detached mode
docker-compose up -d
```

This will start the following services:
- PostgreSQL database
- Redis for caching and Celery broker
- Django web application
- Celery worker for background tasks
- Celery Beat for scheduled tasks
- Nginx web server for serving the application
- pgAdmin for database management (optional)

### 3. Verify the Deployment

Check if all containers are running properly:

```bash
docker-compose ps
```

All services should be in the "Up" state. If any service is not running, check the logs:

```bash
docker-compose logs <service_name>
```

For example, to check the web application logs:

```bash
docker-compose logs web
```

### 4. Access the Application

- Main application: http://your-server-ip/ or http://your-domain.com/
- Admin interface: http://your-server-ip/admin/ or http://your-domain.com/admin/
- pgAdmin: http://your-server-ip:5050 or http://your-domain.com:5050

### 5. SSL/TLS Configuration (For Production)

For a production environment, you should enable HTTPS. Follow these steps:

1. Obtain SSL/TLS certificates for your domain
2. Place the certificates in the `nginx/ssl/` directory:
   - `cert.pem` (certificate file)
   - `key.pem` (private key file)

3. Edit `nginx/nginx.conf`:
   - Uncomment the HTTPS server block
   - Uncomment the redirect from HTTP to HTTPS in the HTTP server block

4. Update `.env` file:
   - Set `SECURE_SSL_REDIRECT=True`
   - Ensure `CSRF_TRUSTED_ORIGINS` includes your HTTPS domain

5. Restart the Nginx service:
   ```bash
   docker-compose restart nginx
   ```

### 6. Docker Compose Commands

Here are some useful Docker Compose commands for managing the application:

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop all services and remove volumes (WARNING: this will delete all data)
docker-compose down -v

# Restart a specific service
docker-compose restart <service_name>

# View logs of all services
docker-compose logs

# View logs of a specific service
docker-compose logs <service_name>

# Follow logs of a specific service
docker-compose logs -f <service_name>

# Run a Django management command
docker-compose exec web python manage.py <command>

# Create a superuser
docker-compose exec web python manage.py createsuperuser

# Enter a shell in the web container
docker-compose exec web /bin/bash
```

### 7. Backups

To back up the PostgreSQL database:

```bash
# Create a backup
docker-compose exec db pg_dump -U postgres cpfcrimereportingsystem > backup_$(date +%Y-%m-%d_%H-%M-%S).sql

# Restore a backup
cat backup_file.sql | docker-compose exec -T db psql -U postgres cpfcrimereportingsystem
```

To back up media files:

```bash
# Create a directory for backups
mkdir -p backups

# Back up media files
docker cp $(docker-compose ps -q web):/app/media ./backups/media_$(date +%Y-%m-%d_%H-%M-%S)
```

### 8. Scaling (Optional)

If needed, you can scale the web application and Celery worker services:

```bash
# Scale web service to 3 instances
docker-compose up -d --scale web=3

# Scale Celery worker service to 2 instances
docker-compose up -d --scale celery_worker=2
```

Note: When scaling the web service, you'll need to configure Nginx to load balance between the instances. The included Nginx configuration already handles this.

### 9. Monitoring (Optional)

Consider adding monitoring tools:

- [Prometheus](https://prometheus.io/) for metrics collection
- [Grafana](https://grafana.com/) for metrics visualization
- [ELK Stack](https://www.elastic.co/elastic-stack/) for log management

### 10. Troubleshooting

If you encounter issues, check the following:

1. Container status: `docker-compose ps`
2. Container logs: `docker-compose logs <service_name>`
3. Database connection: `docker-compose exec web python manage.py dbshell`
4. Redis connection: `docker-compose exec redis redis-cli ping`
5. Network connectivity: `docker-compose exec web ping redis`

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
