import google.generativeai as genai
import requests
import json
import time
import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def pegar_chave():
    try:
        with open("api_key.txt", "r") as f: return f.read().strip()
    except: return None

API_KEY = pegar_chave()

# --- CORREÇÕES DE "ALUCINAÇÃO" DA VISÃO ---
# Aqui corrigimos o que a IA viu errado para o nome real da API
CORRECOES_VISUAIS = {
    # O que a IA viu -> O Nome Real em Inglês (TCG)
    "Synchron Resonator": "Synkron Resonator",
    "Calamity Resonator": "Chain Resonator", # Ela confunde o roxo as vezes
    "Fire Resonator": "Flare Resonator",
    "Garina the Raging Carnivore": "Red Gardna", # Alucinação visual comum
    "Ballista Dreadscythe": "Wandering King Wildwind",
    "Reincarnated Resonator": "Bone Archfiend",
    "Archfiend Roar Resonator": "Bone Archfiend",
    "Lost Power Force": "Absolute Powerforce",
    "Red Dragon Archfiend Abyss": "Hot Red Dragon Archfiend Abyss",
    "Red Dragon Archfiend Tyrant": "Hot Red Dragon Archfiend Bane",
    "Red Dragon Archfiend King": "Scarred Dragon Archfiend",
    "Baronne de Fleur": "Baronne de Fleur", # As vezes ela acerta, mas bom garantir
    "Uku-belt the Blade Dragon": "Kuibelt the Blade Dragon"
}

# --- 1. VISÃO COMPUTACIONAL ---
def analisar_imagem_do_deck(caminho_imagem):
    print(f"👁️ Analisando '{caminho_imagem}'...")
    
    if not API_KEY: 
        print("❌ Sem chave API.")
        return None

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        imagem = Image.open(caminho_imagem)
    except FileNotFoundError:
        print("❌ Imagem não encontrada!")
        return None

    prompt = """
    Analise este print de Yu-Gi-Oh! Master Duel.
    Liste TODAS as cartas (Main e Extra Deck).
    
    Retorne APENAS JSON:
    {
        "cartas": [
            {"pt": "Nome PT", "en": "Nome EN Oficial", "qtd": 1},
            ...
        ]
    }
    """
    
    try:
        response = model.generate_content([prompt, imagem], generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Erro na visão: {e}")
        return None

# --- 2. PROCESSAMENTO DE IMAGEM (BADGES) ---
def processar_imagem_com_badge(url_imagem, quantidade):
    try:
        response = requests.get(url_imagem)
        img = Image.open(BytesIO(response.content))
        
        if quantidade > 1:
            draw = ImageDraw.Draw(img)
            largura, altura = img.size
            texto = f"x{quantidade}"
            
            # Fonte Grande
            try: font = ImageFont.truetype("arial.ttf", 50)
            except: font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), texto, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            
            # Posição ajustada
            padding = 10
            x1 = largura - 20
            x0 = x1 - w - (padding * 2)
            y0 = int(altura * 0.40)
            y1 = y0 + h + (padding * 2)

            draw.rectangle([x0, y0, x1, y1], fill="#D32F2F", outline="white", width=3)
            draw.text((x0 + padding, y0 + padding - 5), texto, fill="white", font=font, stroke_width=2, stroke_fill="black")

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    except: return url_imagem

# --- 3. PRINCIPAL ---
def criar_novo_deck():
    print("--- 📸 CRIADOR DE DECK ---")
    imagem_arquivo = input("Nome da imagem (ex: deck.jpg): ")
    nome_json = input("Nome para salvar (ex: deck_resonate): ")
    
    if not nome_json.endswith(".json"): nome_json += ".json"

    dados_ia = analisar_imagem_do_deck(imagem_arquivo)
    if not dados_ia: return

    lista_cartas = dados_ia.get("cartas", [])
    print(f"🔍 Detectadas {len(lista_cartas)} cartas.")
    
    # --- APLICA CORREÇÕES ANTES DE BAIXAR ---
    for item in lista_cartas:
        nome_ia = item.get("en")
        # Se o nome que a IA achou estiver na nossa lista de correções, troca!
        if nome_ia in CORRECOES_VISUAIS:
            print(f"🔧 Corrigindo: {nome_ia} -> {CORRECOES_VISUAIS[nome_ia]}")
            item["en"] = CORRECOES_VISUAIS[nome_ia]

    print("-" * 50)
    print("🌍 Baixando dados...")
    
    banco_final = []
    
    for item in lista_cartas:
        nome_pt = item.get("pt")
        nome_en = item.get("en")
        qtd = item.get("qtd", 1)
        
        try:
            r = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php", params={"name": nome_en})
            data = r.json()
            
            if "data" in data:
                c = data["data"][0]
                print(f"✅ {nome_pt}")
                img_final = processar_imagem_com_badge(c["card_images"][0]["image_url_small"], qtd)

                banco_final.append({
                    "nome_pt": nome_pt,
                    "nome_ingles": nome_en,
                    "tipo": c["type"],
                    "efeito": c["desc"],
                    "imagem": img_final,
                    "qtd_maxima": qtd
                })
            else:
                print(f"⚠️ Falha API: {nome_en}")
        except: pass
        time.sleep(0.05)

    with open(nome_json, "w", encoding="utf-8") as f:
        json.dump(banco_final, f, indent=4)
    
    print(f"🎉 Deck salvo em '{nome_json}'!")

if __name__ == "__main__":
    criar_novo_deck()