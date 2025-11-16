"""
Fix admin user in MongoDB Atlas - ensure password_hash field exists
"""
import os
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime

# MongoDB Atlas connection
MONGODB_URI = "mongodb+srv://sridattayedida_db_user:2nAgVgWwIEaqE5To@cluster0.yhgzpuk.mongodb.net/smart_hiring_db?retryWrites=true&w=majority"

bcrypt = Bcrypt()

def fix_admin_user():
    """Ensure admin user has proper password_hash field"""
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(MONGODB_URI)
        db = client['smart_hiring_db']
        users_collection = db['users']
        
        # Check current admin user
        admin = users_collection.find_one({'email': 'admin@smarthiring.com'})
        
        if admin:
            print(f"✓ Found admin user: {admin['email']}")
            print(f"  Current fields: {list(admin.keys())}")
            
            # Check if password_hash exists
            if 'password_hash' not in admin:
                print("  ⚠ Missing password_hash field!")
                
                # Hash the password properly
                password_hash = bcrypt.generate_password_hash('changeme').decode('utf-8')
                
                # Update the user with password_hash
                result = users_collection.update_one(
                    {'email': 'admin@smarthiring.com'},
                    {
                        '$set': {
                            'password_hash': password_hash,
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                if result.modified_count > 0:
                    print("  ✅ Admin user updated with password_hash!")
                    print(f"  Password: changeme")
                else:
                    print("  ❌ Failed to update admin user")
            else:
                print("  ✓ password_hash field exists")
                # Verify it's a valid bcrypt hash
                if admin['password_hash'].startswith('$2b$'):
                    print("  ✓ Valid bcrypt hash format")
                else:
                    print("  ⚠ Invalid hash format, fixing...")
                    password_hash = bcrypt.generate_password_hash('changeme').decode('utf-8')
                    users_collection.update_one(
                        {'email': 'admin@smarthiring.com'},
                        {'$set': {'password_hash': password_hash}}
                    )
                    print("  ✅ Password hash fixed!")
        else:
            print("❌ Admin user not found! Creating new admin user...")
            
            # Create new admin user
            password_hash = bcrypt.generate_password_hash('changeme').decode('utf-8')
            
            admin_user = {
                'email': 'admin@smarthiring.com',
                'password_hash': password_hash,
                'role': 'admin',
                'full_name': 'System Administrator',
                'phone': '',
                'linkedin_url': '',
                'github_url': '',
                'is_active': True,
                'profile_completed': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = users_collection.insert_one(admin_user)
            print(f"✅ Admin user created: {result.inserted_id}")
            print(f"   Email: admin@smarthiring.com")
            print(f"   Password: changeme")
        
        # Verify login would work
        admin = users_collection.find_one({'email': 'admin@smarthiring.com'})
        if admin and 'password_hash' in admin:
            if bcrypt.check_password_hash(admin['password_hash'], 'changeme'):
                print("\n✅ VERIFIED: Login will work with admin@smarthiring.com / changeme")
            else:
                print("\n❌ ERROR: Password verification failed!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("="*60)
    print("Fixing Admin User in MongoDB Atlas")
    print("="*60)
    fix_admin_user()
    print("="*60)
