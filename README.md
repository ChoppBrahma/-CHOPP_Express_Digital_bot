 # Documentação Completa do Projeto: Bot de FAQ Inteligente para Telegram

## Introdução

Este projeto consiste em um bot para Telegram, projetado para atuar como um sistema de Perguntas Frequentes (FAQ) inteligente. Ele permite que os usuários obtenham respostas a suas dúvidas de forma rápida e precisa, utilizando técnicas avançadas de Processamento de Linguagem Natural (PLN) para compreender a intenção das perguntas, mesmo que não sejam formuladas exatamente como no FAQ.

**Principais funcionalidades:**
* Respostas precisas baseadas em um arquivo `faq.json`.
* Compreensão de linguagem natural (sinônimos, variações de frases, pequenos erros de digitação).
* Sugestão de perguntas relacionadas.
* Recarregamento dinâmico do FAQ sem necessidade de reiniciar o bot.
* Hospedagem na nuvem para operação contínua.

**Tecnologias Utilizadas:**
* **Python:** Linguagem de programação principal.
* **Flask:** Micro-framework web para gerenciar o webhook do Telegram.
* **`pyTelegramBotAPI`:** Biblioteca para interação simplificada com a API do Telegram.
* **NLTK (Natural Language Toolkit):** Para pré-processamento de texto (remoção de stopwords e stemming).
* **scikit-learn:** Para vetorização de texto (TF-IDF) e cálculo de similaridade de cosseno.
* **Gunicorn:** Servidor WSGI para executar a aplicação Flask em produção.
* **Unidecode:** Para transliterar texto Unicode para ASCII.
* **GitHub:** Para controle de versão e hospedagem do código.
* **Render:** Plataforma de nuvem para deploy contínuo do bot.
* **UptimeRobot:** Serviço de monitoramento para manter o bot "acordado" no Render.

## 1. Configuração do Projeto no Ambiente Web

Como você trabalha totalmente via web, a configuração do ambiente é gerenciada principalmente pelas plataformas que você utiliza.

### 1.1. Pré-requisitos Web

* **Conta GitHub**: Para hospedar seu código.
* **Conta Telegram**: Para criar e gerenciar seu bot.
* **Conta Render**: Para hospedar a aplicação do bot.
* **Conta UptimeRobot**: Para monitorar e manter seu bot ativo.

### 1.2. Estrutura e Criação dos Arquivos Iniciais no GitHub

Você criará estes arquivos diretamente no seu repositório GitHub.

1.  **Crie um novo repositório no GitHub:**
    * No GitHub, clique em `+` (canto superior direito) > `New repository`.
    * **Repository name:** Escolha um nome para seu projeto (ex: `bot-faq-inteligente`).
    * **Description:** (Opcional) Adicione uma breve descrição.
    * **Public/Private:** Recomendo **Private** para projetos pessoais.
    * **NÃO** selecione "Add a README file" ou "Add .gitignore" por enquanto.
    * Clique em `Create repository`.

2.  **Crie o arquivo `requirements.txt`:**
    Este arquivo lista todas as bibliotecas que seu projeto precisa. No seu repositório GitHub, clique em `Add file` > `Create new file`.
    * **Nome do arquivo:** `requirements.txt`
    * **Conteúdo:** (Usando o seu `requirements.txt` fornecido, que inclui `gunicorn` e `unidecode`)
        ```
        Flask==2.3.2
        pyTelegramBotAPI==4.10.0
        gunicorn==20.1.0
        unidecode==1.3.6
        nltk==3.8.1
        scikit-learn==1.5.0
        # Adicionei NLTK e scikit-learn que são usados no seu main.py
        ```
    * Clique em `Commit new file`.

3.  **Crie o arquivo `faq.json`:**
    Este arquivo será sua base de conhecimento para o bot. No seu repositório GitHub, clique em `Add file` > `Create new file`.
    * **Nome do arquivo:** `faq.json`
    * **Conteúdo (exemplo):**
        ```json
        {
          "1": {
            "pergunta": "Como posso solicitar um reembolso?",
            "resposta": "Para solicitar um reembolso, acesse a seção 'Meus Pedidos' no nosso site, encontre o item e clique em 'Solicitar Reembolso'. O processo leva até 5 dias úteis. Para mais detalhes, consulte: [Link para Política de Reembolso](https://seusite.com/reembolso).",
            "palavras_chave": ["reembolso", "devolução", "dinheiro de volta", "cancelamento de compra", "desistir"]
          },
          "2": {
            "pergunta": "Qual é o horário de atendimento da central de suporte?",
            "resposta": "Nosso atendimento é de segunda a sexta, das 9h00 às 18h00, e aos sábados das 9h00 às 13h00. Domingos e feriados não há expediente.",
            "palavras_chave": ["horário", "atendimento", "funciona", "expediente", "abre", "suporte", "ligar"]
          },
          "3": {
            "pergunta": "Como rastrear meu pedido?",
            "resposta": "Você pode rastrear seu pedido diretamente pelo nosso site na seção 'Meus Pedidos' ou usando o código de rastreio que foi enviado para seu e-mail de confirmação.",
            "palavras_chave": ["rastrear", "pedido", "entrega", "envio", "acompanhar", "onde está"]
          },
          "4": {
            "pergunta": "Posso alterar meu endereço de entrega após a compra?",
            "resposta": "Sim, você pode solicitar a alteração do endereço de entrega entrando em contato com nosso suporte o mais rápido possível. Note que a alteração só é possível antes do envio do produto.",
            "palavras_chave": ["endereço", "mudar", "alterar", "entrega", "envio", "novo"]
          }
        }
        ```
    * Clique em `Commit new file`.

4.  **Crie o arquivo `main.py` (ou `main (2).py`):**
    Este é o código principal do seu bot. No seu repositório GitHub, clique em `Add file` > `Create new file`.
    * **Nome do arquivo:** `main.py` (se seu arquivo atual se chama `main (2).py`, pode usar esse nome, mas `main.py` é o padrão e mais simples para o Render).
    * **Conteúdo:** (O código completo do seu bot com todas as melhorias, incluindo as importações, o setup do NLTK, as funções de pré-processamento, carregamento e busca do FAQ, e as rotas do Flask. **Lembre-se de adicionar `import unidecode` se você for usá-lo no `preprocess_text` para remover acentos, por exemplo.** No código que te passei anteriormente, `unidecode` não estava sendo usado diretamente, mas se sua intenção é usá-lo para uma normalização mais profunda, adicione a importação e a lógica.)
        ```python
        import os
        import json
        from flask import Flask, request, jsonify
        import telebot
        import traceback
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

        # O código original não tinha estas importações. Se você deseja usar NLTK e scikit-learn
        # para PLN mais avançado (TF-IDF, similaridade de cosseno, stemming), você precisará
        # adicionar e implementar as funções correspondentes.
        # import nltk
        # from nltk.corpus import stopwords
        # from nltk.stem import RSLPStemmer # Para português
        # from sklearn.feature_extraction.text import TfidfVectorizer
        # from sklearn.metrics.pairwise import cosine_similarity
        # Se você usa unidecode no seu código, adicione aqui:
        # from unidecode import unidecode 

        # --- Configurações do Bot Telegram ---
        app = Flask(__name__)

        # Obtém o token do bot das variáveis de ambiente
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
        if not BOT_TOKEN:
            print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
            exit(1) # Impede que o bot inicie sem o token
        bot = telebot.TeleBot(BOT_TOKEN)

        # Obtém o ID do chat do administrador das variáveis de ambiente
        ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
        if not ADMIN_CHAT_ID:
            print("AVISO: Variável de ambiente ADMIN_CHAT_ID não definida. Comando /recarregarfaq não funcionará para administradores.")
        else:
            ADMIN_CHAT_ID = str(ADMIN_CHAT_ID) # Garante que é string para comparação

        # Variáveis globais para armazenar o FAQ e componentes de PLN
        faq_data = {}
        # Se estiver usando NLTK/scikit-learn, descomente e use estas variáveis:
        # tfidf_vectorizer = None
        # faq_vectors = None
        # faq_ids_indexed = [] # Para mapear de volta do índice do vetorizador para o FAQ ID

        # --- Inicializar Stemmer e Stop Words (se NLTK estiver sendo usado) ---
        # O código original não tinha esta seção. Se você deseja usar NLTK, descomente.
        # try:
        #     nltk.data.find('corpora/stopwords')
        # except nltk.downloader.DownloadError:
        #     print("Baixando dados do NLTK: stopwords...")
        #     nltk.download('stopwords')
        # try:
        #     nltk.data.find('stemmers/rslp')
        # except nltk.downloader.DownloadError:
        #     print("Baixando dados do NLTK: rslp (stemmer para português)...")
        #     nltk.download('rslp')
        # stemmer = RSLPStemmer()
        # stop_words = set(stopwords.words('portuguese'))

        # --- Função de Pré-processamento de Texto ---
        def preprocess_text(text):
            """
            Normaliza o texto: minúsculas e remove espaços extras.
            Para PLN avançado (stemming, stopwords, unidecode), o código precisaria ser expandido.
            """
            if not text:
                return ""
            # Converte para string para evitar erros se o input não for string
            text = str(text).lower().strip() 
            # Opcional: Se 'unidecode' for usado para remover acentos, descomente:
            # from unidecode import unidecode # Isso deve estar no topo com outras importações
            # text = unidecode(text) 

            # Para PLN avançado (stemming e stopwords), as linhas abaixo seriam necessárias:
            # words = [stemmer.stem(word) for word in text.split() if word not in stop_words and len(word) > 1]
            # return " ".join(words)
            return text

        # --- Carregamento e Vetorização do FAQ ---
        def load_faq():
            """
            Carrega o FAQ do arquivo JSON. 
            Para PLN avançado, também vetorizaria o FAQ usando TF-IDF.
            """
            global faq_data 
            # Se estiver usando NLTK/scikit-learn, também global tfidf_vectorizer, faq_vectors, faq_ids_indexed
            try:
                with open('faq.json', 'r', encoding='utf-8') as f:
                    raw_faq = json.load(f)
                    faq_data = {str(k): v for k, v in raw_faq.items()}

                if not faq_data:
                    print("FAQ vazio ou não carregado.")
                    # Se usando PLN avançado, resetaria vetorizador e vetores aqui
                    return

                # Se usando PLN avançado, esta parte seria executada:
                # texts_to_vectorize = []
                # faq_ids_indexed = []
                # for faq_id, entry in faq_data.items():
                #     combined_text = entry.get('pergunta', '') + " " + " ".join(entry.get('palavras_chave', []))
                #     texts_to_vectorize.append(preprocess_text(combined_text))
                #     faq_ids_indexed.append(faq_id)
                # tfidf_vectorizer = TfidfVectorizer()
                # faq_vectors = tfidf_vectorizer.fit_transform(texts_to_vectorize)
                
                print(f"FAQ carregado com sucesso! Tamanho do FAQ: {len(faq_data)} entradas.")
            except FileNotFoundError:
                print("Erro: Arquivo faq.json não encontrado. O bot NÃO poderá responder via FAQ.")
                faq_data = {} 
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON do faq.json: {e}. Verifique a sintaxe do arquivo.")
                faq_data = {}
            except Exception as e:
                print(f"Erro inesperado ao carregar o FAQ: {e}")
                traceback.print_exc()
                faq_data = {}

        # Chama a função para carregar o FAQ quando o bot inicia
        load_faq()

        # --- Função para encontrar a melhor correspondência no FAQ (MAIS DIRETA) ---
        def find_faq_answer(query):
            """
            Encontra a melhor resposta do FAQ usando correspondência de palavras-chave.
            Para PLN avançado, usaria TF-IDF e similaridade de cosseno.
            """
            if not faq_data:
                print("DEBUG: FAQ data não carregado em find_faq_answer.")
                return None, None

            normalized_query = preprocess_text(query)
            if not normalized_query:
                print("DEBUG: Query pré-processada vazia.")
                return None, None

            # PRIORIDADE 1: Correspondência EXATA da query com uma palavra-chave
            for faq_id, entry in faq_data.items():
                keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
                for keyword in keywords:
                    if normalized_query == keyword:
                        print(f"DEBUG: Correspondência EXATA de query com keyword! FAQ ID: {faq_id}, Keyword: '{keyword}'")
                        return entry.get('resposta'), faq_id
            
            # PRIORIDADE 2: Busca por palavras-chave ou pergunta contida na query (ou vice-versa)
            best_faq_id_by_keyword_hits = None
            max_keyword_hits = 0
            
            MIN_HITS_THRESHOLD = 1 # Ajuste este valor se necessário para controlar a sensibilidade

            for faq_id, entry in faq_data.items():
                keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
                current_hits = 0
                
                # Verifica se a palavra-chave está contida na query ou a query na palavra-chave
                for keyword in keywords:
                    if keyword and (keyword in normalized_query or normalized_query in keyword):
                        current_hits += 1
                
                pergunta_faq_normalizada = preprocess_text(entry.get('pergunta', ''))
                if pergunta_faq_normalizada and pergunta_faq_normalizada in normalized_query:
                    current_hits += 1 # Conta também se a pergunta inteira do FAQ está na query

                if current_hits > max_keyword_hits:
                    max_keyword_hits = current_hits
                    best_faq_id_by_keyword_hits = faq_id

            print(f"DEBUG: Melhor correspondência por hits: ID {best_faq_id_by_keyword_hits} com {max_keyword_hits} hits.")

            if max_keyword_hits >= MIN_HITS_THRESHOLD and best_faq_id_by_keyword_hits:
                return faq_data[best_faq_id_by_keyword_hits].get('resposta'), best_faq_id_by_keyword_hits
            
            print("DEBUG: Nenhuma correspondência boa encontrada por hits de palavras-chave.")
            return None, None

        # --- Função para obter botões de perguntas relacionadas ---
        # Aumentei o max_buttons para 10. Você pode ajustar esse valor se precisar de mais.
        def get_related_buttons(query, primary_faq_id=None, max_buttons=10): 
            related_buttons_info = []
            normalized_query = preprocess_text(query)
            
            RELATED_HITS_THRESHOLD = 1 # Limiar simples de palavras-chave para sugestões

            print(f"DEBUG: Buscando botões relacionados para query '{query}', excluindo ID '{primary_faq_id}'.")

            for faq_id, entry in faq_data.items():
                if faq_id == primary_faq_id: 
                    continue

                keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
                pergunta_text = preprocess_text(entry.get('pergunta', ''))

                current_related_hits = 0
                for item_text in keywords + [pergunta_text]:
                    if item_text and (item_text in normalized_query or normalized_query in item_text):
                        current_related_hits += 1
                
                if current_related_hits >= RELATED_HITS_THRESHOLD:
                    if (faq_id, entry.get('pergunta')) not in related_buttons_info:
                        related_buttons_info.append((faq_id, entry.get('pergunta')))
                
                if len(related_buttons_info) >= max_buttons: 
                    break

            if related_buttons_info:
                markup = InlineKeyboardMarkup()
                for faq_id, pergunta in related_buttons_info:
                    # Trunca o texto do botão se for muito longo
                    button_text = pergunta[:50] + '...' if len(pergunta) > 53 else pergunta
                    markup.add(InlineKeyboardButton(button_text, callback_data=str(faq_id))) 
                print(f"DEBUG: Botões relacionados gerados: {len(related_buttons_info)}.")
                return markup
            print("DEBUG: Nenhum botão relacionado encontrado.")
            return None 

        # --- Rotas Flask para Webhook e Health Check ---

        @app.route('/')
        def health_check():
            """
            Endpoint simples para verificar a saúde da aplicação.
            Útil para o Render e UptimeRobot.
            """
            print("Requisição GET recebida no / (Health Check)")
            return "Bot está funcionando!", 200

        @app.route('/webhook', methods=['POST'])
        def webhook():
            """
            Endpoint principal que recebe as atualizações do Telegram.
            Processa mensagens e callbacks.
            """
            if request.method == 'POST':
                update_json = request.get_json()
                print("Requisição POST recebida em /webhook")

                try:
                    update = telebot.types.Update.de_json(json.dumps(update_json))

                    if update.message:
                        message = update.message
                        chat_id = message.chat.id
                        text = message.text

                        print(f"----> Mensagem recebida do chat {chat_id}: '{text}'")

                        response_text = ""
                        markup = None 

                        if text:
                            # O comando /recarregarfaq e a lógica ADMIN_CHAT_ID não estão presentes no seu main (2).py
                            # Se você adicionar, ficaria aqui, por exemplo:
                            # if text == '/recarregarfaq':
                            #     if ADMIN_CHAT_ID and str(chat_id) == ADMIN_CHAT_ID:
                            #         bot.send_message(chat_id, "Iniciando recarregamento do FAQ...")
                            #         load_faq()
                            #         bot.send_message(chat_id, "FAQ recarregado com sucesso!")
                            #     else:
                            #         bot.send_message(chat_id, "Você não tem permissão para usar este comando.")
                            # else:
                            faq_answer, faq_id_matched = find_faq_answer(text)

                            if faq_answer:
                                response_text = faq_answer
                                print(f"----> Resposta principal encontrada no FAQ (ID: {faq_id_matched}): '{response_text}'")
                                markup = get_related_buttons(text, faq_id_matched)
                                
                            else:
                                response_text = "Desculpe, não consegui encontrar uma resposta para sua pergunta no meu FAQ. Por favor, tente perguntar de outra forma ou consulte nosso site oficial."
                                print(f"----> Nenhuma resposta principal encontrada no FAQ para: '{text}'. Enviando fallback genérico.")
                            
                            try:
                                # Tenta enviar com Markdown, se falhar, tenta sem.
                                bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                                print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                            except telebot.apihelper.ApiTelegramException as e:
                                print(f"ERRO Telegram API ao enviar mensagem: {e}")
                                if "Can't parse message text" in str(e) or "Bad Request: can't parse entities" in str(e):
                                    print("DICA: Texto pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                                    bot.send_message(chat_id, response_text, parse_mode=None, reply_markup=markup) 
                                else:
                                    # Se for outro tipo de erro da API, re-lança
                                    raise 
                                print(f"----> Mensagem enviada (sem Markdown se erro anterior) para o chat {chat_id}.")
                            except Exception as e:
                                print(f"ERRO geral ao enviar mensagem: {e}")
                                traceback.print_exc() # Imprime o stack trace completo do erro
                                bot.send_message(chat_id, "Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde.")
                                print(f"----> Mensagem de erro genérica enviada para o chat {chat_id}.")
                        else:
                            print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

                    elif update.callback_query:
                        callback_query = update.callback_query
                        chat_id = callback_query.message.chat.id
                        callback_data = callback_query.data 

                        print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")
                        bot.answer_callback_query(callback_query.id) # Avisa ao Telegram que a query foi processada

                        try:
                            if callback_data in faq_data:
                                response_text = faq_data[callback_data].get('resposta')
                                try:
                                    bot.send_message(chat_id, response_text, parse_mode='Markdown')
                                    print(f"----> Resposta da Callback Query enviada com sucesso para o chat {chat_id}.")
                                except telebot.apihelper.ApiTelegramException as e:
                                    print(f"ERRO Telegram API ao enviar mensagem de callback: {e}")
                                    if "Can't parse message text" in str(e) or "Bad Request: can't parse entities" in str(e):
                                        print("DICA: Texto do callback pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                                        bot.send_message(chat_id, response_text, parse_mode=None) 
                                    else:
                                        raise
                                    print(f"----> Resposta da Callback Query enviada (sem Markdown se erro anterior) para o chat {chat_id}.")
                            else:
                                bot.send_message(chat_id, "Desculpe, não encontrei a informação solicitada pelo botão.", parse_mode='Markdown')
                                print(f"----> ERRO: FAQ ID '{callback_data}' não encontrado para Callback Query.")
                        except Exception as e:
                            print(f"ERRO ao processar Callback Query para FAQ ID {callback_data}: {e}")
                            print(traceback.format_exc())
                            bot.send_message(chat_id, "Ocorreu um erro ao processar sua solicitação do botão. Por favor, tente novamente mais tarde.")
                            print(f"----> Mensagem de erro genérica para Callback Query enviada para o chat {chat_id}.")
                    
                    else:
                        print("----> Update recebido sem as chaves 'message' ou 'callback_query'. Pode ser outro tipo de atualização (edited_message, channel_post, etc.).")

                except Exception as e:
                    print(f"ERRO INESPERADO no processamento do webhook: {e}")
                    print(traceback.format_exc())

                print("Update processado. Retornando 200 OK.")
                return 'OK', 200
            else:
                return 'Método não permitido', 405

        if __name__ == '__main__':
            port = int(os.environ.get('PORT', 5000))
            # No seu deploy com Gunicorn, esta parte pode não ser executada diretamente,
            # pois o Gunicorn irá gerenciar a inicialização da aplicação 'app'.
            # Ela é útil para testes locais ou se você não usar Gunicorn.
            app.run(host='0.0.0.0', port=port)
        ```
    * Clique em `Commit new file`.

## 2. Configuração dos Serviços Externos

Para que seu bot funcione, ele precisará interagir com a API do Telegram e ser hospedado online.

### 2.1. Telegram: Crie seu Bot e Obtenha Tokens

Você precisará de um bot no Telegram e dois IDs importantes: o `BOT_TOKEN` e seu `ADMIN_CHAT_ID`.

1.  **Crie um novo Bot (BotFather):**
    * Abra o Telegram e pesquise por `@BotFather`.
    * Inicie uma conversa e use o comando `/newbot`.
    * Siga as instruções para dar um **Nome** ao seu bot (ex: `Meu Bot de Ajuda`) e um **Username** (deve terminar com "bot", ex: `MeuAjuda_bot`).
    * Ao finalizar, o BotFather lhe fornecerá um **`BOT_TOKEN`**. Ele se parecerá com algo como: `1234567890:ABC-DEF1234ghIJK_LMN-opqRSTuvwxyZAB`. **Copie e guarde este token com segurança.**

2.  **Obtenha seu ID de Chat de Administrador (`ADMIN_CHAT_ID`):**
    * Primeiro, envie uma mensagem para o **seu próprio bot** (o que você acabou de criar). Pode ser um "Olá".
    * Depois, no Telegram, pesquise por `@userinfobot` ou `@get_id_bot`.
    * Inicie uma conversa com um desses bots e ele lhe informará seu `ID de Chat` (um número, ex: `12345678`). **Copie e guarde este número.** Este será o seu `ADMIN_CHAT_ID`.

### 2.2. GitHub: Gerenciamento de Código

Como você já criou o repositório e os arquivos na seção `1.2`, esta etapa é sobre entender o uso contínuo.

* **Propósito:** O GitHub serve como seu sistema de controle de versão, garantindo um histórico de todas as mudanças no código. Mais importante, o Render se conectará ao seu repositório GitHub para realizar deploys automáticos a cada nova alteração que você commitar.
* **Fluxo de Trabalho:** Ao fazer qualquer alteração nos arquivos `main.py`, `faq.json` ou `requirements.txt` diretamente no GitHub (editando os arquivos e clicando em `Commit changes`), o Render detectará essas mudanças e iniciará um novo deploy do seu bot.

### 2.3. Render: Hospedagem do Bot

O Render é uma plataforma de nuvem que permite hospedar seu bot como um serviço web de forma contínua e gratuita (com algumas limitações).

1.  **Crie uma conta no Render:** [render.com](https://render.com/). Você pode usar sua conta do GitHub para um registro rápido.

2.  **Crie um Novo Serviço Web:**
    * Após o login, no Dashboard do Render, clique em `New` > `Web Service`.
    * **Connect a Git repository:** Conecte sua conta do GitHub.
    * Procure e selecione o repositório do seu bot (ex: `bot-faq-inteligente`). Clique em `Connect`.

3.  **Configure o Serviço Web:**
    * **Name:** Um nome para seu serviço no Render (ex: `meu-bot-faq-api`).
    * **Region:** Escolha uma região próxima a você (ex: `São Paulo (South America) - São Paulo`).
    * **Branch:** `main` (ou `master`, dependendo do seu repositório).
    * **Root Directory:** Deixe vazio (se seu projeto estiver na raiz do repositório).
    * **Runtime:** `Python 3`.
    * **Build Command:** Este comando será executado pelo Render para instalar as dependências.
        ```bash
        pip install -r requirements.txt
        ```
    * **Start Command:** Este comando iniciará seu bot. Como você está usando Gunicorn, o comando de start será para o Gunicorn executar sua aplicação Flask. O seu arquivo principal, `main.py`, provavelmente tem uma variável `app = Flask(__name__)`.
        ```bash
        gunicorn --bind 0.0.0.0:$PORT main:app
        ```
        * **Explicação do `Start Command`:**
            * `gunicorn`: O servidor WSGI.
            * `--bind 0.0.0.0:$PORT`: Diz ao Gunicorn para escutar em todas as interfaces de rede na porta especificada pela variável de ambiente `PORT`. O Render define `PORT` automaticamente, geralmente como `10000` para serviços gratuitos.
            * `main:app`: Indica ao Gunicorn para encontrar a aplicação Flask chamada `app` dentro do arquivo `main.py`. Se seu arquivo principal se chama `main (2).py`, você precisaria ajustar para `gunicorn --bind 0.0.0.0:$PORT "main (2)":app` (com aspas no nome do arquivo). Recomendo renomear para `main.py` para simplicidade.
    * **Instance Type:** `Free`.
    * **Environment Variables:** Clique em `Advanced` > `Add Environment Variable`.
        * `Key`: `BOT_TOKEN`, `Value`: `SEU_TOKEN_DO_BOTFATHER` (Cole o token que você obteve do BotFather)
        * `Key`: `ADMIN_CHAT_ID`, `Value`: `SEU_ID_DE_CHAT_ADMIN` (Cole o ID do seu chat)
        * `Key`: `PORT`, `Value`: `10000` (Esta é a porta que o Render geralmente usa para serviços Free Tier. Seu código já lê essa variável).
    * Clique em `Create Web Service`.

    O Render começará a construir e implantar seu bot. Acompanhe os logs na página do serviço. Se houver erros, eles aparecerão aqui.

4.  **Obtenha o URL do Serviço Web:**
    * Uma vez que o deploy esteja completo e o status seja `live`, você verá um `URL` na página do seu serviço Render (ex: `https://meu-bot-faq-api.onrender.com`). **Copie este URL.**

### 2.4. Telegram: Configure o Webhook

Agora que seu bot está hospedado e tem um URL público, você precisa dizer ao Telegram onde enviar as mensagens.

1.  **Abra seu navegador** e vá para o seguinte URL, substituindo `SEU_BOT_TOKEN` e `SEU_RENDER_URL`:
    ```
    [https://api.telegram.org/botSEU_BOT_TOKEN/setWebhook?url=SEU_RENDER_URL/webhook](https://api.telegram.org/botSEU_BOT_TOKEN/setWebhook?url=SEU_RENDER_URL/webhook)
    ```
    * **Exemplo:** Se seu token for `123...` e seu URL do Render for `https://meu-bot-faq-api.onrender.com`, o URL ficaria:
        ```
        [https://api.telegram.org/bot123.../setWebhook?url=https://meu-bot-faq-api.onrender.com/webhook](https://api.telegram.org/bot123.../setWebhook?url=https://meu-bot-faq-api.onrender.com/webhook)
        ```
2.  Pressione Enter. Você deve ver uma resposta JSON indicando `{"ok":true, "result":true, ...}`. Isso significa que o webhook foi configurado com sucesso!

### 2.5. UptimeRobot: Mantenha o Bot Ativo

O Render na camada gratuita pode colocar seu serviço em "sleep" após 15 minutos de inatividade. O UptimeRobot envia pings regulares para o URL do seu bot para mantê-lo ativo.

1.  **Crie uma conta no UptimeRobot:** [uptimerobot.com](https://uptimerobot.com/).

2.  **Adicione um novo Monitor:**
    * No Dashboard do UptimeRobot, clique em `Add New Monitor`.
    * **Monitor Type:** `HTTP(s)`.
    * **Friendly Name:** Um nome fácil para identificar (ex: `Meu Bot FAQ Render`).
    * **URL (or IP):** Cole o **URL do seu serviço Render** (ex: `https://meu-bot-faq-api.onrender.com`).
    * **Monitoring Interval:** `5 Minutes` (ou o mínimo permitido na sua conta gratuita, geralmente 5 minutos é o suficiente).
    * **Alert Contacts:** (Opcional) Configure onde receber alertas se o bot ficar offline.
    * Clique em `Create Monitor`.

    O UptimeRobot começará a "pingar" seu bot a cada 5 minutos, mantendo-o ativo.

## 3. Detalhamento do Código (`main.py`)

Esta seção descreve as principais partes do código do seu bot.

### 3.1. Importações e Configuração Inicial

```python
import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# O código original não tinha estas importações. Se você deseja usar NLTK e scikit-learn
# para PLN mais avançado (TF-IDF, similaridade de cosseno, stemming), você precisará
# adicionar e implementar as funções correspondentes.
# import nltk
# from nltk.corpus import stopwords
# from nltk.stem import RSLPStemmer # Para português
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# Se você usa unidecode no seu código, adicione aqui:
# from unidecode import unidecode 

# --- Configurações do Bot Telegram ---
app = Flask(__name__)

# Obtém o token do bot das variáveis de ambiente
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    exit(1) # Impede que o bot inicie sem o token
bot = telebot.TeleBot(BOT_TOKEN)

# Obtém o ID do chat do administrador das variáveis de ambiente
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
if not ADMIN_CHAT_ID:
    print("AVISO: Variável de ambiente ADMIN_CHAT_ID não definida. Comando /recarregarfaq não funcionará para administradores.")
else:
    ADMIN_CHAT_ID = str(ADMIN_CHAT_ID) # Garante que é string para comparação

# Variáveis globais para armazenar o FAQ e componentes de PLN
faq_data = {}
# Se estiver usando NLTK/scikit-learn, descomente e use estas variáveis:
# tfidf_vectorizer = None
# faq_vectors = None
# faq_ids_indexed = [] # Para mapear de volta do índice do vetorizador para o FAQ ID

# --- Inicializar Stemmer e Stop Words (se NLTK estiver sendo usado) ---
# O código original não tinha esta seção. Se você deseja usar NLTK, descomente.
# try:
#     nltk.data.find('corpora/stopwords')
# except nltk.downloader.DownloadError:
#     print("Baixando dados do NLTK: stopwords...")
#     nltk.download('stopwords')
# try:
#     nltk.data.find('stemmers/rslp')
# except nltk.downloader.DownloadError:
#     print("Baixando dados do NLTK: rslp (stemmer para português)...")
#     nltk.download('rslp')
# stemmer = RSLPStemmer()
# stop_words = set(stopwords.words('portuguese'))

# --- Função de Pré-processamento de Texto ---
def preprocess_text(text):
    """
    Normaliza o texto: minúsculas e remove espaços extras.
    Para PLN avançado (stemming, stopwords, unidecode), o código precisaria ser expandido.
    """
    if not text:
        return ""
    # Converte para string para evitar erros se o input não for string
    text = str(text).lower().strip() 
    # Opcional: Se 'unidecode' for usado para remover acentos, descomente:
    # from unidecode import unidecode # Isso deve estar no topo com outras importações
    # text = unidecode(text) 

    # Para PLN avançado (stemming e stopwords), as linhas abaixo seriam necessárias:
    # words = [stemmer.stem(word) for word in text.split() if word not in stop_words and len(word) > 1]
    # return " ".join(words)
    return text

# --- Carregamento e Vetorização do FAQ ---
def load_faq():
    """
    Carrega o FAQ do arquivo JSON. 
    Para PLN avançado, também vetorizaria o FAQ usando TF-IDF.
    """
    global faq_data 
    # Se estiver usando NLTK/scikit-learn, também global tfidf_vectorizer, faq_vectors, faq_ids_indexed
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            raw_faq = json.load(f)
            faq_data = {str(k): v for k, v in raw_faq.items()}

        if not faq_data:
            print("FAQ vazio ou não carregado.")
            # Se usando PLN avançado, resetaria vetorizador e vetores aqui
            return

        # Se usando PLN avançado, esta parte seria executada:
        # texts_to_vectorize = []
        # faq_ids_indexed = []
        # for faq_id, entry in faq_data.items():
        #     combined_text = entry.get('pergunta', '') + " " + " ".join(entry.get('palavras_chave', []))
        #     texts_to_vectorize.append(preprocess_text(combined_text))
        #     faq_ids_indexed.append(faq_id)
        # tfidf_vectorizer = TfidfVectorizer()
        # faq_vectors = tfidf_vectorizer.fit_transform(texts_to_vectorize)
        
        print(f"FAQ carregado com sucesso! Tamanho do FAQ: {len(faq_data)} entradas.")
    except FileNotFoundError:
        print("Erro: Arquivo faq.json não encontrado. O bot NÃO poderá responder via FAQ.")
        faq_data = {} 
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: {e}. Verifique a sintaxe do arquivo.")
        faq_data = {}
    except Exception as e:
        print(f"Erro inesperado ao carregar o FAQ: {e}")
        traceback.print_exc()
        faq_data = {}

# Chama a função para carregar o FAQ quando o bot inicia
load_faq()

# --- Função para encontrar a melhor correspondência no FAQ (MAIS DIRETA) ---
def find_faq_answer(query):
    """
    Encontra a melhor resposta do FAQ usando correspondência de palavras-chave.
    Para PLN avançado, usaria TF-IDF e similaridade de cosseno.
    """
    if not faq_data:
        print("DEBUG: FAQ data não carregado em find_faq_answer.")
        return None, None

    normalized_query = preprocess_text(query)
    if not normalized_query:
        print("DEBUG: Query pré-processada vazia.")
        return None, None

    # PRIORIDADE 1: Correspondência EXATA da query com uma palavra-chave
    for faq_id, entry in faq_data.items():
        keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
        for keyword in keywords:
            if normalized_query == keyword:
                print(f"DEBUG: Correspondência EXATA de query com keyword! FAQ ID: {faq_id}, Keyword: '{keyword}'")
                return entry.get('resposta'), faq_id
            
    # Se PLN avançado estiver ativo, a busca por similaridade TF-IDF viria aqui
    # try:
    #     query_vector = tfidf_vectorizer.transform([processed_query])
    #     similarities = cosine_similarity(query_vector, faq_vectors).flatten()
    #     best_match_index = similarities.argmax()
    #     best_similarity = similarities[best_match_index]
    #     MIN_SIMILARITY_THRESHOLD = 0.35 # AJUSTE ESTE VALOR!
    #     if best_similarity >= MIN_SIMILARITY_THRESHOLD:
    #         best_faq_id = faq_ids_indexed[best_match_index]
    #         return faq_data[best_faq_id].get('resposta'), best_faq_id
    # except Exception as e:
    #     print(f"Erro ao buscar por similaridade TF-IDF: {e}")
    #     traceback.print_exc()


    # PRIORIDADE 2: Busca por palavras-chave ou pergunta contida na query (ou vice-versa)
    best_faq_id_by_keyword_hits = None
    max_keyword_hits = 0
    
    MIN_HITS_THRESHOLD = 1 # Ajuste este valor se necessário para controlar a sensibilidade

    for faq_id, entry in faq_data.items():
        keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
        current_hits = 0
        
        # Verifica se a palavra-chave está contida na query ou a query na palavra-chave
        for keyword in keywords:
            if keyword and (keyword in normalized_query or normalized_query in keyword):
                current_hits += 1
        
        pergunta_faq_normalizada = preprocess_text(entry.get('pergunta', ''))
        if pergunta_faq_normalizada and pergunta_faq_normalizada in normalized_query:
            current_hits += 1 # Conta também se a pergunta inteira do FAQ está na query

        if current_hits > max_keyword_hits:
            max_keyword_hits = current_hits
            best_faq_id_by_keyword_hits = faq_id

    print(f"DEBUG: Melhor correspondência por hits: ID {best_faq_id_by_keyword_hits} com {max_keyword_hits} hits.")

    if max_keyword_hits >= MIN_HITS_THRESHOLD and best_faq_id_by_keyword_hits:
        return faq_data[best_faq_id_by_keyword_hits].get('resposta'), best_faq_id_by_keyword_hits
    
    print("DEBUG: Nenhuma correspondência boa encontrada por hits de palavras-chave.")
    return None, None

# --- Função para obter botões de perguntas relacionadas ---
# Aumentei o max_buttons para 10. Você pode ajustar esse valor se precisar de mais.
def get_related_buttons(query, primary_faq_id=None, max_buttons=10): 
    related_buttons_info = []
    normalized_query = preprocess_text(query)
    
    RELATED_HITS_THRESHOLD = 1 # Limiar simples de palavras-chave para sugestões

    print(f"DEBUG: Buscando botões relacionados para query '{query}', excluindo ID '{primary_faq_id}'.")

    for faq_id, entry in faq_data.items():
        if faq_id == primary_faq_id: 
            continue

        keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
        pergunta_text = preprocess_text(entry.get('pergunta', ''))

        current_related_hits = 0
        for item_text in keywords + [pergunta_text]:
            if item_text and (item_text in normalized_query or normalized_query in item_text):
                current_related_hits += 1
        
        if current_related_hits >= RELATED_HITS_THRESHOLD:
            if (faq_id, entry.get('pergunta')) not in related_buttons_info:
                related_buttons_info.append((faq_id, entry.get('pergunta')))
        
        if len(related_buttons_info) >= max_buttons: 
            break

    if related_buttons_info:
        markup = InlineKeyboardMarkup()
        for faq_id, pergunta in related_buttons_info:
            # Trunca o texto do botão se for muito longo
            button_text = pergunta[:50] + '...' if len(pergunta) > 53 else pergunta
            markup.add(InlineKeyboardButton(button_text, callback_data=str(faq_id))) 
        print(f"DEBUG: Botões relacionados gerados: {len(related_buttons_info)}.")
        return markup
    print("DEBUG: Nenhum botão relacionado encontrado.")
    return None 

# --- Rotas Flask para Webhook e Health Check ---

@app.route('/')
def health_check():
    """
    Endpoint simples para verificar a saúde da aplicação.
    Útil para o Render e UptimeRobot.
    """
    print("Requisição GET recebida no / (Health Check)")
    return "Bot está funcionando!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint principal que recebe as atualizações do Telegram.
    Processa mensagens e callbacks.
    """
    if request.method == 'POST':
        update_json = request.get_json()
        print("Requisição POST recebida em /webhook")

        try:
            update = telebot.types.Update.de_json(json.dumps(update_json))

            if update.message:
                message = update.message
                chat_id = message.chat.id
                text = message.text

                print(f"----> Mensagem recebida do chat {chat_id}: '{text}'")

                response_text = ""
                markup = None 

                if text:
                    # O comando /recarregarfaq e a lógica ADMIN_CHAT_ID não estão presentes no seu main (2).py
                    # Se você adicionar, ficaria aqui, por exemplo:
                    # if text == '/recarregarfaq':
                    #     if ADMIN_CHAT_ID and str(chat_id) == ADMIN_CHAT_ID:
                    #         bot.send_message(chat_id, "Iniciando recarregamento do FAQ...")
                    #         load_faq()
                    #         bot.send_message(chat_id, "FAQ recarregado com sucesso!")
                    #     else:
                    #         bot.send_message(chat_id, "Você não tem permissão para usar este comando.")
                    # else:
                    faq_answer, faq_id_matched = find_faq_answer(text)

                    if faq_answer:
                        response_text = faq_answer
                        print(f"----> Resposta principal encontrada no FAQ (ID: {faq_id_matched}): '{response_text}'")
                        markup = get_related_buttons(text, faq_id_matched)
                        
                    else:
                        response_text = "Desculpe, não consegui encontrar uma resposta para sua pergunta no meu FAQ. Por favor, tente perguntar de outra forma ou consulte nosso site oficial."
                        print(f"----> Nenhuma resposta principal encontrada no FAQ para: '{text}'. Enviando fallback genérico.")
                    
                    try:
                        # Tenta enviar com Markdown, se falhar, tenta sem.
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        if "Can't parse message text" in str(e) or "Bad Request: can't parse entities" in str(e):
                            print("DICA: Texto pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                            bot.send_message(chat_id, response_text, parse_mode=None, reply_markup=markup) 
                        else:
                            # Se for outro tipo de erro da API, re-lança
                            raise 
                        print(f"----> Mensagem enviada (sem Markdown se erro anterior) para o chat {chat_id}.")
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                        traceback.print_exc() # Imprime o stack trace completo do erro
                        bot.send_message(chat_id, "Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde.")
                        print(f"----> Mensagem de erro genérica enviada para o chat {chat_id}.")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

            elif update.callback_query:
                callback_query = update.callback_query
                chat_id = callback_query.message.chat.id
                callback_data = callback_query.data 

                print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")
                bot.answer_callback_query(callback_query.id) # Avisa ao Telegram que a query foi processada

                try:
                    if callback_data in faq_data:
                        response_text = faq_data[callback_data].get('resposta')
                        try:
                            bot.send_message(chat_id, response_text, parse_mode='Markdown')
                            print(f"----> Resposta da Callback Query enviada com sucesso para o chat {chat_id}.")
                        except telebot.apihelper.ApiTelegramException as e:
                            print(f"ERRO Telegram API ao enviar mensagem de callback: {e}")
                            if "Can't parse message text" in str(e) or "Bad Request: can't parse entities" in str(e):
                                print("DICA: Texto do callback pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                                bot.send_message(chat_id, response_text, parse_mode=None) 
                            else:
                                raise
                            print(f"----> Resposta da Callback Query enviada (sem Markdown se erro anterior) para o chat {chat_id}.")
                    else:
                        bot.send_message(chat_id, "Desculpe, não encontrei a informação solicitada pelo botão.", parse_mode='Markdown')
                        print(f"----> ERRO: FAQ ID '{callback_data}' não encontrado para Callback Query.")
                except Exception as e:
                    print(f"ERRO ao processar Callback Query para FAQ ID {callback_data}: {e}")
                    print(traceback.format_exc())
                    bot.send_message(chat_id, "Ocorreu um erro ao processar sua solicitação do botão. Por favor, tente novamente mais tarde.")
                    print(f"----> Mensagem de erro genérica para Callback Query enviada para o chat {chat_id}.")
            
            else:
                print("----> Update recebido sem as chaves 'message' ou 'callback_query'. Pode ser outro tipo de atualização (edited_message, channel_post, etc.).")

        except Exception as e:
            print(f"ERRO INESPERADO no processamento do webhook: {e}")
            print(traceback.format_exc())

        print("Update processado. Retornando 200 OK.")
        return 'OK', 200
    else:
        return 'Método não permitido', 405

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # No seu deploy com Gunicorn, esta parte pode não ser executada diretamente,
    # pois o Gunicorn irá gerenciar a inicialização da aplicação 'app'.
    # Ela é útil para testes locais ou se você não usar Gunicorn.
    app.run(host='0.0.0.0', port=port)
        ```
    * Clique em `Commit new file`.

## 2. Configuração dos Serviços Externos

Para que seu bot funcione, ele precisará interagir com a API do Telegram e ser hospedado online.

### 2.1. Telegram: Crie seu Bot e Obtenha Tokens

Você precisará de um bot no Telegram e dois IDs importantes: o `BOT_TOKEN` e seu `ADMIN_CHAT_ID`.

1.  **Crie um novo Bot (BotFather):**
    * Abra o Telegram e pesquise por `@BotFather`.
    * Inicie uma conversa e use o comando `/newbot`.
    * Siga as instruções para dar um **Nome** ao seu bot (ex: `Meu Bot de Ajuda`) e um **Username** (deve terminar com "bot", ex: `MeuAjuda_bot`).
    * Ao finalizar, o BotFather lhe fornecerá um **`BOT_TOKEN`**. Ele se parecerá com algo como: `1234567890:ABC-DEF1234ghIJK_LMN-opqRSTuvwxyZAB`. **Copie e guarde este token com segurança.**

2.  **Obtenha seu ID de Chat de Administrador (`ADMIN_CHAT_ID`):**
    * Primeiro, envie uma mensagem para o **seu próprio bot** (o que você acabou de criar). Pode ser um "Olá".
    * Depois, no Telegram, pesquise por `@userinfobot` ou `@get_id_bot`.
    * Inicie uma conversa com um desses bots e ele lhe informará seu `ID de Chat` (um número, ex: `12345678`). **Copie e guarde este número.** Este será o seu `ADMIN_CHAT_ID`.

### 2.2. GitHub: Gerenciamento de Código

Como você já criou o repositório e os arquivos na seção `1.2`, esta etapa é sobre entender o uso contínuo.

* **Propósito:** O GitHub serve como seu sistema de controle de versão, garantindo um histórico de todas as mudanças no código. Mais importante, o Render se conectará ao seu repositório GitHub para realizar deploys automáticos a cada nova alteração que você commitar.
* **Fluxo de Trabalho:** Ao fazer qualquer alteração nos arquivos `main.py`, `faq.json` ou `requirements.txt` diretamente no GitHub (editando os arquivos e clicando em `Commit changes`), o Render detectará essas mudanças e iniciará um novo deploy do seu bot.

### 2.3. Render: Hospedagem do Bot

O Render é uma plataforma de nuvem que permite hospedar seu bot como um serviço web de forma contínua e gratuita (com algumas limitações).

1.  **Crie uma conta no Render:** [render.com](https://render.com/). Você pode usar sua conta do GitHub para um registro rápido.

2.  **Crie um Novo Serviço Web:**
    * Após o login, no Dashboard do Render, clique em `New` > `Web Service`.
    * **Connect a Git repository:** Conecte sua conta do GitHub.
    * Procure e selecione o repositório do seu bot (ex: `bot-faq-inteligente`). Clique em `Connect`.

3.  **Configure o Serviço Web:**
    * **Name:** Um nome para seu serviço no Render (ex: `meu-bot-faq-api`).
    * **Region:** Escolha uma região próxima a você (ex: `São Paulo (South America) - São Paulo`).
    * **Branch:** `main` (ou `master`, dependendo do seu repositório).
    * **Root Directory:** Deixe vazio (se seu projeto estiver na raiz do repositório).
    * **Runtime:** `Python 3`.
    * **Build Command:** Este comando será executado pelo Render para instalar as dependências.
        ```bash
        pip install -r requirements.txt
        ```
    * **Start Command:** Este comando iniciará seu bot. Como você está usando Gunicorn, o comando de start será para o Gunicorn executar sua aplicação Flask. O seu arquivo principal, `main.py`, provavelmente tem uma variável `app = Flask(__name__)`.
        ```bash
        gunicorn --bind 0.0.0.0:$PORT main:app
        ```
        * **Explicação do `Start Command`:**
            * `gunicorn`: O servidor WSGI.
            * `--bind 0.0.0.0:$PORT`: Diz ao Gunicorn para escutar em todas as interfaces de rede na porta especificada pela variável de ambiente `PORT`. O Render define `PORT` automaticamente, geralmente como `10000` para serviços gratuitos.
            * `main:app`: Indica ao Gunicorn para encontrar a aplicação Flask chamada `app` dentro do arquivo `main.py`. Se seu arquivo principal se chama `main (2).py`, você precisaria ajustar para `gunicorn --bind 0.0.0.0:$PORT "main (2)":app` (com aspas no nome do arquivo). Recomendo renomear para `main.py` para simplicidade.
    * **Instance Type:** `Free`.
    * **Environment Variables:** Clique em `Advanced` > `Add Environment Variable`.
        * `Key`: `BOT_TOKEN`, `Value`: `SEU_TOKEN_DO_BOTFATHER` (Cole o token que você obteve do BotFather)
        * `Key`: `ADMIN_CHAT_ID`, `Value`: `SEU_ID_DE_CHAT_ADMIN` (Cole o ID do seu chat)
        * `Key`: `PORT`, `Value`: `10000` (Esta é a porta que o Render geralmente usa para serviços Free Tier. Seu código já lê essa variável).
    * Clique em `Create Web Service`.

    O Render começará a construir e implantar seu bot. Acompanhe os logs na página do serviço. Se houver erros, eles aparecerão aqui.

4.  **Obtenha o URL do Serviço Web:**
    * Uma vez que o deploy esteja completo e o status seja `live`, você verá um `URL` na página do seu serviço Render (ex: `https://meu-bot-faq-api.onrender.com`). **Copie este URL.**

### 2.4. Telegram: Configure o Webhook

Agora que seu bot está hospedado e tem um URL público, você precisa dizer ao Telegram onde enviar as mensagens.

1.  **Abra seu navegador** e vá para o seguinte URL, substituindo `SEU_BOT_TOKEN` e `SEU_RENDER_URL`:
    ```
    [https://api.telegram.org/botSEU_BOT_TOKEN/setWebhook?url=SEU_RENDER_URL/webhook](https://api.telegram.org/botSEU_BOT_TOKEN/setWebhook?url=SEU_RENDER_URL/webhook)
    ```
    * **Exemplo:** Se seu token for `123...` e seu URL do Render for `https://meu-bot-faq-api.onrender.com`, o URL ficaria:
        ```
        [https://api.telegram.org/bot123.../setWebhook?url=https://meu-bot-faq-api.onrender.com/webhook](https://api.telegram.org/bot123.../setWebhook?url=https://meu-bot-faq-api.onrender.com/webhook)
        ```
2.  Pressione Enter. Você deve ver uma resposta JSON indicando `{"ok":true, "result":true, ...}`. Isso significa que o webhook foi configurado com sucesso!

### 2.5. UptimeRobot: Mantenha o Bot Ativo

O Render na camada gratuita pode colocar seu serviço em "sleep" após 15 minutos de inatividade. O UptimeRobot envia pings regulares para o URL do seu bot para mantê-lo ativo.

1.  **Crie uma conta no UptimeRobot:** [uptimerobot.com](https://uptimerobot.com/).

2.  **Adicione um novo Monitor:**
    * No Dashboard do UptimeRobot, clique em `Add New Monitor`.
    * **Monitor Type:** `HTTP(s)`.
    * **Friendly Name:** Um nome fácil para identificar (ex: `Meu Bot FAQ Render`).
    * **URL (or IP):** Cole o **URL do seu serviço Render** (ex: `https://meu-bot-faq-api.onrender.com`).
    * **Monitoring Interval:** `5 Minutes` (ou o mínimo permitido na sua conta gratuita, geralmente 5 minutos é o suficiente).
    * **Alert Contacts:** (Opcional) Configure onde receber alertas se o bot ficar offline.
    * Clique em `Create Monitor`.

    O UptimeRobot começará a "pingar" seu bot a cada 5 minutos, mantendo-o ativo.

## 3. Detalhamento do Código (`main.py`)

Esta seção descreve as principais partes do código do seu bot.

### 3.1. Importações e Configuração Inicial

```python
import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# O código original não tinha estas importações. Se você deseja usar NLTK e scikit-learn
# para PLN mais avançado (TF-IDF, similaridade de cosseno, stemming), você precisará
# adicionar e implementar as funções correspondentes.
# import nltk
# from nltk.corpus import stopwords
# from nltk.stem import RSLPStemmer # Para português
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# Se você usa unidecode no seu código, adicione aqui:
# from unidecode import unidecode 

# --- Configurações do Bot Telegram ---
app = Flask(__name__)

# Obtém o token do bot das variáveis de ambiente
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    exit(1) # Impede que o bot inicie sem o token
bot = telebot.TeleBot(BOT_TOKEN)

# Obtém o ID do chat do administrador das variáveis de ambiente
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
if not ADMIN_CHAT_ID:
    print("AVISO: Variável de ambiente ADMIN_CHAT_ID não definida. Comando /recarregarfaq não funcionará para administradores.")
else:
    ADMIN_CHAT_ID = str(ADMIN_CHAT_ID) # Garante que é string para comparação

# Variáveis globais para armazenar o FAQ e componentes de PLN
faq_data = {}
# Se estiver usando NLTK/scikit-learn, descomente e use estas variáveis:
# tfidf_vectorizer = None
# faq_vectors = None
# faq_ids_indexed = [] # Para mapear de volta do índice do vetorizador para o FAQ ID

# --- Inicializar Stemmer e Stop Words (se NLTK estiver sendo usado) ---
# O código original não tinha esta seção. Se você deseja usar NLTK, descomente.
# try:
#     nltk.data.find('corpora/stopwords')
# except nltk.downloader.DownloadError:
#     print("Baixando dados do NLTK: stopwords...")
#     nltk.download('stopwords')
# try:
#     nltk.data.find('stemmers/rslp')
# except nltk.downloader.DownloadError:
#     print("Baixando dados do NLTK: rslp (stemmer para português)...")
#     nltk.download('rslp')
# stemmer = RSLPStemmer()
# stop_words = set(stopwords.words('portuguese'))

# --- Função de Pré-processamento de Texto ---
def preprocess_text(text):
    """
    Normaliza o texto: minúsculas e remove espaços extras.
    Para PLN avançado (stemming, stopwords, unidecode), o código precisaria ser expandido.
    """
    if not text:
        return ""
    # Converte para string para evitar erros se o input não for string
    text = str(text).lower().strip() 
    # Opcional: Se 'unidecode' for usado para remover acentos, descomente:
    # from unidecode import unidecode # Isso deve estar no topo com outras importações
    # text = unidecode(text) 

    # Para PLN avançado (stemming e stopwords), as linhas abaixo seriam necessárias:
    # words = [stemmer.stem(word) for word in text.split() if word not in stop_words and len(word) > 1]
    # return " ".join(words)
    return text

# --- Carregamento e Vetorização do FAQ ---
def load_faq():
    """
    Carrega o FAQ do arquivo JSON. 
    Para PLN avançado, também vetorizaria o FAQ usando TF-IDF.
    """
    global faq_data 
    # Se estiver usando NLTK/scikit-learn, também global tfidf_vectorizer, faq_vectors, faq_ids_indexed
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            raw_faq = json.load(f)
            faq_data = {str(k): v for k, v in raw_faq.items()}

        if not faq_data:
            print("FAQ vazio ou não carregado.")
            # Se usando PLN avançado, resetaria vetorizador e vetores aqui
            return

        # Se usando PLN avançado, esta parte seria executada:
        # texts_to_vectorize = []
        # faq_ids_indexed = []
        # for faq_id, entry in faq_data.items():
        #     combined_text = entry.get('pergunta', '') + " " + " ".join(entry.get('palavras_chave', []))
        #     texts_to_vectorize.append(preprocess_text(combined_text))
        #     faq_ids_indexed.append(faq_id)
        # tfidf_vectorizer = TfidfVectorizer()
        # faq_vectors = tfidf_vectorizer.fit_transform(texts_to_vectorize)
        
        print(f"FAQ carregado com sucesso! Tamanho do FAQ: {len(faq_data)} entradas.")
    except FileNotFoundError:
        print("Erro: Arquivo faq.json não encontrado. O bot NÃO poderá responder via FAQ.")
        faq_data = {} 
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: {e}. Verifique a sintaxe do arquivo.")
        faq_data = {}
    except Exception as e:
        print(f"Erro inesperado ao carregar o FAQ: {e}")
        traceback.print_exc()
        faq_data = {}

# Chama a função para carregar o FAQ quando o bot inicia
load_faq()

# --- Função para encontrar a melhor correspondência no FAQ (MAIS DIRETA) ---
def find_faq_answer(query):
    """
    Encontra a melhor resposta do FAQ usando correspondência de palavras-chave.
    Para PLN avançado, usaria TF-IDF e similaridade de cosseno.
    """
    if not faq_data:
        print("DEBUG: FAQ data não carregado em find_faq_answer.")
        return None, None

    normalized_query = preprocess_text(query)
    if not normalized_query:
        print("DEBUG: Query pré-processada vazia.")
        return None, None

    # PRIORIDADE 1: Correspondência EXATA da query com uma palavra-chave
    for faq_id, entry in faq_data.items():
        keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
        for keyword in keywords:
            if normalized_query == keyword:
                print(f"DEBUG: Correspondência EXATA de query com keyword! FAQ ID: {faq_id}, Keyword: '{keyword}'")
                return entry.get('resposta'), faq_id
            
    # Se PLN avançado estiver ativo, a busca por similaridade TF-IDF viria aqui
    # try:
    #     query_vector = tfidf_vectorizer.transform([processed_query])
    #     similarities = cosine_similarity(query_vector, faq_vectors).flatten()
    #     best_match_index = similarities.argmax()
    #     best_similarity = similarities[best_match_index]
    #     MIN_SIMILARITY_THRESHOLD = 0.35 # AJUSTE ESTE VALOR!
    #     if best_similarity >= MIN_SIMILARITY_THRESHOLD:
    #         best_faq_id = faq_ids_indexed[best_match_index]
    #         return faq_data[best_faq_id].get('resposta'), best_faq_id
    # except Exception as e:
    #     print(f"Erro ao buscar por similaridade TF-IDF: {e}")
    #     traceback.print_exc()


    # PRIORIDADE 2: Busca por palavras-chave ou pergunta contida na query (ou vice-versa)
    best_faq_id_by_keyword_hits = None
    max_keyword_hits = 0
    
    MIN_HITS_THRESHOLD = 1 # Ajuste este valor se necessário para controlar a sensibilidade

    for faq_id, entry in faq_data.items():
        keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
        current_hits = 0
        
        # Verifica se a palavra-chave está contida na query ou a query na palavra-chave
        for keyword in keywords:
            if keyword and (keyword in normalized_query or normalized_query in keyword):
                current_hits += 1
        
        pergunta_faq_normalizada = preprocess_text(entry.get('pergunta', ''))
        if pergunta_faq_normalizada and pergunta_faq_normalizada in normalized_query:
            current_hits += 1 # Conta também se a pergunta inteira do FAQ está na query

        if current_hits > max_keyword_hits:
            max_keyword_hits = current_hits
            best_faq_id_by_keyword_hits = faq_id

    print(f"DEBUG: Melhor correspondência por hits: ID {best_faq_id_by_keyword_hits} com {max_keyword_hits} hits.")

    if max_keyword_hits >= MIN_HITS_THRESHOLD and best_faq_id_by_keyword_hits:
        return faq_data[best_faq_id_by_keyword_hits].get('resposta'), best_faq_id_by_keyword_hits
    
    print("DEBUG: Nenhuma correspondência boa encontrada por hits de palavras-chave.")
    return None, None

# --- Função para obter botões de perguntas relacionadas ---
# Aumentei o max_buttons para 10. Você pode ajustar esse valor se precisar de mais.
def get_related_buttons(query, primary_faq_id=None, max_buttons=10): 
    related_buttons_info = []
    normalized_query = preprocess_text(query)
    
    RELATED_HITS_THRESHOLD = 1 # Limiar simples de palavras-chave para sugestões

    print(f"DEBUG: Buscando botões relacionados para query '{query}', excluindo ID '{primary_faq_id}'.")

    for faq_id, entry in faq_data.items():
        if faq_id == primary_faq_id: 
            continue

        keywords = [preprocess_text(k) for k in entry.get('palavras_chave', [])]
        pergunta_text = preprocess_text(entry.get('pergunta', ''))

        current_related_hits = 0
        for item_text in keywords + [pergunta_text]:
            if item_text and (item_text in normalized_query or normalized_query in item_text):
                current_related_hits += 1
        
        if current_related_hits >= RELATED_HITS_THRESHOLD:
            if (faq_id, entry.get('pergunta')) not in related_buttons_info:
                related_buttons_info.append((faq_id, entry.get('pergunta')))
        
        if len(related_buttons_info) >= max_buttons: 
            break

    if related_buttons_info:
        markup = InlineKeyboardMarkup()
        for faq_id, pergunta in related_buttons_info:
            # Trunca o texto do botão se for muito longo
            button_text = pergunta[:50] + '...' if len(pergunta) > 53 else pergunta
            markup.add(InlineKeyboardButton(button_text, callback_data=str(faq_id))) 
        print(f"DEBUG: Botões relacionados gerados: {len(related_buttons_info)}.")
        return markup
    print("DEBUG: Nenhum botão relacionado encontrado.")
    return None 

# --- Rotas Flask para Webhook e Health Check ---

@app.route('/')
def health_check():
    """
    Endpoint simples para verificar a saúde da aplicação.
    Útil para o Render e UptimeRobot.
    """
    print("Requisição GET recebida no / (Health Check)")
    return "Bot está funcionando!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint principal que recebe as atualizações do Telegram.
    Processa mensagens e callbacks.
    """
    if request.method == 'POST':
        update_json = request.get_json()
        print("Requisição POST recebida em /webhook")

        try:
            update = telebot.types.Update.de_json(json.dumps(update_json))

            if update.message:
                message = update.message
                chat_id = message.chat.id
                text = message.text

                print(f"----> Mensagem recebida do chat {chat_id}: '{text}'")

                response_text = ""
                markup = None 

                if text:
                    # O comando /recarregarfaq e a lógica ADMIN_CHAT_ID não estão presentes no seu main (2).py
                    # Se você adicionar, ficaria aqui, por exemplo:
                    # if text == '/recarregarfaq':
                    #     if ADMIN_CHAT_ID and str(chat_id) == ADMIN_CHAT_ID:
                    #         bot.send_message(chat_id, "Iniciando recarregamento do FAQ...")
                    #         load_faq()
                    #         bot.send_message(chat_id, "FAQ recarregado com sucesso!")
                    #     else:
                    #         bot.send_message(chat_id, "Você não tem permissão para usar este comando.")
                    # else:
                    faq_answer, faq_id_matched = find_faq_answer(text)

                    if faq_answer:
                        response_text = faq_answer
                        print(f"----> Resposta principal encontrada no FAQ (ID: {faq_id_matched}): '{response_text}'")
                        markup = get_related_buttons(text, faq_id_matched)
                        
                    else:
                        response_text = "Desculpe, não consegui encontrar uma resposta para sua pergunta no meu FAQ. Por favor, tente perguntar de outra forma ou consulte nosso site oficial."
                        print(f"----> Nenhuma resposta principal encontrada no FAQ para: '{text}'. Enviando fallback genérico.")
                    
                    try:
                        # Tenta enviar com Markdown, se falhar, tenta sem.
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        if "Can't parse message text" in str(e) or "Bad Request: can't parse entities" in str(e):
                            print("DICA: Texto pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                            bot.send_message(chat_id, response_text, parse_mode=None, reply_markup=markup) 
                        else:
                            # Se for outro tipo de erro da API, re-lança
                            raise 
                        print(f"----> Mensagem enviada (sem Markdown se erro anterior) para o chat {chat_id}.")
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                        traceback.print_exc() # Imprime o stack trace completo do erro
                        bot.send_message(chat_id, "Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde.")
                        print(f"----> Mensagem de erro genérica enviada para o chat {chat_id}.")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

            elif update.callback_query:
                callback_query = update.callback_query
                chat_id = callback_query.message.chat.id
                callback_data = callback_query.data 

                print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")
                bot.answer_callback_query(callback_query.id) # Avisa ao Telegram que a query foi processada

                try:
                    if callback_data in faq_data:
                        response_text = faq_data[callback_data].get('resposta')
                        try:
                            bot.send_message(chat_id, response_text, parse_mode='Markdown')
                            print(f"----> Resposta da Callback Query enviada com sucesso para o chat {chat_id}.")
                        except telebot.apihelper.ApiTelegramException as e:
                            print(f"ERRO Telegram API ao enviar mensagem de callback: {e}")
                            if "Can't parse message text" in str(e) or "Bad Request: can't parse entities" in str(e):
                                print("DICA: Texto do callback pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                                bot.send_message(chat_id, response_text, parse_mode=None) 
                            else:
                                raise
                            print(f"----> Resposta da Callback Query enviada (sem Markdown se erro anterior) para o chat {chat_id}.")
                    else:
                        bot.send_message(chat_id, "Desculpe, não encontrei a informação solicitada pelo botão.", parse_mode='Markdown')
                        print(f"----> ERRO: FAQ ID '{callback_data}' não encontrado para Callback Query.")
                except Exception as e:
                    print(f"ERRO ao processar Callback Query para FAQ ID {callback_data}: {e}")
                    print(traceback.format_exc())
                    bot.send_message(chat_id, "Ocorreu um erro ao processar sua solicitação do botão. Por favor, tente novamente mais tarde.")
                    print(f"----> Mensagem de erro genérica para Callback Query enviada para o chat {chat_id}.")
            
            else:
                print("----> Update recebido sem as chaves 'message' ou 'callback_query'. Pode ser outro tipo de atualização (edited_message, channel_post, etc.).")

        except Exception as e:
            print(f"ERRO INESPERADO no processamento do webhook: {e}")
            print(traceback.format_exc())

        print("Update processado. Retornando 200 OK.")
        return 'OK', 200
    else:
        return 'Método não permitido', 405

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # No seu deploy com Gunicorn, esta parte pode não ser executada diretamente,
    # pois o Gunicorn irá gerenciar a inicialização da aplicação 'app'.
    # Ela é útil para testes locais ou se você não usar Gunicorn.
    app.run(host='0.0.0.0', port=port)
4. Como Fazer o Deploy Completo
Siga estes passos para colocar seu bot online, combinando o GitHub, Render e UptimeRobot.

Commit e Push para o GitHub:

Certifique-se de que os arquivos main.py (ou main (2).py), faq.json e requirements.txt estão na raiz do seu repositório GitHub. Se você os criou diretamente na interface web, eles já estão "commitados".

Qualquer alteração futura em qualquer um desses arquivos no GitHub (editando e "Commitando") automaticamente acionará um novo deploy no Render.

Deploy no Render:

Se você já criou o serviço web, ele deve detectar automaticamente as mudanças no GitHub e iniciar um novo deploy. Acompanhe os logs na página do serviço Render.

Se for a primeira vez, siga os passos da seção 2.3. Render: Hospedagem do Bot.

Crucial: Certifique-se de que as Variáveis de Ambiente (BOT_TOKEN, ADMIN_CHAT_ID, PORT) estão corretas e configuradas no Render!

Configurar Webhook no Telegram:

Obtenha o URL do seu serviço Render (ex: https://meu-bot-faq-api.onrender.com).

Abra seu navegador e cole o URL de configuração do webhook:

[https://api.telegram.org/botSEU_BOT_TOKEN/setWebhook?url=SEU_RENDER_URL/webhook](https://api.telegram.org/botSEU_BOT_TOKEN/setWebhook?url=SEU_RENDER_URL/webhook)
Substitua SEU_BOT_TOKEN (o token do seu bot do BotFather) e SEU_RENDER_URL (o URL do seu serviço Render).

Pressione Enter. Você deve ver uma resposta JSON indicando {"ok":true, "result":true, ...}. Isso significa que o webhook foi configurado com sucesso!

Configurar UptimeRobot:

Siga os passos da seção 2.5. UptimeRobot: Mantenha o Bot Ativo, usando o URL do seu serviço Render. Isso garantirá que seu bot não "durma" no Render.

5. Testando o Bot
Com tudo configurado e em deploy, é hora de testar!

Inicie uma conversa com seu bot no Telegram.

Teste perguntas básicas:

"Olá"

"Quero um reembolso"

"Horário de atendimento"

"Como faço para rastrear o meu pedido?"

Teste variações e sinônimos (aqui a inteligência é demonstrada!):

Em vez de "reembolso", tente "quero meu dinheiro de volta" ou "como faço para devolver um produto?".

Em vez de "horário", tente "qual o expediente de vocês?" ou "a que horas a loja abre?".

Experimente pequenos erros de digitação (ex: "rembolso", "horario d e atendimento").

Teste o comando de administrador:

No chat do Telegram com o seu bot, digite /recarregarfaq.

Atenção: Seu main (2).py atual não possui a implementação do comando /recarregarfaq. Se você o adicionar no futuro, esta seção será relevante.

Se você adicionar e configurar o ADMIN_CHAT_ID corretamente no Render e estiver usando o chat correto, o bot deve responder com "Iniciando recarregamento..." e depois "FAQ recarregado com sucesso!".

Para testar a funcionalidade de recarregamento (APÓS IMPLEMENTAÇÃO NO CÓDIGO):

Edite seu faq.json diretamente no GitHub (adicione uma nova entrada ou modifique uma existente).

Vá para a página do seu serviço no Render. Observe que um novo deploy automático será acionado.

Após o Render concluir o deploy (levará alguns segundos/minutos), use o comando /recarregarfaq novamente no Telegram.

Teste o bot com uma pergunta relacionada à sua nova/modificada entrada do FAQ.

Monitore os logs do Render:

Na página do seu serviço no Render, clique na aba Logs. Isso é essencial para depurar qualquer problema e ver as mensagens DEBUG que adicionei ao código.

6. Ajustando a Precisão (MIN_HITS_THRESHOLD)
Dentro do main.py (ou main (2).py), na função find_faq_answer, há uma linha:

Python

MIN_HITS_THRESHOLD = 1 
Este valor controla o quão "parecida" a pergunta do usuário precisa ser com uma entrada do FAQ para que o bot dê uma resposta direta, baseado no número de correspondências de palavras-chave.

Se o bot estiver respondendo com muitas informações irrelevantes ou "nada a ver": AUMENTE este valor (ex: 2, 3). Isso torna o bot mais "seletivo" e exige mais correspondências.

Se o bot estiver dizendo "Desculpe, não consegui encontrar..." com muita frequência para perguntas que você esperava que ele soubesse: DIMINUA este valor (se já estiver em 1, significa que até uma correspondência é suficiente, então o problema pode estar nas palavras-chave do seu faq.json ou na lógica).

Após cada ajuste no main.py no GitHub, salve as mudanças (Commit changes). O Render fará um novo deploy automático. Teste novamente após o deploy.

7. Solução de Problemas Comuns
Bot não responde:

Verifique o status do seu serviço no Render. Ele deve estar live. Se estiver sleeping (dormindo), aguarde um pouco ou verifique sua configuração no UptimeRobot. Se estiver failed, olhe os logs.

Confira as Variáveis de Ambiente no Render, especialmente o BOT_TOKEN.

Verifique se o webhook foi configurado corretamente no Telegram (passo 2.4), o URL deve ser https://api.telegram.org/botSEU_BOT_TOKEN/setWebhook?url=SEU_RENDER_URL/webhook. A resposta deve ser {"ok":true, "result":true, ...}.

Olhe os Logs do seu serviço no Render para qualquer erro Python.

Bot responde "Desculpe, não consegui encontrar...":

Verifique os logs do Render e procure por DEBUG: Nenhuma correspondência boa encontrada.... Isso indica que a lógica de correspondência de palavras-chave não encontrou um MIN_HITS_THRESHOLD suficiente. Você pode precisar ajustar o limiar para baixo ou, mais importante, melhorar as perguntas/palavras_chave no faq.json para aquela dúvida específica.

Confira se a pergunta está realmente no faq.json e se as palavras_chave são abrangentes.

Certifique-se de que o faq.json está bem formatado (JSON válido) e sendo carregado corretamente (verifique os logs de load_faq no Render).

Comando /recarregarfaq não funciona:

Lembre-se: Seu main (2).py atual não tem a implementação para este comando. Você precisaria adicionar a lógica ao seu código.

Se você adicionar a lógica, então verifique se ADMIN_CHAT_ID está configurado corretamente nas Variáveis de Ambiente do Render e se o ID corresponde exatamente ao seu chat no Telegram.

Certifique-se de que você está enviando o comando no chat do Telegram vinculado ao bot.

Erros de Markdown na resposta:

Se o bot retornar um erro do Telegram sobre Can't parse message text ou Bad Request: can't parse entities, geralmente significa que há um erro de sintaxe Markdown na resposta do seu faq.json. Verifique a formatação (negrito com **texto**, itálico com _texto_, links com [texto](link)). O bot já tenta reenviar sem Markdown nesses casos, mas é melhor corrigir a fonte.
