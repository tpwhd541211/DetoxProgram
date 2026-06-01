import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

from core.config import settings

path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
print("Resolved GOOGLE_APPLICATION_CREDENTIALS path:", path)
print("Exists:", os.path.exists(path) if path else False)
print("GCP_API_KEY set:", bool(settings.GCP_API_KEY))

try:
    from google.cloud import language_v2
    if settings.GCP_API_KEY:
        client = language_v2.LanguageServiceClient(client_options={"api_key": settings.GCP_API_KEY})
        print("Client initialized successfully using API Key.")
    else:
        client = language_v2.LanguageServiceClient()
        print("Client initialized successfully using Service Account JSON.")
    
    text = "테스트입니다."
    document = language_v2.Document(content=text, type_=language_v2.Document.Type.PLAIN_TEXT)
    features = {"extract_entities": True}
    response = client.annotate_text(request={"document": document, "features": features})
    print("API called successfully:", type(response))
except Exception as e:
    print("GCP failed:", str(e))

