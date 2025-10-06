"""
Create a default test user for development and testing
"""
# Standard library imports
import asyncio
import sys
from pathlib import Path

# Third-party imports
from sqlalchemy import select


# Add parent directory to path to import local modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Local application imports
from app.core.database import AsyncSessionLocal  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models.user import User  # noqa: E402


async def create_test_user():
    """Create a default test user if it doesn't exist"""

    async with AsyncSessionLocal() as session:
        # Check if user with ID 1 exists
        result = await session.execute(select(User).where(User.id == 1))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"✓ Test user already exists: {existing_user.email}")
            return

        # Create test user with hashed password
        test_password = "testpassword123"
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash(test_password),
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )

        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)

        print("Created test user:")
        print(f"   ID: {test_user.id}")
        print(f"   Email: {test_user.email}")
        print("   Password: testpassword123")
        print(f"   Full Name: {test_user.full_name}")
        print()
        print("Login credentials for frontend:")
        print("   Email: test@example.com")
        print("   Password: testpassword123")


async def main():
    """Main function"""
    print("Creating test user for development...")
    print()

    try:
        await create_test_user()
        print()
        print("Test user setup complete!")

    except Exception as e:
        print(f"ERROR: Error creating test user: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
