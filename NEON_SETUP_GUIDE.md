# 🚀 Neon Database Setup Guide for Quizlet AI

## 📋 Prerequisites

1. **Neon Account**: Sign up at [neon.tech](https://neon.tech)
2. **Python Dependencies**: Install PostgreSQL adapter
3. **Environment Variables**: Configure your database URL

## 🔧 Step-by-Step Setup

### 1. Install PostgreSQL Dependencies

```bash
pip install psycopg2-binary
# or for async support
pip install asyncpg
```

### 2. Create Neon Database

1. **Sign up/Login** to [neon.tech](https://neon.tech)
2. **Create a new project**:
   - Click "Create Project"
   - Choose a project name (e.g., "quizlet-ai")
   - Select a region close to you
   - Click "Create Project"

3. **Get your connection string**:
   - Go to your project dashboard
   - Click "Connection Details"
   - Copy the connection string

### 3. Configure Environment Variables

Create or update your `.env` file:

```env
# Neon Database Configuration
NEON_DATABASE_URL=postgresql://username:password@host/database

# Example format:
# NEON_DATABASE_URL=postgresql://john:password123@ep-cool-name-123456.us-east-2.aws.neon.tech/quizlet_db?sslmode=require
```

### 4. Update Database Configuration

Replace the SQLite configuration in `app/core/database.py` with Neon configuration:

```python
# Option 1: Use the new neon_config.py
from app.core.neon_config import engine, Base, get_db

# Option 2: Update existing database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")
engine = create_engine(NEON_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### 5. Initialize Database Tables

```bash
python init_db.py
```

### 6. Test Connection

Create a test script `test_neon_connection.py`:

```python
from app.core.neon_config import engine

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT version();")
            print("✅ Neon database connected successfully!")
            print(f"PostgreSQL version: {result.fetchone()[0]}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
```

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit database credentials to version control
- Use `.env` files for local development
- Use environment variables in production

### 2. SSL Configuration
- Always use SSL for production connections
- Add `?sslmode=require` to your connection string

### 3. Connection Pooling
- Configure appropriate pool sizes
- Monitor connection usage

## 🚀 Deployment Configuration

### For Render/Vercel/Heroku:

1. **Set Environment Variables**:
   ```bash
   NEON_DATABASE_URL=your-neon-connection-string
   ```

2. **Update requirements.txt**:
   ```
   psycopg2-binary==2.9.9
   ```

3. **Database Migration**:
   ```bash
   python init_db.py
   ```

## 🔍 Troubleshooting

### Common Issues:

1. **Connection Refused**:
   - Check if your IP is whitelisted
   - Verify connection string format
   - Ensure SSL is properly configured

2. **Authentication Failed**:
   - Verify username/password
   - Check if credentials are URL-encoded
   - Ensure database exists

3. **SSL Issues**:
   - Add `?sslmode=require` to connection string
   - Check firewall settings

### Connection String Format:

```
postgresql://username:password@host:port/database?sslmode=require
```

## 📊 Monitoring

### Neon Dashboard Features:
- **Query Performance**: Monitor slow queries
- **Connection Usage**: Track active connections
- **Storage Usage**: Monitor database size
- **Logs**: View database logs

### Health Check Endpoint:

Add to your FastAPI app:

```python
@app.get("/health")
async def health_check():
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

## 🎯 Next Steps

1. **Test the connection** with the provided script
2. **Migrate existing data** if any
3. **Update your application** to use Neon
4. **Monitor performance** and optimize queries
5. **Set up backups** and monitoring

## 📞 Support

- **Neon Documentation**: [docs.neon.tech](https://docs.neon.tech)
- **Neon Community**: [community.neon.tech](https://community.neon.tech)
- **SQLAlchemy Documentation**: [docs.sqlalchemy.org](https://docs.sqlalchemy.org)

---

**🎉 Congratulations!** Your Quizlet AI app is now ready to use Neon database for production-grade performance and scalability. 