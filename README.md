# SafetyNet Reporting System

This is a comprehensive SafetyNet Reporting System designed for communities to report and track incidents.

## Features

- User authentication and authorization
- Incident reporting with media attachments
- Data analytics and visualization
- Community alerts and notifications
- Mobile-friendly responsive interface

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation & Running

1. Clone this repository
2. Navigate to the project directory:
   ```
   cd SafetyNetReporting
   ```
3. Start the application using Docker Compose:
   ```
   docker-compose up -d
   ```
4. Access the application at http://localhost:8081

## Access Details

- **Web Interface**: http://localhost:8081
- **Admin Interface**: http://localhost:8081/admin
  - Username: admin
  - Password: SafeAdmin123

## System Architecture

- **Web Server**: Nginx
- **Application**: Django with Gunicorn
- **Database**: PostgreSQL
- **Cache & Message Broker**: Redis

## Development

To run the application in development mode:

```
docker-compose up
```

## License

This project is proprietary software.

## Support

For technical support, please contact support@safetynet.com
# -SafetyNetReporting-
