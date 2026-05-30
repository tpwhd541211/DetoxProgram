import shutil
import os

src = r"C:\Users\Administrator\Desktop\UnbelievableTeamProject\others\tidal-sum-478102-i8-bfff5241f766.json"
dst = r"C:\Users\Administrator\Desktop\UnbelievableTeamProject\DetoxProgram\backend\gcp_creds.json"

if os.path.exists(src):
    shutil.copy(src, dst)
    print("Copied successfully.")
else:
    print("Source not found:", src)
