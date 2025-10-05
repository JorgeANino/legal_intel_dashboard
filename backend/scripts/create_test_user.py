"""
Create a default test user for development and testing
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User


async def create_test_user():
    """Create a default test user if it doesn't exist"""
    
    async with AsyncSessionLocal() as session:
        # Check if user with ID 1 exists
        result = await session.execute(
            select(User).where(User.id == 1)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"✓ Test user already exists: {existing_user.email}")
            return
        
        # Create test user with dummy password (auth is optional in this project)
        test_user = User(
            email="test@example.com",
            hashed_password="dummy_hash_not_used",  # Auth is optional
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        
        print(f"✅ Created test user:")
        print(f"   ID: {test_user.id}")
        print(f"   Email: {test_user.email}")
        print(f"   Password: testpassword123")
        print(f"   Full Name: {test_user.full_name}")


async def main():
    """Main function"""
    print("🔧 Creating test user for development...")
    print()
    
    try:
        await create_test_user()
        print()
        print("✅ Test user setup complete!")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

