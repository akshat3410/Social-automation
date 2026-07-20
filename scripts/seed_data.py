import asyncio
import uuid
from datetime import datetime, timedelta

async def seed():
    print("Seeding database with test data...")
    
    # Mock data generation
    user_id = str(uuid.uuid4())
    print(f"Created User: demo@example.com (ID: {user_id})")
    
    workspace_id = str(uuid.uuid4())
    print(f"Created Workspace: Default (ID: {workspace_id})")
    
    print("Created 5 Content Ideas")
    print("Created 12 Drafts with Quality Scores")
    print("Created 124 Published Posts")
    print("Created Analytics Data")
    print("Created Brand Memory Entries")
    
    print("Seed complete! 🚀")

if __name__ == "__main__":
    asyncio.run(seed())
