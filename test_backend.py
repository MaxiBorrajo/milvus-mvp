import requests
import json

def test_backend():
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Health check
        print("🔍 Probando conexión al backend...")
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        
        # Test 2: Root endpoint
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
        
        # Test 3: Debug collections
        response = requests.get(f"{base_url}/debug/collections")
        print(f"✅ Debug collections: {response.status_code} - {response.json()}")
        
        # Test 4: Find person endpoint
        params = {"question": "test", "top_k": 1}
        response = requests.get(f"{base_url}/find-person", params=params)
        print(f"✅ Find person: {response.status_code} - {response.json()}")
        
        print("\n🎉 Backend funcionando correctamente!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al backend en http://localhost:8000")
        print("💡 Asegúrate de que el backend esté ejecutándose con: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_backend() 