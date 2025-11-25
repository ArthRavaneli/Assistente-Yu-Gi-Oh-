import google.generativeai as genai
import requests
import json
import time
import os

# --- FUNÇÃO PARA LER A CHAVE ---
def pegar_chave():
    try:
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ Erro: Crie o arquivo 'api_key.txt' com sua chave dentro!")
        return None

API_KEY = pegar_chave()

# --- SUA LISTA EM PORTUGUÊS ---
minha_lista_pt = [
    "Ressonador de Sinkron",
    "Ressonador da Corrente",
    '"C" Maxx',
    "Ressonador Vermelho",
    "Ressonador Carmesim",
    "Ressonador da Visão",
    "Ressonador das Chamas",
    "Rei Lótus, Crime das Chamas",
    "Florescer de Cinzas & Primavera",
    "Ressonador da Alma",
    "Gardna Vermelho",
    "Rei Vagante Vento Selvagem",
    "Arquidemônio de Ossos",
    "Raigeki",
    "Reviver Monstro",
    "Chamado do Ressonador",
    "Tempestade de Relâmpagos",
    "Gaia Carmesim",
    "Comandar Ressonador",
    "Força de Poder Absoluta",
    "Tapete Vermelho",
    "Reino Vermelho",
    "Golem Demoníaco",
    "Corrente Demoníaca",
    "Apollousa, o Arco da Deusa",
    "Zona Vermelha",
    "Dragão da Ascendência Vermelha",
    "Kuibelt, o Dragão Lâmina",
    "Dragão Vermelho Arquidemônio",
    "Dragão Vermelho Arquidemônio com Cicatriz",
    "Dragão Vermelho Arquidemônio do Abismo",
    "Dragão Vermelho Arquidemônio do Banimento",
    "Dração Vermelho Nova",
    "Dragão Vermelho Super Nova",
]

# --- CORREÇÕES MANUAIS (O TIRA-TEIMA) ---
# Se a IA errar ou a API não achar, coloque a correção aqui.
# Formato: "Nome em Português da lista": "Nome Oficial em Inglês Correto"
CORRECOES_MANUAIS = {
    "Ressonador das Chamas": "Flare Resonator",
    "Florescer de Cinzas & Primavera Feliz": "Ash Blossom & Joyous Spring",
    "Kuibelt, o Dragão Lâmina": "Kuibelt the Blade Dragon",
    "Dragão Vermelho Arquidemônio do Abismo": "Hot Red Dragon Archfiend Abyss",
    "Dragão Vermelho Arquidemônio do Banimento": "Hot Red Dragon Archfiend Bane",
    "Dragão Vermelho Super Nova": "Red Supernova Dragon",
    "Ressonador de Sinkron": "Synkron Resonator",
    "Rei Lótus, Crime das Chamas": "Red Lotus King, Flame Crime",
    "Golem Demoníaco": "Fiendish Golem",
    "Reino Vermelho": "Red Reign",
    "Dragão Vermelho Arquidemônio com Cicatriz": "Scarlight Red Dragon Archfiend",
    "Rei Vagante Vento Selvagem": "Wandering King Wildwind",
    "Dragão Vermelho Arquidemônio com Cicatriz": "Scarred Dragon Archfiend",
    "Dragão Vermelho Arquidemônio do Abismo": "Hot Red Dragon Archfiend Abyss",
    "Dragão Vermelho Arquidemônio do Banimento": "Hot Red Dragon Archfiend Bane",
    "Força de Poder Absoluta": "Absolute Powerforce",
}

def traduzir_nomes(lista_pt):
    print("🤖 A IA está traduzindo os nomes para o Inglês oficial...")
    
    if not API_KEY: return {}

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Eu tenho uma lista de cartas de Yu-Gi-Oh em Português (Master Duel).
    Preciso que você as traduza para o nome oficial em INGLÊS (TCG/OCG).
    
    LISTA PT: {lista_pt}
    
    FORMATO DE RESPOSTA (JSON Puro):
    {{
        "Nome em Português": "Nome Oficial em Inglês",
        ...
    }}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Erro na tradução da IA: {e}")
        return {}

def criar_banco_inteligente():
    # 1. Traduzir com a IA
    mapa_traducao = traduzir_nomes(minha_lista_pt)
    
    if not mapa_traducao:
        return

    # 2. APLICAR AS CORREÇÕES MANUAIS (AQUI É A MÁGICA)
    # Sobrescreve o que a IA disse com o que você mandou na lista de correções
    if CORRECOES_MANUAIS:
        print("🔧 Aplicando correções manuais...")
        mapa_traducao.update(CORRECOES_MANUAIS)

    print("-" * 50)
    print("🌍 Baixando dados da API...")
    
    banco_final = []
    
    # 3. Buscar na API
    for nome_pt, nome_ingles in mapa_traducao.items():
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        try:
            r = requests.get(url, params={"name": nome_ingles})
            data = r.json()
            
            if "data" in data:
                carta_api = data["data"][0]
                print(f"✅ {nome_pt} -> {nome_ingles} (OK)")
                
                banco_final.append({
                    "nome_pt": nome_pt,
                    "nome_ingles": nome_ingles,
                    "tipo": carta_api["type"],
                    "efeito": carta_api["desc"],
                    "atk": carta_api.get("atk", "N/A"),
                    "def": carta_api.get("def", "N/A"),
                    "nivel": carta_api.get("level", "N/A")
                })
            else:
                print(f"⚠️ API não achou: '{nome_ingles}' (Verifique se o nome em inglês está exato)")
                
        except Exception as e:
            print(f"❌ Erro ao buscar {nome_ingles}: {e}")
            
        time.sleep(0.05)

    with open("master_duel_deck.json", "w", encoding="utf-8") as f:
        json.dump(banco_final, f, indent=4, ensure_ascii=False)
    
    print("-" * 50)
    print(f"🎉 Banco pronto! {len(banco_final)} cartas processadas.")

if __name__ == "__main__":
    criar_banco_inteligente()