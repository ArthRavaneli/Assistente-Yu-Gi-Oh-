🃏 Yu-Gi-Oh! Assistente de IA para Combos Iniciais (Multimodal RAG)

Um assistente tático inteligente para Yu-Gi-Oh! Master Duel que converte listas de decks em PDF para bancos de dados estruturados e utiliza LLMs avançadas para sugerir as melhores jogadas (combos) em tempo real baseadas na mão inicial.

![combo_dragao_9k](galeria_prints/print_galeria.png)

💡 Sobre o Projeto

Este projeto resolve a complexidade de pilotar decks meta em Yu-Gi-Oh! Master Duel. Ele elimina a necessidade de entrada manual de dados, utilizando IA para ler arquivos exportados diretamente do jogo e criando um sistema de RAG (Retrieval-Augmented Generation) para fornecer conselhos estratégicos contextualizados.

O Fluxo de Trabalho (Pipeline)

1. Exportação: O usuário exporta seu deck do jogo para o site oficial da Konami (Yu-Gi-Oh! Card Database) usando uma função presente no próprio jogo e baixa a lista em formato .PDF.

2. Ingestão Inteligente (importar_pdf.py):

    •  Utiliza o modelo Gemini 1.5 Pro para ler e interpretar a estrutura do PDF.

    •  Cruza os dados com a API pública do YGOPRODeck para obter metadados e imagens em alta resolução.

    •  Utiliza a biblioteca Pillow para processar as imagens, "carimbando" visualmente a quantidade de cópias (x1, x2, x3) diretamente no arquivo de imagem.

    •  Gera um banco de dados local .json persistente.

3. Interface Tática (app.py):

   •  Interface visual interativa construída em Streamlit com design customizado (CSS).

   •  Permite seleção visual da mão inicial e alternância dinâmica entre diferentes decks carregados.

   •  Envia o contexto exato das cartas (efeitos e nomes) para o Gemini 2.5 Flash , que atua como um "Pro Player", retornando um fluxograma passo-a-passo da melhor jogada.


🛠️ Tecnologias e Bibliotecas

   •  gemini-1.5-pro: Para análise estrutural de documentos (PDF) e extração de dados complexos.

   •  gemini-2.5-flash: Para raciocínio lógico rápido e geração de estratégia de jogo.

   •  Streamlit: Frontend reativo com gerenciamento de estado (session_state) e componentes personalizados.

   •  Pillow (PIL): Manipulação programática de imagens para adicionar indicadores visuais de quantidade.

   •  Requests & JSON: Integração de APIs REST e manipulação de dados locais.

🚀 Como Executar

1. Instalação

Certifique-se de ter o Python instalado. Clone o repositório e instale as dependências:

     pip install google-generativeai streamlit st-clickable-images requests pillow

2. Configuração da API (Crucial) 🔑
   
    1. Crie um arquivo chamado api_key.txt na raiz do projeto.
   
    2. Cole sua chave do Google AI Studio (Gemini) dentro dele.

⚠️ Atenção sobre Modelos: Este código está configurado para utilizar o Gemini 1.5 Pro (no importador) e o Gemini 2.5 Flash (no app). Se a sua chave de API não tiver acesso a esses modelos específicos, você precisará alterar os nomes dos modelos nas linhas correspondentes dos arquivos .py.


3. Gerando o Banco de Dados

Coloque o arquivo PDF do seu deck na pasta do projeto e execute:

        python importar_pdf.py

O script pedirá o nome do arquivo e gerará o JSON automaticamente.

4. Iniciando o Assistente

        streamlit run app.py


📸 Funcionalidades Visuais

Galeria Dinâmica: Separação automática entre Main Deck e Extra Deck.

Feedback Visual: As cartas selecionadas recebem destaque visual e contagem dinâmica.

Resposta Estruturada: A IA retorna a estratégia formatada em Cards HTML estilizados (CSS), facilitando a leitura rápida durante o duelo.
     
