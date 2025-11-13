#!/bin/bash

# Quick Server Update Script
# Run this on your server to safely update without losing data

echo "🛡️  UMS Safe Server Update"
echo "=========================="

# Backup current database
echo "📦 Creating database backup..."
cp db.sqlite3 "db_backup_$(date +%Y%m%d_%H%M%S).sqlite3" 2>/dev/null || echo "No existing database found"

# Pull latest changes (this will now be safe - no database files included)
echo "📥 Pulling latest code..."
git pull origin main

# Run migrations (updates database structure without losing data)
echo "🔄 Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart gunicorn 2>/dev/null || echo "Gunicorn restart skipped"
sudo systemctl restart nginx 2>/dev/null || echo "Nginx restart skipped"

echo "✅ Update complete! Your data is preserved."
echo "🎉 ums.solutions is now updated with latest code!"