import requests
import json
import time

# --- SUA LISTA DE CARTAS ---
meu_deck_nomes_ingles = [
    "Snake-Eye Ash",
    "Snake-Eye Poplar",
    "Bonfire",
    "Promethean Princess, Bestower of Flames",
    "S:P Little Knight",
    "Nibiru, the Primal Being",
    "Infinite Impermanence",
    "Maxx \"C\"",
    "Ash Blossom & Joyous Spring",
    "Wanted: Seeker of Sinful Spoils",
    "Diabellstar the Black Witch",
    "Divine Temple of the Snake-Eye",
    "Original Sinful Spoils - Snake-Eye",
    "Flamberge Dragon"
    # Adicione o resto aqui...
]

def buscar_carta_robusta(nome_ingles):
    url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    
    # 1. TENTATIVA EM PORTUGUÊS
    try:
        r = requests.get(url, params={"name": nome_ingles, "language": "pt"})
        data = r.json()
        if "data" in data:
            return data["data"][0], "PT-BR"
    except:
        pass

    # 2. TENTATIVA EM INGLÊS (FALLBACK - PLANO B)
    # Se falhou em PT (porque a carta é muito nova), baixa em Inglês
    try:
        r = requests.get(url, params={"name": nome_ingles}) # Sem filtro de lingua
        data = r.json()
        if "data" in data:
            return data["data"][0], "EN (Fallback)"
    except:
        pass
    
    return None, None

def criar_banco_master_duel():
    print(f"🔍 Buscando {len(meu_deck_nomes_ingles)} cartas (Modo Híbrido PT/EN)...")
    print("-" * 50)
    
    banco_final = []
    
    for nome in meu_deck_nomes_ingles:
        carta_dados, idioma_encontrado = buscar_carta_robusta(nome)
        
        if carta_dados:
            print(f"✅ [{idioma_encontrado}] Sucesso: {nome}")
            banco_final.append({
                "nome_pt": carta_dados["name"], # Guarda o nome encontrado
                "nome_ingles": nome,           # Guarda o nome original da sua lista
                "tipo": carta_dados["type"],
                "efeito": carta_dados["desc"], # Texto do efeito
                "atk": carta_dados.get("atk", "N/A"),
                "def": carta_dados.get("def", "N/A"),
                "nivel": carta_dados.get("level", "N/A")
            })
        else:
            print(f"❌ ERRO CRÍTICO: Carta não existe nem em Inglês: {nome}")
        
        time.sleep(0.05) # Pausa rápida para a API não bloquear

    # Salva o arquivo final
    with open("master_duel_deck.json", "w", encoding="utf-8") as f:
        json.dump(banco_final, f, indent=4, ensure_ascii=False)
    
    print("-" * 50)
    print(f"\n📄 Sucesso! Banco criado com {len(banco_final)} cartas.")
    print("Agora pode rodar: streamlit run app.py")

if __name__ == "__main__":
    criar_banco_master_duel()