import google.generativeai as genai
import requests
import json
import time
import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURAÇÃO ---
def pegar_chave():
    try:
        with open("api_key.txt", "r") as f: return f.read().strip()
    except: return None

API_KEY = pegar_chave()

# --- SEU DECK COM QUANTIDADES ---
meu_deck_config = {
    # Monstros
    "Dragão Branco de Olhos Azuis": 3,
    "Dragão Branco Alternativo de Olhos Azuis": 3,
    "Dragão Jato de Olhos Azuis": 1,
    "Dragão Branco de Olhos Profundos": 1,
    "Dragão MÁX do Caos de Olhos Azuis": 1,
    "A Pedra Branca das Lendas": 1,
    "A Pedra Branca dos Antigos": 3,
    "Sábio com Azul nos Olhos": 3,
    "Ditador dos Dragões": 3,
    "Espírito Dragão de Branco": 1,
    'Maxx "C"': 3,
    "Nibiru, o Ser Primitivo": 1,
    "Florescer de Cinzas & Primavera Feliz": 3,
    
    # Magias
    "Raigeki": 1,
    "Reviver Monstro": 1,
    "Trocar": 3,
    "Tempestade de Relâmpagos": 1,
    "A Melodia do Despertar do Dragão": 3,
    "Cards da Consonância": 3,
    "Retorno dos Senhores Dragão": 1,
    "Forma do Caos": 1,
    "Alma do Sucessor": 1,
    "Fusão Definitiva": 1,
    "Luz Verdadeira": 1,
    "Chamado pela Cova": 2,
    "Designador de Cancelamento": 1,
    
    # Armadilhas
    "Impermanência Infinita": 3,
    "A Criatura Definitiva da Destruição": 1,
    "Rivais Destinados": 1,

    # Extra
    "Dragão Tirano de Olhos Azuis": 1,
    "Dragão Gêmeo da Explosão de Olhos Azuis": 1,
    "Dragão Prateado de Olhos Cerúleos": 1,
    "Dragão Espírito de Olhos Azuis": 1,
    "Dragão Solar Hierático Suserano de Heliópolis": 1,
    "Dragão-Guarda Pisty": 1,
}

CORRECOES_MANUAIS = {
    "Dragão Gêmeo da Explosão de Olhos Azuis": "Blue-Eyes Twin Burst Dragon",
    "Dragão Solar Hierático Suserano de Heliópolis": "Hieratic Sun Dragon Overlord of Heliopolis",
    "Dragão MÁX do Caos de Olhos Azuis": "Blue-Eyes Chaos MAX Dragon",
    "Dragão Tirano de Olhos Azuis": "Blue-Eyes Tyrant Dragon",
    "Sábio com Azul nos Olhos": "Sage with Eyes of Blue",
    "Dragão Jato de Olhos Azuis": "Blue-Eyes Jet Dragon",
    "Dragão Branco de Olhos Profundos": "Deep-Eyes White Dragon",
    "Florescer de Cinzas & Primavera Feliz": "Ash Blossom & Joyous Spring"
}

# --- FUNÇÃO DE DESIGN: DESENHAR O NÚMERO (ATUALIZADA) ---
def processar_imagem_com_badge(url_imagem, quantidade):
    try:
        # 1. Baixa a imagem
        response = requests.get(url_imagem)
        img = Image.open(BytesIO(response.content))
        
        # Se tiver mais de 1 carta, desenha o badge
        if quantidade > 1:
            draw = ImageDraw.Draw(img)
            largura_img, altura_img = img.size
            
            # --- CONFIGURAÇÕES VISUAIS NOVAS ---
            texto = f"x{quantidade}"
            tamanho_fonte = 50  # AUMENTEI BASTANTE (era 24)
            padding_x = 12      # Espaço horizontal dentro do badge
            padding_y = 8       # Espaço vertical dentro do badge
            margem_direita = 0 # Distância da borda direita da carta

            # Tenta carregar fonte Arial Grande
            try:
                font = ImageFont.truetype("arial.ttf", tamanho_fonte)
            except:
                 # Fallback genérico se não tiver Arial
                try: font = ImageFont.truetype("calibri.ttf", tamanho_fonte)
                except: font = ImageFont.load_default()

            # Calcula tamanho do texto
            left, top, right, bottom = draw.textbbox((0, 0), texto, font=font)
            w_texto = right - left
            h_texto = bottom - top
            
            # --- CÁLCULO DA NOVA POSIÇÃO (MÉDIA ALTURA) ---
            # Posição X (Horizontal): Canto direito menos a margem
            x1_rect = largura_img - margem_direita
            x0_rect = x1_rect - w_texto - (padding_x * 2)

            # Posição Y (Vertical): Aprox. 40% da altura da carta (início da arte)
            y0_rect = int(altura_img * 0.80)
            y1_rect = y0_rect + h_texto + (padding_y * 2)

            # Desenha fundo vermelho (Badge) com borda mais grossa
            draw.rectangle([x0_rect, y0_rect, x1_rect, y1_rect], fill="#D32F2F", outline="white", width=3)
            
            # Desenha o texto centralizado no badge com contorno
            text_x = x0_rect + padding_x
            # Pequeno ajuste fino vertical para centralizar visualmente a fonte
            text_y = y0_rect + padding_y - (h_texto * 0.3) 
            draw.text((text_x, text_y), texto, fill="white", font=font, stroke_width=2, stroke_fill="black")

        # 2. Converte para Base64
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
        
    except Exception as e:
        print(f"Erro ao processar imagem ({url_imagem}): {e}")
        return url_imagem # Fallback

def traduzir_nomes(lista_pt):
    print("🤖 A IA está traduzindo...")
    if not API_KEY: return {}
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Traduza para INGLÊS OFICIAL (TCG): {lista_pt}. Responda JSON: {{'Nome PT': 'Nome EN'}}."
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except: return {}

def criar_banco_inteligente():
    lista_nomes = list(meu_deck_config.keys())
    mapa = traduzir_nomes(lista_nomes)
    if not mapa: return
    if CORRECOES_MANUAIS: mapa.update(CORRECOES_MANUAIS)

    print("🌍 Baixando e Editando Imagens (Gerando Badges maiores)...")
    banco = []
    
    for nome_pt, nome_ingles in mapa.items():
        try:
            r = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php", params={"name": nome_ingles})
            data = r.json()
            if "data" in data:
                c = data["data"][0]
                qtd = meu_deck_config.get(nome_pt, 1)
                
                print(f"🎨 Processando: {nome_pt} (x{qtd})...")
                
                # Processa a imagem
                url_original = c["card_images"][0]["image_url_small"]
                imagem_final = processar_imagem_com_badge(url_original, qtd)

                banco.append({
                    "nome_pt": nome_pt,
                    "nome_ingles": nome_ingles,
                    "tipo": c["type"],
                    "efeito": c["desc"],
                    "imagem": imagem_final,
                    "qtd_maxima": qtd
                })
        except: pass
        
    with open("master_duel_deck.json", "w", encoding="utf-8") as f:
        json.dump(banco, f, indent=4, ensure_ascii=False)
    print("🎉 Banco Atualizado! As etiquetas agora estão maiores e mais baixas.")

if __name__ == "__main__":
    criar_banco_inteligente()