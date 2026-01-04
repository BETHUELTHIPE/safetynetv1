# SafetyNet Reporting System on DockerHub

The SafetyNet Reporting System Docker image is now available on DockerHub.

## Docker Pull Command

```
docker pull bethuelm/safetynet_reporting:v1.0
```

Or to get the latest version:

```
docker pull bethuelm/safetynet_reporting:latest
```

## Running the SafetyNet Reporting System

1. Pull the image from DockerHub:

```
docker pull bethuelm/safetynet_reporting:latest
```

2. Create a docker-compose.yml file with the following content:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    restart: always
    environment:
      POSTGRES_DB: safetynet_db
      POSTGRES_USER: safetynet_user
      POSTGRES_PASSWORD: safetynet_password
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    ports:
      - "5433:5432"

  redis:
    image: redis:alpine
    restart: always
    ports:
      - "6380:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  web:
    image: bethuelm/safetynet_reporting:latest
    restart: always
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    environment:
      - DJANGO_SETTINGS_MODULE=cpfcrimereportingsystem.settings
      - DEBUG=True
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_DB=safetynet_db
      - POSTGRES_USER=safetynet_user
      - POSTGRES_PASSWORD=safetynet_password
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_SUPERUSER_USERNAME=admin
      - DJANGO_SUPERUSER_EMAIL=admin@safetynet.com
      - DJANGO_SUPERUSER_PASSWORD=SafeAdmin123
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "8081:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/app/static:ro
      - media_volume:/app/media:ro
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

3. Create an nginx directory and nginx.conf file:

```
mkdir -p nginx
```

4. Create nginx/nginx.conf with the following content:

```nginx
server {
    listen 80;
    server_name localhost;
    client_max_body_size 100M;

    location /static/ {
        alias /app/static/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_read_timeout 120s;
    }
}
```

5. Start the application:

```
docker-compose up -d
```

6. Access the application at http://localhost:8081

## Access Details

- **Web Interface**: http://localhost:8081
- **Admin Interface**: http://localhost:8081/admin
  - Username: admin
  - Password: SafeAdmin123

## Image Information

- **Repository**: bethuelm/safetynet_reporting
- **Tags**: 
  - v1.0 - First release
  - latest - Most recent version
