from core.database import engine
from sqlalchemy import text

tables_to_drop = [
    "topic_embedding",
    "session_text",
    "score_axis",
    "detox_plan",
    "yt_video_meta",
    "yt_channel_meta",
    "compare_snapshot"
]

with engine.begin() as conn:
    for table in tables_to_drop:
        try:
            conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
            print(f"Successfully dropped {table}")
        except Exception as e:
            print(f"Error dropping {table}: {e}")
