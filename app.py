import streamlit as st
import json
import google.generativeai as genai
import os
from st_clickable_images import clickable_images

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Yu-Gi-Oh! AI", page_icon="🐉", layout="wide")

# --- CSS AVANÇADO (O SEGREDO DO DESIGN) ---
st.markdown("""
    <style>
        .block-container {padding-top: 3rem; padding-bottom: 5rem;}
        iframe {margin: auto; display: block;}
        
        /* Botão de remover na carta */
        div[data-testid="column"] > div > div > div > div > button {
            margin-top: -12px !important; padding-top: 0px !important;
            height: 25px; font-size: 10px;
        }

        /* --- ESTILOS DOS CARDS DE ESTRATÉGIA --- */
        
        /* Caixa do Campo Final (Destaque Dourado) */
        .final-field {
            background-color: #2e2300;
            border-left: 6px solid #ffd700;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 16px;
        }

        /* Caixa de Passo do Combo (Estilo Cyberpunk) */
        .combo-step {
            background-color: #131720;
            border: 1px solid #2d3748;
            border-left: 6px solid #00d4ff; /* Azul Neon */
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        .combo-step:hover {
            transform: translateX(5px); /* Efeito de movimento ao passar mouse */
            border-left-color: #00ff9d; /* Muda cor ao passar mouse */
        }
        
        /* Títulos e Textos dentro do Card */
        .step-action { color: #ffffff; font-weight: bold; font-size: 1.1em; }
        .step-reason { color: #a0aec0; font-size: 0.9em; font-style: italic; margin-top: 4px; display: block;}
        
        /* Setinha entre os passos */
        .arrow-down {
            text-align: center; color: #555; font-size: 20px; margin: -10px 0 5px 0;
        }

        /* Caixa de Risco (Vermelha) */
        .risk-box {
            background-color: #2c0b0e;
            border-left: 6px solid #ff4b4b;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR CHAVE ---
def carregar_chave_arquivo():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return None

chave_arquivo = carregar_chave_arquivo()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Painel")
    zoom_nivel = st.slider("🔍 Zoom", 80, 250, 130, 10)
    
    if chave_arquivo: api_key = chave_arquivo
    else: api_key = st.text_input("API Key:", type="password")
    
    archetype = st.text_input("Deck:", value="Blue-Eyes White Dragon")
    
    if 'mao_real' not in st.session_state: st.session_state['mao_real'] = []
    if 'galeria_id' not in st.session_state: st.session_state['galeria_id'] = 0

    st.divider()
    st.write(f"**Mão:** {len(st.session_state['mao_real'])}")
    if st.button("🗑️ Limpar", use_container_width=True):
        st.session_state['mao_real'] = []
        st.rerun()

# --- FUNÇÕES ---
@st.cache_data
def carregar_banco():
    try:
        with open("master_duel_deck.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def renderizar_galeria(titulo, lista_cartas, key_suffix):
    if not lista_cartas: return
    st.markdown(f"### {titulo}")
    
    imagens = [c["imagem"] for c in lista_cartas]
    titulos = [f"{c['nome_pt']} (No Deck: {c.get('qtd_maxima', 1)})" for c in lista_cartas]

    clique = clickable_images(
        imagens, titles=titulos,
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap", "background-color": "#0e1117", "padding": "10px"},
        img_style={"margin": "4px", "height": f"{zoom_nivel}px", "cursor": "pointer", "border-radius": "4px"},
        key=f"galeria_{key_suffix}_{st.session_state['galeria_id']}"
    )
    
    if clique > -1:
        carta = lista_cartas[clique]
        nome = carta['nome_pt']
        limit = carta.get('qtd_maxima', 1)
        atual = st.session_state['mao_real'].count(nome)
        
        if atual < limit:
            st.session_state['mao_real'].append(nome)
            st.toast(f"➕ {nome}")
        else:
            st.toast(f"⚠️ Máximo {limit}!", icon="🛑")
        
        st.session_state['galeria_id'] += 1
        st.rerun()

# --- INTERFACE ---
st.title("🐉 Galeria de Duelo")
deck = carregar_banco()

if deck:
    # MÃO
    st.markdown("#### ✋ Sua Mão Atual:")
    if st.session_state['mao_real']:
        cols = st.columns(10)
        w_calc = int(zoom_nivel * 0.71)
        for i, nome in enumerate(st.session_state['mao_real']):
            if i < 10:
                d = next((c for c in deck if c['nome_pt'] == nome), None)
                if d:
                    with cols[i]:
                        st.image(d['imagem'], width=w_calc)
                        if st.button("❌", key=f"del_{i}"):
                            st.session_state['mao_real'].pop(i)
                            st.rerun()
    else: st.info("Clique nas cartas abaixo.")

    st.divider()

    # --- LÓGICA DE ANÁLISE OTIMIZADA ---
    if st.session_state['mao_real']:
        if st.button("🧠 ANALISAR JOGADA (VISUAL)", type="primary", use_container_width=True):
            if not api_key: st.error("Faltou API Key")
            else:
                with st.spinner("Processando táticas avançadas..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        objs = []
                        for n in st.session_state['mao_real']:
                            o = next((x for x in deck if x['nome_pt'] == n), None)
                            if o: objs.append(o)
                        
                        detalhes = "\n".join([f"- {c['nome_pt']}: {c['efeito']}" for c in objs])
                        
                        # --- PROMPT FORMATADO PARA JSON (MUITO MAIS SEGURO PARA VISUAL) ---
                        prompt = f"""
                        Atue como Campeão Mundial de Yu-Gi-Oh.
                        DECK: {archetype}. MÃO: {', '.join([c['nome_pt'] for c in objs])}
                        DETALHES: {detalhes}
                        
                        OBJETIVO: Crie o melhor combo Turno 1.
                        
                        SAÍDA OBRIGATÓRIA: Responda EXCLUSIVAMENTE com este formato, separando os passos por '|||':
                        
                        CAMPO_FINAL: (Resumo do campo)
                        RISCOS: (Resumo de fraquezas)
                        COMBO_START
                        Passo 1: Ação Clara (Motivo curto)
                        |||
                        Passo 2: Ação Clara (Motivo curto)
                        |||
                        Passo 3: ...
                        COMBO_END
                        
                        REGRAS: Use Português. Seja extremamente direto. Não use Markdown na lista de combo, apenas texto puro separado por |||.
                        """
                        
                        raw_res = model.generate_content(prompt).text
                        st.session_state['analise_raw'] = raw_res
                        
                    except Exception as e: st.error(f"Erro: {e}")

    # --- RENDERIZAÇÃO BONITA DA RESPOSTA ---
    if 'analise_raw' in st.session_state:
        texto = st.session_state['analise_raw']
        
        # Processamento "Manual" do texto para criar o visual
        try:
            # Extrair partes
            campo_final = ""
            riscos = ""
            passos_combo = []
            
            linhas = texto.split('\n')
            modo_combo = False
            
            for linha in linhas:
                if "CAMPO_FINAL:" in linha:
                    campo_final = linha.replace("CAMPO_FINAL:", "").strip()
                elif "RISCOS:" in linha:
                    riscos = linha.replace("RISCOS:", "").strip()
                elif "COMBO_START" in linha:
                    modo_combo = True
                elif "COMBO_END" in linha:
                    modo_combo = False
                elif modo_combo:
                    # Aqui pegamos os passos separados por |||
                    partes = linha.split("|||")
                    for p in partes:
                        if p.strip(): passos_combo.append(p.strip())

            # 1. Renderiza Campo Final
            if campo_final:
                st.markdown(f'<div class="final-field">🎯 <b>CAMPO FINAL:</b> {campo_final}</div>', unsafe_allow_html=True)
            
            # 2. Renderiza o Fluxograma (Cards)
            st.markdown("### ⚡ Sequência de Jogadas:")
            for i, passo in enumerate(passos_combo):
                # Tenta separar Ação de Motivo se houver parenteses
                if "(" in passo and ")" in passo:
                    acao = passo.split("(")[0].strip()
                    motivo = passo.split("(")[1].replace(")", "").strip()
                else:
                    acao = passo
                    motivo = ""
                
                # HTML do Card
                html_card = f"""
                <div class="combo-step">
                    <div class="step-action">{acao}</div>
                    {f'<span class="step-reason">💡 {motivo}</span>' if motivo else ''}
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                
                # Seta para baixo (menos no último)
                if i < len(passos_combo) - 1:
                    st.markdown('<div class="arrow-down">⬇</div>', unsafe_allow_html=True)

            # 3. Renderiza Riscos
            if riscos:
                st.markdown(f'<div class="risk-box">⚠️ <b>ATENÇÃO / RISCOS:</b><br>{riscos}</div>', unsafe_allow_html=True)

        except Exception as parse_error:
            # Fallback se a IA não obedecer o formato exato
            st.warning("Visualização otimizada falhou, mostrando texto bruto:")
            st.write(texto)

    st.markdown("---")

    main = [c for c in deck if not any(x in c['tipo'].lower() for x in ["fusion", "synchro", "xyz", "link"])]
    extra = [c for c in deck if any(x in c['tipo'].lower() for x in ["fusion", "synchro", "xyz", "link"])]
    
    main.sort(key=lambda x: x['nome_pt'])
    extra.sort(key=lambda x: x['nome_pt'])

    renderizar_galeria("📖 Main Deck", main, "main")
    renderizar_galeria("🟣 Extra Deck", extra, "extra")
else:
    st.error("Rode 'python gerar_banco_ia.py'")