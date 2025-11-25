import google.generativeai as genai

# Cole sua API Key aqui dentro das aspas para testar
MINHA_KEY = "AIzaSyAFq9OBxSCelSLlv2YsZjbbs1qsgnQpfWA"

def listar_modelos():
    if MINHA_KEY.startswith("COLE_"):
        print("⚠️ Edite o arquivo e coloque sua chave na variável MINHA_KEY")
        return

    genai.configure(api_key=MINHA_KEY)
    
    print(f"🔍 Conectando com a chave: {MINHA_KEY[:5]}... (oculto)")
    print("📋 Modelos disponíveis para sua conta:")
    print("-" * 30)
    
    try:
        encontrou_algum = False
        # Lista todos os modelos disponíveis
        for m in genai.list_models():
            # Filtra só os que geram texto (chat)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                encontrou_algum = True
        
        if not encontrou_algum:
            print("❌ Nenhum modelo de texto encontrado. Sua chave pode estar limitada.")
            
    except Exception as e:
        print(f"❌ ERRO GRAVE: {e}")

if __name__ == "__main__":
    listar_modelos()