# UMS Safe Deployment Guide

## 🚨 CRITICAL: Database Protection

Your server database was being overwritten because `db.sqlite3` was tracked in git. This has been FIXED with the following changes:

### ✅ What Was Fixed:

1. **Added .gitignore file** - Prevents database files from being committed
2. **Removed db.sqlite3 from git tracking** - Server database is now safe
3. **Created deployment scripts** - Safe update procedures

### 📋 Safe Development Workflow:

#### For Local Development:
```bash
# 1. Make your code changes
# 2. Test locally
# 3. Run safety check before committing
./dev_safety_check.sh

# 4. Add only code files (never database files)
git add core/views.py core/models.py core/templates/
git add core/forms.py  # etc.

# 5. Commit your changes
git commit -m "Your changes description"

# 6. Push to repository
git push origin main
```

#### For Server Updates:
```bash
# On the server, run:
./server_update.sh
```

### 🛡️ Protection Measures Now in Place:

1. **`.gitignore`** - Blocks these files from being committed:
   - `*.sqlite3` - All database files
   - `db.sqlite3` - Main database  
   - `__pycache__/` - Python cache
   - `media/` - User uploads
   - Development scripts and backups

2. **Database Backups** - Server script automatically creates backups before updates

3. **Migration Safety** - Schema changes are applied without losing data

### ⚠️ NEVER Commit These Files:
- `db.sqlite3` (main database)
- Any `*.sqlite3` files
- `media/` folder (user uploads)
- `__pycache__/` folders
- Backup files (`*.backup`, `*.json` backups)

### 🔧 If Database Issues Occur:

1. **Check server logs**: 
   ```bash
   sudo journalctl -u gunicorn -f
   ```

2. **Restore from backup**:
   ```bash
   cp db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

### 📝 Best Practices:

1. **Always test locally first**
2. **Use the safety check script before commits**
3. **Only commit code changes, never data**
4. **Use the server update script for deployments**
5. **Keep regular database backups**

## 🎯 Your Data Is Now Safe!

The server database at `ums.solutions` will no longer be overwritten during deployments. Your projects, inventory, customers, and all other data will persist through updates.

### Quick Commands:

```bash
# Before committing (run locally):
./dev_safety_check.sh

# To update server safely:
ssh your-server
cd /home/ubuntu/UMS
./server_update.sh
```

The database protection is now ACTIVE and will prevent future data loss!