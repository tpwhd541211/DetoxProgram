import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(encoding="utf-8", override=True)

path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
abs_path = os.path.abspath(path)
print("Path:", path)
print("Abs Path:", abs_path)
print("Exists:", os.path.exists(abs_path))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path

try:
    from google.cloud import language_v2
    client = language_v2.LanguageServiceClient()
    print("Client initialized successfully.")
    
    text = "테스트입니다."
    document = language_v2.Document(content=text, type_=language_v2.Document.Type.PLAIN_TEXT)
    features = {"extract_entities": True}
    response = client.annotate_text(request={"document": document, "features": features})
    print("API called successfully:", type(response))
except Exception as e:
    print("GCP failed:", str(e))
