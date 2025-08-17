import google.generativeai as genai
import json

API_KEY = "AIzaSyCPsyWhUw7t9WCUSRg5zzqQyje8Tizou2E"
genai.configure(api_key=API_KEY)

try:
    response = genai.list_models()
    model_names = [model.name for model in response]
    print("Modelos disponibles:")
    print(json.dumps(model_names, indent=2))

except Exception as e:
    print(f"Error al listar modelos: {e}")