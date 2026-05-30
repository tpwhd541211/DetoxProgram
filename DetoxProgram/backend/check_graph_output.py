import sys
import os
from unittest.mock import MagicMock

# Mock celery module to avoid ModuleNotFoundError
sys.modules['celery'] = MagicMock()

# Ensure the backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from api.v1.dashboard import get_graph_data

async def check_output():
    # We will simulate calling the get_graph_data endpoint directly.
    # We need a user ID that has datasets. Let's find one.
    db = SessionLocal()
    from models.schemas import ScoreRun
    latest_run = db.query(ScoreRun).order_by(ScoreRun.created_at.desc()).first()
    if not latest_run:
        print("No ScoreRun found in DB, cannot test output.")
        db.close()
        return
        
    user_id = latest_run.user_id
    print(f"Testing graph output for User ID: {user_id} on Dataset: {latest_run.dataset_id}")
    db.close()
    
    try:
        # call the router function directly by passing the user_id
        # get_graph_data is async
        result = await get_graph_data(current_user=user_id)
        
        nodes = result.get("nodes", [])
        edges = result.get("edges", [])
        
        print(f"\n=== Resulting Graph Data ===")
        print(f"Total Nodes: {len(nodes)}")
        print(f"Total Edges: {len(edges)}")
        
        print("\nNodes list:")
        for node in nodes:
            print(f"  ID: {node['id']} | Label: {node['label']} | Group: {node['group']} | Size: {node['size']}")
            
        print("\nGarbage check in nodes:")
        garbage_found = False
        for node in nodes:
            label = node['label']
            if "=" in label or len(label) > 20 or any(c in label for c in ["-", "|", ":", "/", "\\"]):
                print(f"  🚨 Found Garbage Node: {label}")
                garbage_found = True
        if not garbage_found:
            print("  ✅ No garbage nodes found in the generated output!")
            
    except Exception as e:
        print("Error getting graph data:", e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_output())
