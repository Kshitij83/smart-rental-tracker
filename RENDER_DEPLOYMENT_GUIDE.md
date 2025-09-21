# Smart Rental Tracker - Render Deployment Guide

This guide will help you deploy the Smart Rental Tracker application on Render.com.

## 🚀 Quick Deployment

### Prerequisites
- GitHub repository with your code
- Render.com account (free tier available)
- Basic understanding of web applications

### Step 1: Prepare Your Repository

1. **Ensure all files are committed to your repository:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify the following files exist in your repository:**
   - `render.yaml` (deployment configuration)
   - `backend/requirements.txt` (Python dependencies)
   - `frontend/package.json` (Node.js dependencies)
   - `backend/start_production.py` (production startup script)

### Step 2: Deploy Backend API

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the backend service:**
   - **Name:** `smart-rental-tracker-backend`
   - **Environment:** `Python 3`
   - **Build Command:** 
     ```bash
     cd backend && pip install -r requirements.txt && python -m app.populate_database
     ```
   - **Start Command:**
     ```bash
     cd backend && python start_production.py
     ```
   - **Instance Type:** `Free` (or upgrade as needed)

5. **Set Environment Variables:**
   - `PYTHON_VERSION`: `3.11.0`
   - `DATABASE_URL`: `sqlite:///./app/rental.db`
   - `ALLOWED_ORIGINS`: `https://smart-rental-tracker-frontend.onrender.com`

6. **Click "Create Web Service"**

### Step 3: Deploy Frontend

1. **In Render Dashboard, click "New +" → "Static Site"**
2. **Connect your GitHub repository**
3. **Configure the frontend service:**
   - **Name:** `smart-rental-tracker-frontend`
   - **Build Command:**
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Publish Directory:** `frontend/out`
   - **Node Version:** `18.18.0`

4. **Set Environment Variables:**
   - `NEXT_PUBLIC_API_URL`: `https://smart-rental-tracker-backend.onrender.com`

5. **Click "Create Static Site"**

### Step 4: Update CORS Settings

1. **Go to your backend service in Render Dashboard**
2. **Navigate to "Environment" tab**
3. **Update the `ALLOWED_ORIGINS` variable:**
   ```
   https://smart-rental-tracker-frontend.onrender.com
   ```
4. **Redeploy the backend service**

## 🔧 Alternative: Using render.yaml (Recommended)

If you prefer to use the `render.yaml` file for automated deployment:

1. **Ensure `render.yaml` is in your repository root**
2. **In Render Dashboard, click "New +" → "Blueprint"**
3. **Connect your GitHub repository**
4. **Render will automatically detect and use the `render.yaml` configuration**
5. **Click "Apply" to deploy both services**

## 📊 Monitoring and Management

### Health Checks
- **Backend Health:** `https://smart-rental-tracker-backend.onrender.com/health`
- **Frontend:** Your frontend URL should load the dashboard

### Logs
- Access logs through Render Dashboard → Your Service → "Logs" tab
- Monitor for any errors during startup or runtime

### Database
- The application uses SQLite for the free tier
- For production, consider upgrading to PostgreSQL

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility
   - Check build logs for specific errors

2. **CORS Errors:**
   - Ensure `ALLOWED_ORIGINS` includes your frontend URL
   - Check that the frontend URL is correct

3. **Database Issues:**
   - Verify database initialization in startup script
   - Check that SQLite file permissions are correct

4. **Frontend Not Loading:**
   - Verify `NEXT_PUBLIC_API_URL` is set correctly
   - Check that the backend is running and accessible

### Debug Steps

1. **Check Backend Logs:**
   ```bash
   # In Render Dashboard → Backend Service → Logs
   # Look for startup messages and errors
   ```

2. **Test Backend API:**
   ```bash
   curl https://smart-rental-tracker-backend.onrender.com/health
   ```

3. **Check Frontend Build:**
   - Look for build errors in the frontend deployment logs
   - Verify that static files are generated in the `out` directory

## 🔄 Updates and Maintenance

### Updating the Application
1. **Make changes to your code**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```
3. **Render will automatically redeploy both services**

### Scaling
- **Free Tier:** Limited to 750 hours/month
- **Paid Plans:** Available for higher usage and better performance
- **Database:** Consider PostgreSQL for production workloads

## 📈 Performance Optimization

### Backend Optimizations
- Use connection pooling for database connections
- Implement caching for frequently accessed data
- Optimize database queries

### Frontend Optimizations
- Enable gzip compression
- Optimize images and assets
- Use CDN for static assets

## 🔒 Security Considerations

### Environment Variables
- Never commit sensitive data to the repository
- Use Render's environment variable system
- Rotate API keys regularly

### CORS Configuration
- Only allow necessary origins
- Use HTTPS in production
- Validate all incoming requests

## 📞 Support

If you encounter issues:
1. Check the Render documentation
2. Review application logs
3. Verify environment variables
4. Test locally before deploying

## 🎉 Success!

Once deployed, your Smart Rental Tracker will be available at:
- **Frontend:** `https://smart-rental-tracker-frontend.onrender.com`
- **Backend API:** `https://smart-rental-tracker-backend.onrender.com`

The application includes:
- ✅ Equipment management dashboard
- ✅ Real-time analytics and monitoring
- ✅ Anomaly detection and alerts
- ✅ Demand forecasting
- ✅ Email notifications
- ✅ Mobile-responsive interface

Enjoy your deployed Smart Rental Tracker! 🚀
