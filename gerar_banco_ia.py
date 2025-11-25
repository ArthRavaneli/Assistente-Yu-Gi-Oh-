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
    "Dragão Branco de Olhos Azuis",
    "A Pedra Branca das Lendas",
    'Sábio com Azul nos Olhos',
    "A Pedra Branca dos Antigos",
    "Florescer de Cinzas & Primavera",
    "Ditador dos Dragões",
    "Dragão Branco Alternativo de Olhos Azuis",
    "Espírito Dragão de Branco",
    "Dragão do Abismo de Olhos Azuis",
    "Dragão Jato de Olhos Azuis",
    "Dragão Branco de Olhos Profundos",
    "Dragão MÁX do Caos de Olhos Azuis",
    "Raigeki",
    "Reviver Monstro",
    "Trocar",
    "Tempestade de Relâmpagos",
    "A Melodia do Despertar do Dragão",
    "Cards da Consonância",
    "Retorno dos Senhores Dragão",
    "Forma do Caos",
    "Alma do Sucessor",
    "Fusão Definitiva",
    "Impermanência Infinita",
    "A Criatura Definitiva da Destruição",
    "Rivais Destinados",
    "Luz Verdadeira",
    "Dragão Tirano de Olhos Azuis",
    "Dragão Gêmeo da Explosão de Olhos Azuis",
    "Dragão Prateado de Olhos Cerúleos",
    "Dragão Espírito de Olhos Azuis",
    "Dragão Solar Hierático Suserano de Heliópolis",
    "Dragão-Guarda Pisty",
]

# --- CORREÇÕES MANUAIS (O TIRA-TEIMA) ---
# Se a IA errar ou a API não achar, coloque a correção aqui.
# Formato: "Nome em Português da lista": "Nome Oficial em Inglês Correto"
CORRECOES_MANUAIS = {
    
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