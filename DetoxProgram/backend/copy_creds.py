import shutil
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(backend_dir)
root_dir = os.path.dirname(project_dir)

# Find any JSON file starting with "tidal-sum" in the others directory
others_dir = os.path.join(root_dir, "others")
src = None
if os.path.exists(others_dir):
    for f in os.listdir(others_dir):
        if f.startswith("tidal-sum") and f.endswith(".json"):
            src = os.path.join(others_dir, f)
            break

dst = os.path.join(backend_dir, "gcp_creds.json")

if src and os.path.exists(src):
    shutil.copy(src, dst)
    print(f"Copied successfully from {src} to {dst}")
else:
    # Hardcoded absolute path fallback
    fallback_src = r"C:\Users\Administrator\Desktop\UnbelievableTeamProject\others\tidal-sum-478102-i8-bfff5241f766.json"
    if os.path.exists(fallback_src):
        shutil.copy(fallback_src, dst)
        print("Copied successfully from fallback.")
    else:
        print("Source credentials file not found in 'others/' directory.")
