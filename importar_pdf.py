import google.generativeai as genai
import requests
import json
import time
import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURAÇÃO DE CAMINHOS ---
PASTA_DECKS = "yu_gi_oh_decks"

# Garante que a pasta existe (cria se não existir)
if not os.path.exists(PASTA_DECKS):
    os.makedirs(PASTA_DECKS)

def pegar_chave():
    """Tenta ler a API Key do arquivo api_key.txt"""
    try:
        with open("api_key.txt", "r") as f: return f.read().strip()
    except: return None

API_KEY = pegar_chave()

# --- FUNÇÕES DE API E DESIGN ---

def buscar_dados_api(nome_ingles):
    """Busca na API YGOPRODeck, tentando PT-BR e depois EN."""
    url_api = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    
    # 1. Tenta PT (para o nome bonito)
    try:
        r = requests.get(url_api, params={"name": nome_ingles, "language": "pt"})
        data = r.json()
        if "data" in data: return data["data"][0]
    except: pass

    # 2. Tenta EN (para garantir que pega o efeito)
    try:
        r = requests.get(url_api, params={"name": nome_ingles})
        data = r.json()
        if "data" in data: return data["data"][0]
    except: pass
    
    return None

def processar_imagem_com_badge(url_imagem, quantidade):
    """Baixa a imagem e aplica o badge 'xN' embutido em Base64."""
    try:
        response = requests.get(url_imagem)
        img = Image.open(BytesIO(response.content))
        
        if quantidade > 1:
            draw = ImageDraw.Draw(img)
            largura, altura = img.size
            texto = f"x{quantidade}"
            
            try: font = ImageFont.truetype("arial.ttf", 50)
            except: font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), texto, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x1, y0 = largura - 20, int(altura * 0.40)
            x0, y1 = x1 - w - 20, y0 + h + 16
            
            draw.rectangle([x0, y0, x1, y1], fill="#D32F2F", outline="white", width=3)
            draw.text((x0 + 10, y0 + 4), texto, fill="white", font=font, stroke_width=2, stroke_fill="black")
            
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    except: return url_imagem

# --- FUNÇÃO PRINCIPAL: LER O PDF E GERAR O JSON ---
def criar_deck_via_pdf():
    print("--- 📑 IMPORTADOR DECK PDF COM IA ---")
    print(f"📂 Diretório de trabalho: ./{PASTA_DECKS}/")
    
    # 1. Entrada do usuário
    pdf_arquivo_input = input("Digite o NOME do arquivo PDF (ex: deck_dragao_branco): ").strip()
    
    # --- VERIFICAÇÃO ROBUSTA COM CAMINHO DA PASTA ---
    pdf_arquivo_full = None
    
    # Monta os caminhos possíveis DENTRO DA PASTA DE DECKS
    caminho_com_pdf = os.path.join(PASTA_DECKS, pdf_arquivo_input if pdf_arquivo_input.endswith(".pdf") else pdf_arquivo_input + ".pdf")
    
    # Verifica se o arquivo existe
    if os.path.exists(caminho_com_pdf):
        pdf_arquivo_full = caminho_com_pdf
    
    if not pdf_arquivo_full:
        print(f"❌ Erro: Arquivo não encontrado em '{caminho_com_pdf}'")
        print(f"DICA: O arquivo PDF deve estar dentro da pasta '{PASTA_DECKS}'.")
        return
        
    # Nomeia o JSON com base no nome do PDF (e define caminho de saída na pasta certa)
    nome_arquivo_pdf = os.path.basename(pdf_arquivo_full)
    base_name = os.path.splitext(nome_arquivo_pdf)[0]
    caminho_json_saida = os.path.join(PASTA_DECKS, f"{base_name}.json")

    if not API_KEY: 
        print("❌ Sem chave API. Insira sua chave no 'api_key.txt'.")
        return

    # 1. ANÁLISE ESTRUTURAL DO PDF COM GEMINI
    print(f"\n👁️ Enviando '{pdf_arquivo_full}' para análise estrutural (Gemini Flash)...")
    
    genai.configure(api_key=API_KEY)
    # Mantivemos o modelo que estava no seu código (Flash)
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    try:
        # AQUI USAMOS O CAMINHO COMPLETO (pasta/arquivo.pdf)
        pdf_file = genai.upload_file(pdf_arquivo_full) 
    except Exception as e:
        print(f"❌ Erro ao subir arquivo para IA: {e}")
        return

    prompt = f"""
    Analise o documento PDF anexo que contém a lista de um deck de Yu-Gi-Oh! em formato de tabela (QUANTIDADE e NOME DA CARTA em Inglês).
    Sua tarefa é extrair todas as cartas listadas no 'Main Deck' e 'Extra Deck'. IGNORE O 'SIDE DECK'.
    
    Responda EXCLUSIVAMENTE um JSON que consolide as quantidades por nome:
    {{
        "cartas": [
            {{"en": "Blue-Eyes White Dragon", "qtd": 3}},
            {{"en": "Raigeki", "qtd": 1}},
            ...
        ]
    }}
    """
    
    lista_cartas = []
    try:
        # Usando generation_config conforme sua versão corrigida
        response = model.generate_content([prompt, pdf_file], 
            generation_config={"response_mime_type": "application/json"}
        )
        
        raw_json_str = response.text.strip()
        if raw_json_str.startswith("```json"):
            raw_json_str = raw_json_str.strip("```json").strip("```").strip()

        dados_ia = json.loads(raw_json_str)
        lista_cartas = dados_ia.get("cartas", [])
        
    except Exception as e:
        print(f"❌ Erro na análise do PDF. Erro: {e}")
        lista_cartas = []
    finally:
        # Limpar o arquivo do servidor do Gemini
        try:
            genai.delete_file(pdf_file.name)
        except: pass
    
    if not lista_cartas:
        print("\n❌ Nenhuma carta extraída da análise da IA. Verifique se o PDF está no formato esperado.")
        return
        
    # 2. PROCESAMENTO E DOWNLOAD DA API YGOPRODECK
    
    print(f"\n📊 Encontradas {len(lista_cartas)} cartas únicas. Baixando dados...")
    print("-" * 50)
    
    banco_final = []
    
    for item in lista_cartas:
        name_en = item.get("en")
        qtd = item.get("qtd", 1)
        
        dados_api = buscar_dados_api(name_en)
        
        if dados_api:
            nome_display = dados_api["name"] 
            print(f"✅ {nome_display} (x{qtd})")
            
            img_final = processar_imagem_com_badge(dados_api["card_images"][0]["image_url_small"], qtd)
            
            banco_final.append({
                "nome_pt": nome_display,
                "nome_ingles": name_en,
                "tipo": dados_api["type"],
                "efeito": dados_api["desc"],
                "imagem": img_final,
                "qtd_maxima": qtd
            })
        else:
            print(f"⚠️ API YGOPRODeck não achou dados para: {name_en}")
        
        time.sleep(0.05)

    # 3. Salvar (Agora no caminho correto dentro da pasta)
    with open(caminho_json_saida, "w", encoding="utf-8") as f:
        json.dump(banco_final, f, indent=4, ensure_ascii=False)
    
    print("-" * 50)
    print(f"🎉 SUCESSO! Deck salvo em '{caminho_json_saida}'.")

if __name__ == "__main__":
    criar_deck_via_pdf()