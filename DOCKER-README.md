# Authenticator.AI Docker Setup

This directory contains Docker configuration files to run the complete Authenticator.AI stack with SQL Server.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- At least 4GB RAM available for containers
- Ports 1433, 5174, and 8001 available

### Option 1: Automated Setup (Recommended)
```bash
# Make the setup script executable (if not already)
chmod +x docker-setup.sh

# Run the complete setup
./docker-setup.sh
```

### Option 2: Manual Setup
```bash
# Start the services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📋 Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5174 | React application |
| Backend API | http://localhost:8001 | Flask API server |
| API Documentation | http://localhost:8001/docs | Swagger UI |
| SQL Server | localhost:1433 | Database server |

### Database Credentials
- **Server**: localhost:1433
- **Username**: sa
- **Password**: SecurePassword123!
- **Databases**: auth_db, docs_db, clones_db

## 🛠️ Development Mode

For active development with hot reload:

```bash
# Use development configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Optional: Add database management UI
# Access CloudBeaver at http://localhost:8082
```

## 📁 File Structure

```
├── docker-compose.yml          # Main compose configuration
├── docker-compose.dev.yml      # Development overrides
├── docker-setup.sh            # Automated setup script
├── .env.example               # Environment variables template
├── backend/
│   ├── Dockerfile             # Backend container definition
│   └── .dockerignore         # Backend ignore rules
└── frontend/
    ├── Dockerfile             # Frontend container definition
    └── .dockerignore         # Frontend ignore rules
```

## 🔧 Configuration

1. **Environment Variables**: Copy `.env.example` to `.env` and customize
2. **Database Settings**: Modify `docker-compose.yml` if different credentials needed
3. **Port Configuration**: Change ports in compose file if conflicts exist

## 📊 Monitoring & Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f sqlserver

# Check service status
docker-compose ps

# Monitor resource usage
docker stats
```

## 🗄️ Data Persistence

- **SQL Server Data**: Stored in Docker volume `sqlserver_data`
- **Uploaded Files**: Mounted to `./backend/uploads`
- **Logs**: Mounted to `./backend/logs`

## 🔄 Common Commands

```bash
# Start services
./docker-setup.sh start

# Stop services
./docker-setup.sh stop

# Restart services
./docker-setup.sh restart

# View logs
./docker-setup.sh logs

# Complete cleanup (removes all data!)
./docker-setup.sh clean

# Rebuild containers
docker-compose up --build

# Shell into backend container
docker-compose exec backend bash

# Shell into database
docker-compose exec sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P SecurePassword123!
```

## 🐛 Troubleshooting

### SQL Server Connection Issues
```bash
# Check if SQL Server is ready
docker-compose logs sqlserver

# Test connection
docker-compose exec sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P SecurePassword123! -Q "SELECT 1"
```

### Backend Issues
```bash
# Check backend logs
docker-compose logs backend

# Restart just the backend
docker-compose restart backend

# Check if models are loading
docker-compose exec backend ls -la models/
```

### Frontend Issues
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up --build frontend
```

### Port Conflicts
If you have port conflicts, modify the ports in `docker-compose.yml`:
```yaml
services:
  backend:
    ports:
      - "8002:8001"  # Use 8002 instead of 8001
  frontend:
    ports:
      - "3000:5174"  # Use 3000 instead of 5174
```

## 🔐 Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Consider using Docker secrets for production deployments
- Enable SSL/TLS for production use

## 📦 Production Deployment

For production deployment:

1. Copy `.env.example` to `.env.production`
2. Set production values (disable debug, set secure passwords)
3. Use production compose file:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## 🆘 Support

If you encounter issues:

1. Check the logs: `./docker-setup.sh logs`
2. Verify all services are running: `docker-compose ps`
3. Test individual services: `curl http://localhost:8001/health`
4. Check resource usage: `docker stats`

## 🧹 Cleanup

To completely remove everything:
```bash
# Stop and remove containers, networks, and volumes
./docker-setup.sh clean

# Or manually:
docker-compose down -v --rmi all
docker system prune -a
```
