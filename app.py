import streamlit as st
import json
import google.generativeai as genai
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Yu-Gi-Oh! AI", page_icon="🃏")
st.title("🃏 Assistente de Duelo (PT-BR)")

# --- CARREGAR CHAVE AUTOMÁTICA ---
def carregar_chave_arquivo():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    return None

chave_arquivo = carregar_chave_arquivo()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuração")
    
    # Se achou o arquivo, avisa e usa a chave
    if chave_arquivo:
        st.success("🔑 API Key carregada do arquivo!")
        api_key = chave_arquivo
    else:
        # Se não achou, pede para digitar
        api_key = st.text_input("Cole sua Gemini API Key:", type="password")
        st.warning("Dica: Crie um arquivo 'api_key.txt' na pasta para não precisar digitar.")

    archetype = st.text_input("Nome do seu Deck:", value="Blue-Eyes White Dragon")

# --- FUNÇÕES ---
@st.cache_data
def carregar_banco():
    try:
        with open("master_duel_deck.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
            dados.sort(key=lambda x: x['nome_pt'])
            return dados
    except FileNotFoundError:
        return []

def gerar_estrategia(mao_selecionada, deck_archetype, key):
    if not key: return "⚠️ API Key necessária."
    
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        texto_cartas = ""
        nomes_mao = []
        for c in mao_selecionada:
            nomes_mao.append(c['nome_pt'])
            texto_cartas += f"- {c['nome_pt']} (Efeito: {c['efeito']})\n"

        prompt = f"""
        Atue como Pro Player de Yu-Gi-Oh Master Duel.
        DECK: {deck_archetype}
        MÃO: {', '.join(nomes_mao)}
        
        DETALHES:
        {texto_cartas}
        
        OBJETIVO: Melhor combo Turno 1.
        
        REGRAS:
        1. Responda APENAS usando os nomes em Português.
        2. Seja direto: 🎯 Campo Final, ⚡ Combo (Passo a passo com setas).
        3. Fale Português.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro: {e}"

# --- INTERFACE ---
deck_data = carregar_banco()

if deck_data:
    opcoes = [c['nome_pt'] for c in deck_data]
    selecao = st.multiselect("Sua mão:", options=opcoes, max_selections=6)

    if st.button("🧠 Gerar Jogada", type="primary"):
        if selecao:
            mao_objs = [c for c in deck_data if c['nome_pt'] in selecao]
            res = gerar_estrategia(mao_objs, archetype, api_key)
            st.markdown(res)
else:
    st.warning("Banco de dados vazio. Rode o script gerador primeiro.")