# MongoDB Atlas Setup for Railway Deployment

## Quick Setup Steps

### 1. Create MongoDB Atlas Account
- Go to: https://www.mongodb.com/cloud/atlas/register
- Sign up with your email: **sridattayedida@gmail.com**
- Verify your email

### 2. Create a Free Cluster
1. Click "Build a Database"
2. Choose **FREE** tier (M0 Sandbox)
3. Select **AWS** as provider
4. Choose region closest to you (e.g., `us-east-1`)
5. Cluster Name: `smart-hiring-cluster`
6. Click "Create Cluster"

### 3. Create Database User
1. Go to "Database Access" in left sidebar
2. Click "Add New Database User"
3. Username: `admin`
4. Password: Generate a secure password (save it!)
5. Database User Privileges: **Read and write to any database**
6. Click "Add User"

### 4. Configure Network Access
1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (0.0.0.0/0)
   - ⚠️ For production, restrict to Railway IPs
4. Click "Confirm"

### 5. Get Connection String
1. Go to "Database" in left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Driver: **Python**, Version: **3.12 or later**
5. Copy the connection string, it looks like:
   ```
   mongodb+srv://admin:<password>@smart-hiring-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual database user password
7. Add database name at the end:
   ```
   mongodb+srv://admin:YOUR_PASSWORD@smart-hiring-cluster.xxxxx.mongodb.net/smart-hiring1?retryWrites=true&w=majority
   ```

### 6. Set MongoDB URI in Railway

**Option A: Using Railway CLI (Recommended)**
```powershell
cd "C:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system"
railway variables --set MONGODB_URI="mongodb+srv://admin:YOUR_PASSWORD@smart-hiring-cluster.xxxxx.mongodb.net/smart-hiring1?retryWrites=true&w=majority"
```

**Option B: Using Railway Dashboard**
1. Go to: https://railway.com/project/75c7b478-0155-4ba7-ba08-e320c52b61f5
2. Click on your service `my-project-s1`
3. Go to "Variables" tab
4. Find `MONGODB_URI` and update with your connection string
5. Save changes

### 7. Important Notes

✅ **Database Name**: Use `smart-hiring1` (already configured)
✅ **Connection String Format**: Must use `mongodb+srv://` for Atlas
✅ **Security**: Never commit the password to Git
✅ **Testing**: After deployment, check Railway logs for MongoDB connection success

### 8. Current Configuration Status

Your Railway environment variables are SET:
- ✅ DB_NAME=smart-hiring1
- ⚠️ MONGODB_URI=mongodb://localhost:27017/smart_hiking_db (needs update to Atlas URI)
- ✅ All other variables configured

### 9. After MongoDB Setup

Once you've set the correct MongoDB URI, redeploy:
```powershell
cd "C:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system"
railway up --detach
```

### 10. Troubleshooting

**Connection Timeout**:
- Ensure 0.0.0.0/0 is added to Network Access
- Wait 2-3 minutes after adding IP whitelist

**Authentication Failed**:
- Double-check username and password
- Ensure password doesn't contain special characters that need URL encoding

**Database Not Found**:
- Database will be created automatically on first connection
- Ensure database name is in connection string

---

## Your Project URL
Once deployed successfully, your app will be at:
`https://my-project-s1-production.up.railway.app`

Check deployment status:
```powershell
railway status
```

View logs:
```powershell
railway logs
```
