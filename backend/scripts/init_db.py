"""
Database migration runner script
This script runs Alembic migrations to create/update database tables

DEPRECATED: Use `alembic upgrade head` directly instead
This script is kept for backwards compatibility
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Run database migrations using Alembic"""
    print("🔨 Running database migrations...")
    
    try:
        # Change to backend directory where alembic.ini is located
        backend_dir = Path(__file__).parent.parent
        
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        print("✅ Database migrations completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running migrations: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()

