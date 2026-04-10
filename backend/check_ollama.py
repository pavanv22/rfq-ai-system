#!/usr/bin/env python3
"""Check Ollama status"""
import requests
import json

print("=" * 80)
print("CHECKING OLLAMA STATUS")
print("=" * 80)

try:
    resp = requests.get("http://localhost:11434/api/tags", timeout=5)
    print(f"\n✅ Ollama is running! (Status: {resp.status_code})")
    
    data = resp.json()
    models = data.get("models", [])
    
    if models:
        print(f"\n📦 Available models ({len(models)}):")
        for model in models:
            print(f"   - {model.get('name')}")
    else:
        print("\n❌ No models available!")
        print("\n   To download a model, run:")
        print("   ollama pull llama2")
        print("   or")
        print("   ollama pull neural-chat")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Ollama is NOT running!")
    print("\n   Start Ollama and ensure it's listening on localhost:11434")
    print("\n   Then run: ollama serve")
    print("   And in another terminal: ollama pull llama2")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 80)
