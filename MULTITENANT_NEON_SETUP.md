# 🏢 **Multitenant Neon Database Setup Guide**

## 📋 **Overview**

This guide sets up a **schema-based multitenant architecture** for Quizlet AI using Neon PostgreSQL. Each tenant gets their own isolated schema with complete data separation.

## 🏗️ **Architecture**

```
Neon PostgreSQL Database
├── public schema (shared)
├── shared schema (common data)
└── tenant_* schemas (isolated per tenant)
    ├── tenant_abc123 (Acme Corp)
    ├── tenant_def456 (Tech Startup)
    └── tenant_ghi789 (University)
```

## 🚀 **Step-by-Step Setup**

### **1. Create Neon Database**

1. **Sign up** at [neon.tech](https://neon.tech)
2. **Create project**: "quizlet-multitenant"
3. **Copy connection string** from dashboard

### **2. Install Dependencies**

```bash
# PostgreSQL adapter
pip install psycopg2-binary

# Additional dependencies for multitenancy
pip install contextvars
```

### **3. Configure Environment**

Create `.env` file:
```env
# Neon Database
NEON_DATABASE_URL=postgresql://username:password@host/database?sslmode=require

# Example:
# NEON_DATABASE_URL=postgresql://john:password123@ep-cool-name-123456.us-east-2.aws.neon.tech/quizlet_db?sslmode=require
```

### **4. Initialize Multitenant Database**

```bash
# Run the multitenant initialization script
python init_multitenant_db.py
```

This will:
- ✅ Test Neon connection
- ✅ Create shared schemas
- ✅ Create sample tenants
- ✅ Set up admin users
- ✅ Test tenant isolation

### **5. Update Application Configuration**

Replace `app/core/database.py` with multitenant config:

```python
# In your main.py or app initialization
from app.core.multitenant_config import multitenant_db, get_db
from app.api.routes import tenants

# Add tenant routes
app.include_router(tenants.router, prefix="/api")
```

## 🏢 **Tenant Management**

### **Creating Tenants**

```bash
# Create a new tenant
curl -X POST "http://localhost:8000/api/tenants/" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "My Company",
    "owner_email": "admin@mycompany.com"
  }'
```

**Response:**
```json
{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_name": "My Company",
  "schema_created": true,
  "admin_user_created": true,
  "admin_email": "admin@mycompany.com",
  "temp_password": "admin123"
}
```

### **Using Tenants**

```bash
# All API requests must include X-Tenant-ID header
curl -X GET "http://localhost:8000/api/users" \
  -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Tenant Operations**

```bash
# List all tenants
curl -X GET "http://localhost:8000/api/tenants/"

# Get tenant statistics
curl -X GET "http://localhost:8000/api/tenants/{tenant_id}/stats"

# Delete tenant
curl -X DELETE "http://localhost:8000/api/tenants/{tenant_id}"

# Create user in tenant
curl -X POST "http://localhost:8000/api/tenants/{tenant_id}/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "username": "newuser",
    "password": "password123"
  }'
```

## 🔒 **Security & Isolation**

### **Data Isolation**
- ✅ **Schema-based separation**: Each tenant has isolated schema
- ✅ **Row-level security**: Users can only access their tenant's data
- ✅ **Connection pooling**: Optimized for multitenant workloads
- ✅ **Audit trails**: Track tenant operations

### **Authentication**
```python
# Tenant-aware authentication
def get_current_user(tenant_id: str = Depends(get_tenant_from_header)):
    # User can only access their tenant's data
    pass
```

### **API Security**
```python
# All endpoints require tenant context
@app.middleware("http")
async def add_tenant_context(request: Request, call_next):
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        set_tenant_context(tenant_id)
    response = await call_next(request)
    return response
```

## 📊 **Monitoring & Analytics**

### **Tenant Statistics**
```python
# Get tenant usage statistics
stats = TenantManager.get_tenant_stats(tenant_id)
# Returns: users_count, quizzes_count, questions_count, etc.
```

### **Database Monitoring**
```sql
-- Monitor tenant schemas
SELECT 
    schema_name,
    COUNT(*) as table_count
FROM information_schema.tables 
WHERE schema_name LIKE 'tenant_%'
GROUP BY schema_name;

-- Monitor tenant data usage
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname LIKE 'tenant_%';
```

## 🚀 **Deployment**

### **Environment Variables**
```env
# Production
NEON_DATABASE_URL=postgresql://prod_user:prod_pass@prod-host/db?sslmode=require
ENVIRONMENT=production
TENANT_ISOLATION_LEVEL=schema
```

### **Docker Configuration**
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Run multitenant app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Kubernetes Deployment**
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quizlet-multitenant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: quizlet-multitenant
  template:
    metadata:
      labels:
        app: quizlet-multitenant
    spec:
      containers:
      - name: app
        image: quizlet-multitenant:latest
        env:
        - name: NEON_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: neon-secret
              key: database-url
```

## 🔧 **Testing**

### **Tenant Isolation Test**
```python
# test_tenant_isolation.py
import requests

def test_tenant_isolation():
    # Create two tenants
    tenant1 = create_tenant("Company A")
    tenant2 = create_tenant("Company B")
    
    # Create users in each tenant
    user1 = create_user(tenant1["id"], "user1@companya.com")
    user2 = create_user(tenant2["id"], "user2@companyb.com")
    
    # Verify isolation - user1 cannot see user2's data
    response = requests.get(
        f"/api/users/{user2['id']}", 
        headers={"X-Tenant-ID": tenant1["id"]}
    )
    assert response.status_code == 404  # Should not find user2
```

### **Performance Testing**
```python
# Load testing with multiple tenants
import asyncio
import aiohttp

async def load_test_multitenant():
    tenants = [generate_tenant_id() for _ in range(10)]
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for tenant_id in tenants:
            task = session.get(
                "/api/quizzes",
                headers={"X-Tenant-ID": tenant_id}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return responses
```

## 📈 **Scaling Considerations**

### **Database Scaling**
- **Connection Pooling**: Configure pool size per tenant
- **Read Replicas**: Use Neon's read replicas for analytics
- **Sharding**: Consider sharding for very large tenants

### **Application Scaling**
- **Horizontal Scaling**: Stateless app instances
- **Caching**: Redis per tenant or shared with tenant isolation
- **CDN**: Static assets with tenant-specific paths

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **Connection Errors**
```bash
# Check Neon connection
python test_neon_connection.py

# Verify SSL settings
NEON_DATABASE_URL=postgresql://...?sslmode=require
```

2. **Schema Creation Errors**
```sql
-- Check schema permissions
SELECT schema_name, schema_owner 
FROM information_schema.schemata;

-- Grant permissions if needed
GRANT CREATE ON DATABASE your_db TO your_user;
```

3. **Tenant Isolation Issues**
```python
# Verify tenant context
print(f"Current tenant: {tenant_context.get()}")

# Check schema search path
session.execute(text("SHOW search_path"))
```

### **Performance Optimization**
```sql
-- Create indexes for tenant queries
CREATE INDEX CONCURRENTLY idx_users_tenant_id ON users(tenant_id);
CREATE INDEX CONCURRENTLY idx_quizzes_tenant_id ON quizzes(tenant_id);

-- Analyze tenant schemas
ANALYZE tenant_abc123.users;
ANALYZE tenant_abc123.quizzes;
```

## 🎯 **Best Practices**

### **Tenant Management**
- ✅ **UUID-based IDs**: Use UUIDs for tenant identification
- ✅ **Schema naming**: Consistent schema naming convention
- ✅ **Admin users**: Create admin user for each tenant
- ✅ **Backup strategy**: Backup per tenant or entire database

### **Security**
- ✅ **Header validation**: Validate X-Tenant-ID header
- ✅ **SQL injection**: Use parameterized queries
- ✅ **Access control**: Implement tenant-aware authorization
- ✅ **Audit logging**: Log all tenant operations

### **Performance**
- ✅ **Connection pooling**: Optimize pool settings
- ✅ **Indexing**: Index tenant-specific columns
- ✅ **Caching**: Cache tenant-specific data
- ✅ **Monitoring**: Monitor per-tenant performance

## 📞 **Support**

- **Neon Documentation**: [docs.neon.tech](https://docs.neon.tech)
- **PostgreSQL Multitenancy**: [postgresql.org](https://www.postgresql.org/docs/current/ddl-schemas.html)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

**🎉 Congratulations!** Your Quizlet AI app now supports multitenant architecture with complete data isolation using Neon PostgreSQL. 