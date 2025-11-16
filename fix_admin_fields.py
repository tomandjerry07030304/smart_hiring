"""
Update admin user to have all required fields with correct names
"""
from pymongo import MongoClient
from datetime import datetime

# MongoDB Atlas connection
MONGODB_URI = "mongodb+srv://sridattayedida_db_user:2nAgVgWwIEaqE5To@cluster0.yhgzpuk.mongodb.net/smart_hiring_db?retryWrites=true&w=majority"

def fix_admin_fields():
    """Ensure admin user has all required fields with correct names"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client['smart_hiring_db']
        users_collection = db['users']
        
        # Get admin user
        admin = users_collection.find_one({'email': 'admin@smarthiring.com'})
        
        if admin:
            print(f"✓ Found admin user")
            print(f"  Current fields: {list(admin.keys())}")
            
            # Build update with all required fields
            updates = {}
            
            # Copy 'name' to 'full_name' if exists
            if 'name' in admin and 'full_name' not in admin:
                updates['full_name'] = admin['name']
                print(f"  → Adding full_name: {admin['name']}")
            elif 'full_name' not in admin:
                updates['full_name'] = 'System Administrator'
                print(f"  → Adding full_name: System Administrator")
            
            # Ensure other required fields exist
            if 'phone' not in admin:
                updates['phone'] = ''
                print("  → Adding phone: ''")
            
            if 'linkedin_url' not in admin:
                updates['linkedin_url'] = ''
                print("  → Adding linkedin_url: ''")
            
            if 'github_url' not in admin:
                updates['github_url'] = ''
                print("  → Adding github_url: ''")
            
            if 'profile_completed' not in admin:
                updates['profile_completed'] = True
                print("  → Adding profile_completed: True")
            
            if 'updated_at' not in admin:
                updates['updated_at'] = datetime.utcnow()
            
            # Apply updates
            if updates:
                result = users_collection.update_one(
                    {'email': 'admin@smarthiring.com'},
                    {'$set': updates}
                )
                print(f"\n✅ Admin user updated! Modified {result.modified_count} field(s)")
            else:
                print("\n✓ All fields already correct")
            
            # Show final state
            admin = users_collection.find_one({'email': 'admin@smarthiring.com'})
            print(f"\n✅ Final admin user fields:")
            for key in ['email', 'full_name', 'role', 'password_hash', 'phone', 'linkedin_url', 'github_url', 'is_active', 'profile_completed']:
                value = admin.get(key, 'MISSING')
                if key == 'password_hash':
                    value = '***HIDDEN***' if value != 'MISSING' else 'MISSING'
                print(f"   {key}: {value}")
        else:
            print("❌ Admin user not found!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("="*60)
    print("Fixing Admin User Fields")
    print("="*60)
    fix_admin_fields()
    print("="*60)
