# 📦 Smart Rental Tracker - Complete Dependency List

## 🎯 Overview

This document lists all dependencies installed for the Smart Rental Tracker backend system, from initial setup through the notification system implementation.

## 📋 Main Dependencies (pip install required)

### 🚀 **Core FastAPI Framework**

```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

1. **FastAPI** (v0.104.1)

   - Purpose: Main web framework for REST API
   - Features: Automatic API documentation, data validation, async support
   - Used in: `main.py` - all API endpoints

2. **Uvicorn** (v0.24.0)

   - Purpose: ASGI server to run FastAPI application
   - Features: Hot reload during development, production-ready
   - Used for: Running the server (`uvicorn main:app --reload`)

3. **SQLAlchemy** (v2.0.23)

   - Purpose: Database ORM (Object Relational Mapping)
   - Features: SQL abstraction, relationship mapping, migrations
   - Used in: `models.py`, `database.py`, `crud.py`

4. **Pydantic** (v2.5.0)
   - Purpose: Data validation and serialization
   - Features: Type checking, automatic JSON schema generation
   - Used in: `schemas.py` - API request/response models

### 📧 **Notification System Dependencies**

```bash
pip install python-dotenv schedule requests
```

5. **python-dotenv** (v1.0.0)

   - Purpose: Load environment variables from .env file
   - Features: Configuration management, secrets handling
   - Used in: `notification_service.py` - email configuration

6. **schedule** (v1.2.0)

   - Purpose: Job scheduling for automated notifications
   - Features: Cron-like scheduling, easy syntax
   - Used in: `scheduler.py`, `notification_service.py`

7. **requests** (v2.31.0)
   - Purpose: HTTP library for testing API endpoints
   - Features: Simple HTTP requests, JSON handling
   - Used in: Testing scripts and API validation

## 🔧 **Built-in Python Libraries** (no installation needed)

### Standard Library Modules Used:

```python
# Email handling
import smtplib           # SMTP email sending
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Date and time
from datetime import datetime, timedelta
import time

# System and utilities
import os                # Environment variables, file paths
import sys               # System parameters
import logging           # Application logging
import argparse          # Command line parsing
import random            # Random data generation

# Type hints and data structures
from typing import List, Dict, Any, Optional
```

## 📁 **Installation Commands Used**

### Initial Backend Setup:

```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

### Notification System Addition:

```bash
pip install python-dotenv schedule requests
```

### Complete Installation (one command):

```bash
pip install -r requirements.txt
```

## 🎯 **Dependency Usage by File**

### `main.py` (FastAPI Application)

- **fastapi**: Core framework, endpoints, middleware
- **sqlalchemy**: Database session management
- **typing**: Type hints for parameters

### `models.py` (Database Models)

- **sqlalchemy**: Column definitions, relationships, base classes
- **datetime**: Timestamp fields

### `database.py` (Database Configuration)

- **sqlalchemy**: Engine creation, session management
- **os**: Environment variable access

### `schemas.py` (API Schemas)

- **pydantic**: BaseModel classes for validation
- **datetime**: Date/time field types
- **typing**: Optional and List types

### `crud.py` (Database Operations)

- **sqlalchemy**: Query operations, filtering, joins
- **datetime**: Date calculations and filtering
- **typing**: Return type annotations

### `notification_service.py` (Email System)

- **smtplib**: SMTP email sending
- **email**: Email formatting and attachments
- **schedule**: Job scheduling
- **python-dotenv**: Configuration loading
- **datetime**: Date calculations for notifications
- **logging**: Error tracking and audit logs

### `scheduler.py` (Automated Scheduling)

- **schedule**: Cron-like job scheduling
- **time**: Sleep and timing functions
- **logging**: Scheduler status logging
- **argparse**: Command line options

### `test_notifications.py` (Testing Framework)

- **random**: Generate test data
- **datetime**: Test date scenarios
- **sys/os**: Path manipulation for imports

## 🚀 **Production Considerations**

### Additional Dependencies for Production:

```bash
# Database migrations
pip install alembic

# Production WSGI server (alternative to uvicorn)
pip install gunicorn

# Environment-specific packages
pip install python-multipart  # For file uploads
pip install passlib[bcrypt]    # For password hashing
pip install python-jose[cryptography]  # For JWT tokens
```

### Docker Requirements:

```dockerfile
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

## 📊 **Dependency Statistics**

- **Total External Packages**: 7
- **Built-in Python Modules**: 15+
- **Total Installation Commands**: 2
- **Configuration Files**: 2 (.env, requirements.txt)

## 🔄 **Update Commands**

### Check for updates:

```bash
pip list --outdated
```

### Update all packages:

```bash
pip install --upgrade -r requirements.txt
```

### Freeze current versions:

```bash
pip freeze > requirements-lock.txt
```

## ✅ **Verification**

### Test installation:

```bash
python -c "import fastapi, sqlalchemy, pydantic, uvicorn, dotenv, schedule, requests; print('All dependencies imported successfully!')"
```

### Check versions:

```bash
pip show fastapi sqlalchemy pydantic uvicorn python-dotenv schedule requests
```

**All dependencies are now documented and ready for deployment! 🎉**
