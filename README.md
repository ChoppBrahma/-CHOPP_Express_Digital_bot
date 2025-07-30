# -CHOPP_Express_Digital_bot 
# Aqui está o seu guia completo, formatado como um arquivo README.md, pronto para ser copiado e colado diretamente no seu repositório do GitHub. Ele inclui todas as explicações, links e o conteúdo de cada arquivo, seguindo a estrutura Markdown para uma leitura clara e organizada.
# Guia Completo: Construindo Seu Bot de FAQ no Telegram com Python, Render e GitHub

Bem-vindo ao guia definitivo para criar e implantar seu próprio bot de FAQ no Telegram! Este `README.md` abrange desde a configuração inicial no Telegram até a hospedagem e manutenção, garantindo que seu bot esteja sempre online e responsivo.

## Sumário
1.  **Fase 1: A Gênese do Bot – O Nascimento no Telegram**
    * 1.1. Conhecendo o @BotFather
2.  **Fase 2: A Mente do Bot – Onde o Conhecimento Reside (Seus Arquivos!)**
    * 2.1. Criando a Base de Conhecimento: o `faq.json`
    * 2.2. O Coração do Bot: o `main.py`
    * 2.3. As Ferramentas do Bot: o `requirements.txt`
    * 2.4. A Instrução de Lançamento: o `Procfile`
3.  **Fase 3: A Base Secreta – Hospedando Seu Bot no Render**
    * 3.1. O Escritório na Nuvem: Criando sua Conta no Render
    * 3.2. Publicando o Manual: Enviando seu Código para o GitHub
    * 3.3. Montando o Escritório: Criando um Web Service no Render
    * 3.4. O Cofre Secreto: Adicionando Variáveis de Ambiente
    * 3.5. Conectando os Fios: Configurando o Webhook do Telegram
4.  **Fase 4: O Vigiante Noturno – Mantendo seu Bot Sempre Acordado (Plano Gratuito!)**
    * 4.1. O Guarda Noturno: Configurando o UptimeRobot
5.  **Fase 5: O Toque Final – Testes e Refinamentos**
6.  **Conteúdo dos Arquivos para Você Copiar e Colar (O Tesouro!)**
    * `main.py`
    * `requirements.txt`
    * `Procfile`
    * `faq.json` (Amostra)

---

## 1. Fase 1: A Gênese do Bot – O Nascimento no Telegram

Nesta fase, você criará a identidade do seu bot no Telegram e obterá sua chave de acesso.

### 1.1. Conhecendo o @BotFather: O Pai de Todos os Bots!

* **O que é:** O **@BotFather** é um bot oficial do Telegram, responsável por gerar novos bots e gerenciar suas configurações básicas.
* **Por que é crucial:** Ele fornece o `BOT_TOKEN`, a "chave de acesso" que seu código usará para se comunicar com a API do Telegram.
* **Passo a Passo:**
    1.  Abra o aplicativo **Telegram** (celular ou computador).
    2.  Na barra de pesquisa, digite `@BotFather` e selecione o contato verificado.
    3.  Inicie uma conversa (clique em "Iniciar" ou "Start").
    4.  Digite o comando `/newbot` e envie.
    5.  Escolha um **nome** amigável para seu bot (ex: `"Atendimento Soluções Rápidas"`).
    6.  Escolha um **username** único para seu bot, que deve terminar com `bot` (ex: `SolucoesRapidas_bot`).
    7.  O @BotFather parabenizará você e fornecerá o `BOT_TOKEN`. **Anote esse token imediatamente!** Ele é seu segredo.
* **Dica:** Considere criar um grupo de Telegram e adicionar seu bot para facilitar os testes.

---

## 2. Fase 2: A Mente do Bot – Onde o Conhecimento Reside (Seus Arquivos!)

Aqui, você criará os arquivos essenciais que dão "inteligência" e comportamento ao seu bot. Todos esses arquivos devem estar na **mesma pasta** no seu computador.

### 2.1. Criando a Base de Conhecimento: o `faq.json`

* **O que é:** Um arquivo formatado em JSON que armazena todas as suas perguntas frequentes (FAQs), respostas e palavras-chave. É o "cérebro" do seu bot.
* **Por que é crucial:** Sem ele, o bot não terá conteúdo para responder.
* **Passo a Passo:**
    1.  Abra um editor de texto (como Bloco de Notas, VS Code, Sublime Text).
    2.  Crie um novo arquivo e salve-o como `faq.json` na pasta do seu projeto.
    3.  **Conteúdo (Amostra):** Use esta estrutura e preencha com suas 55 FAQs. Certifique-se de que o JSON seja válido (chaves e valores de texto entre aspas duplas, vírgulas entre os itens, e o arquivo começando e terminando com `{}`).

    ```json
    {
      "1": {
        "id": 1,
        "pergunta": "Boas-vindas / Início de Conversa",
        "resposta": "Olá! Eu sou o **Bot de Suporte Rápido**, aqui para te ajudar com suas dúvidas. \n\nPosso te ajudar com:\n➡️ *Como pedir um orçamento?*\n➡️ *Quais os horários de atendimento?*\n➡️ *Problemas técnicos comuns?*\n\nOu digite sua pergunta específica!",
        "palavras_chave": [
          "oi", "olá", "bom dia", "boa tarde", "boa noite", "ajuda", "começar", "início", "saudação", "menu"
        ]
      },
      "15": {
        "id": 15,
        "pergunta": "Como solicitar um orçamento ou agendar um serviço?",
        "resposta": "Para solicitar um orçamento ou agendar um serviço, por favor, visite nosso site em [www.suaempresa.com.br/orcamento](https://www.suaempresa.com.br/orcamento) ou entre em contato via WhatsApp pelo número (XX) XXXXX-XXXX. Nossa equipe está pronta para te atender!",
        "palavras_chave": [
          "orçamento", "agendar", "solicitar", "preço", "custo", "serviço", "agendamento", "cotação", "valores"
        ]
      },
      "28": {
        "id": 28,
        "pergunta": "Quais são os horários de atendimento do suporte técnico?",
        "resposta": "Nosso suporte técnico funciona de segunda a sexta, das 8h às 18h. Para emergências fora do horário comercial, temos plantão de atendimento no WhatsApp.",
        "palavras_chave": [
          "horário", "atendimento", "suporte", "funcionamento", "plantão", "horários", "expediente", "abre"
        ]
      },
      "54": {
        "id": 54,
        "pergunta": "Não encontrei minha dúvida. Como posso falar com um humano?",
        "resposta": "Sentimos muito que você não tenha encontrado a resposta! Para falar com um de nossos atendentes, por favor, entre em contato via WhatsApp através do link: [Fale Conosco](https://wa.me/55XXYYYYYYYYY?text=Ol%C3%A1%2C+preciso+de+ajuda+com+uma%C3%BAd%C3%BAvida).",
        "palavras_chave": [
          "não encontrei", "humano", "falar com atendente", "contato", "atendimento pessoal", "emergência", "urgente"
        ]
      }
      // Adicione aqui todas as suas outras 51 FAQs, seguindo o mesmo padrão.
      // Certifique-se de que os IDs são únicos e as palavras-chave abrangentes!
    }
    ```

### 2.2. O Coração do Bot: o `main.py`

* **O que é:** O arquivo Python que contém toda a lógica do bot: leitura do FAQ, processamento de mensagens, busca de respostas e interação com o Telegram.
* **Por que é crucial:** É o motor que faz seu bot funcionar.
* **Passo a Passo:**
    1.  Crie um novo arquivo e salve-o como `main.py` na *mesma pasta* do `faq.json`.
    2.  **Conteúdo Completo:** Copie e cole o código a seguir:

    ```python
    import os
    import json
    from flask import Flask, request, jsonify
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    import traceback
    import re
    from unidecode import unidecode

    app = Flask(__name__)

    # --- Configuração do Token do Bot ---
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    if not BOT_TOKEN:
        print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
        exit(1)

    bot = telebot.TeleBot(BOT_TOKEN)

    # --- Variável Global para o FAQ ---
    faq_data = {}

    # --- Função para Carregar o FAQ ---
    def load_faq():
        global faq_data
        try:
            with open('faq.json', 'r', encoding='utf-8') as f:
                raw_faq = json.load(f)
                faq_data = {str(k): v for k, v in raw_faq.items()}
            print(f"FAQ carregado com sucesso! Total de {len(faq_data)} entradas.")
        except FileNotFoundError:
            print("Erro crítico: Arquivo faq.json não encontrado. Certifique-se de que ele está na mesma pasta do main.py.")
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON do faq.json: Verifique a sintaxe do arquivo. Erro: {e}")
        except Exception as e:
            print(f"Erro inesperado ao carregar FAQ: {e}")

    # --- Carrega o FAQ ao iniciar a aplicação ---
    load_faq()

    # --- Função para Normalizar Texto ---
    def normalize_text(text):
        if not isinstance(text, str):
            return ""
        return unidecode(text).lower()

    # --- Função para Encontrar a Melhor FAQ ---
    def find_faq_answer(query):
        normalized_query = normalize_text(query)
        best_match_id = None
        max_score = 0
        found_by_direct_keyword = False

        for faq_id, faq in faq_data.items():
            normalized_keywords = [normalize_text(kw) for kw in faq.get('palavras_chave', [])]
            for kw in normalized_keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', normalized_query):
                    best_match_id = faq_id
                    found_by_direct_keyword = True
                    break
            if found_by_direct_keyword:
                break
        
        if found_by_direct_keyword:
            return best_match_id, found_by_direct_keyword

        for faq_id, faq in faq_data.items():
            normalized_pergunta = normalize_text(faq.get('pergunta', ''))
            score = 0
            query_words = normalized_query.split()
            
            for word in query_words:
                if word and word in normalized_pergunta:
                    score += 1

            if score > max_score:
                max_score = score
                best_match_id = faq_id

        return best_match_id, found_by_direct_keyword

    # --- Função para Gerar Botões de Perguntas Relacionadas ---
    def get_related_buttons(query, primary_faq_id=None, max_buttons=5):
        normalized_query = normalize_text(query)
        related_faqs_candidates = []
        seen_ids = set()

        if primary_faq_id:
            seen_ids.add(primary_faq_id)

        for faq_id, faq in faq_data.items():
            if faq_id in seen_ids:
                continue

            normalized_keywords = [normalize_text(kw) for kw in faq.get('palavras_chave', [])]
            normalized_pergunta = normalize_text(faq.get('pergunta', ''))
            
            is_relevant = False
            
            for kw in normalized_keywords:
                if kw and kw in normalized_query:
                    is_relevant = True
                    break
            
            if not is_relevant:
                if any(word and word in normalized_pergunta for word in normalized_query.split()):
                    is_relevant = True

            if not is_relevant:
                if any(re.search(r'\b' + re.escape(q_word) + r'\b', kw) for q_word in normalized_query.split() for kw in normalized_keywords):
                    is_relevant = True
                if not is_relevant and any(re.search(r'\b' + re.escape(q_word) + r'\b', normalized_pergunta) for q_word in normalized_query.split()):
                    is_relevant = True

            if is_relevant:
                related_faqs_candidates.append({'id': faq_id, 'pergunta': faq['pergunta']})

        selected_buttons = []
        for faq_item in related_faqs_candidates:
            if len(selected_buttons) < max_buttons:
                button_text = faq_item['pergunta']
                if len(button_text.encode('utf-8')) > 60:
                    button_text = button_text[:25] + "..."
                
                selected_buttons.append(
                    InlineKeyboardButton(
                        text=button_text,
                        callback_data=str(faq_item['id'])
                    )
                )

        if '54' in faq_data and '54' not in seen_ids:
            if not selected_buttons or len(selected_buttons) < max_buttons:
                selected_buttons.append(
                    InlineKeyboardButton(
                        text=faq_data['54']['pergunta'],
                        callback_data='54'
                    )
                )

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*selected_buttons)
    return markup

    # --- Handler para Mensagens de Texto (Quando o Usuário Digita) ---
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        chat_id = message.chat.id
        user_query = message.text

        print(f"Mensagem recebida do chat {chat_id}: '{user_query}'")

        if not faq_data:
            bot.send_message(chat_id, "Desculpe, meu banco de dados de FAQs não foi carregado. Por favor, tente novamente mais tarde ou contate o suporte técnico.")
            print("ERRO: FAQ_DATA está vazio. Bot não pode responder.")
            return

        if '54' in faq_data:
            keywords_54 = [normalize_text(kw) for kw in faq_data['54'].get('palavras_chave', [])]
            pergunta_54 = normalize_text(faq_data['54'].get('pergunta', ''))
            
            if normalize_text(user_query) in keywords_54 or normalize_text(user_query) == pergunta_54:
                response_text = faq_data['54']['resposta']
                bot.send_message(chat_id, response_text, parse_mode='Markdown')
                print(f"----> Resposta enviada para ID 54 por query direta para o chat {chat_id}.")
                return

        best_match_id, _ = find_faq_answer(user_query)

        if best_match_id:
            response_text = faq_data[best_match_id]['resposta']
            markup = get_related_buttons(user_query, primary_faq_id=best_match_id)
            
            bot.send_message(chat_id, response_text, parse_mode='Markdown', reply_markup=markup)
            print(f"----> Resposta enviada para ID {best_match_id} com botões relacionados para o chat {chat_id}.")
        else:
            if '54' in faq_data:
                response_text = faq_data['54']['resposta']
                bot.send_message(chat_id, response_text, parse_mode='Markdown')
                print(f"----> Nenhuma FAQ correspondente encontrada. Enviando resposta padrão (ID 54) para o chat {chat_id}.")
            else:
                bot.send_message(chat_id, "Desculpe, não consegui encontrar uma resposta para sua pergunta e a opção de suporte não está disponível. Por favor, tente reformular sua pergunta.")
                print(f"----> ERRO: Nenhuma FAQ correspondente e ID 54 não disponível. Chat {chat_id}.")

    # --- Handler para Callback Queries (Cliques nos Botões Inline) ---
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call):
        chat_id = call.message.chat.id
        callback_data = call.data
        
        print(f"Callback Query recebida do chat {chat_id} com dados: '{callback_data}'")

        bot.answer_callback_query(call.id, text="Carregando resposta...") 

        if callback_data in faq_data:
            response_text = faq_data[callback_data]['resposta']
            markup = get_related_buttons(faq_data[callback_data]['pergunta'], primary_faq_id=callback_data)
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=response_text,
                parse_mode='Markdown',
                reply_markup=markup
            )
            print(f"----> Resposta da Callback Query enviada com sucesso para o chat {chat_id}.")
        else:
            bot.send_message(chat_id, "Desculpe, não encontrei a informação solicitada pelo botão.", parse_mode='Markdown')
            print(f"----> ERRO: FAQ ID '{callback_data}' não encontrado para Callback Query.")

    # --- Rota do Webhook para o Render ---
    @app.route(f'/{BOT_TOKEN}', methods=['POST'])
    def webhook():
        if request.method == 'POST':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            
            try:
                bot.process_new_updates([update])
                print("Update processado com sucesso pelo Telebot.")
            except Exception as e:
                print(f"ERRO ao processar update do webhook: {e}")
                print(traceback.format_exc())
            
            return 'OK', 200
        else:
            return 'Método não permitido', 405

    # --- Rota Inicial (para verificar se o bot está rodando) ---
    @app.route('/')
    def index():
        return 'Bot de FAQ está online e rodando!'

    # --- Execução Principal do Aplicativo Flask ---
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    ```

### 2.3. As Ferramentas do Bot: o `requirements.txt`

* **O que é:** Lista as bibliotecas Python e suas versões que seu `main.py` precisa.
* **Por que é crucial:** Garante que o ambiente de execução no servidor (Render) tenha as dependências corretas.
* **Passo a Passo:**
    1.  Crie um novo arquivo e salve-o como `requirements.txt` na *mesma pasta* dos outros arquivos.
    2.  **Conteúdo Completo:**

    ```
    Flask==2.3.2
    pyTelegramBotAPI==4.10.0
    gunicorn==20.1.0
    unidecode==1.3.6
    ```

### 2.4. A Instrução de Lançamento: o `Procfile`

* **O que é:** Um arquivo sem extensão que informa ao Render como iniciar sua aplicação.
* **Por que é crucial:** O Render o usa para executar o comando correto para subir seu bot.
* **Passo a Passo:**
    1.  Crie um novo arquivo e salve-o como `Procfile` (sem extensão!) na *mesma pasta* dos outros arquivos.
    2.  **Conteúdo Completo:**

    ```
    web: gunicorn main:app
    ```

---

## 3. Fase 3: A Base Secreta – Hospedando Seu Bot no Render

Aqui, você publicará seu código e configurará seu bot para rodar 24/7.

### 3.1. O Escritório na Nuvem: Criando sua Conta no Render

* **O que é:** Um serviço de hospedagem que permite rodar seu código continuamente.
* **Por que é crucial:** Seu bot precisa estar online para responder aos usuários a qualquer momento.
* **Passo a Passo:**
    1.  Acesse [Render.com](https://render.com/).
    2.  Clique em "Get started free" ou "Sign Up".
    3.  **Recomendado:** Cadastre-se e **conecte sua conta do GitHub** para facilitar a integração.

### 3.2. Publicando o Manual: Enviando seu Código para o GitHub

* **O que é:** Uma plataforma para hospedar seu código e permitir que o Render o acesse.
* **Por que é crucial:** O Render se integra diretamente com o GitHub para deploys automatizados.
* **Passo a Passo:**
    1.  Crie uma conta em [GitHub.com](https://github.com/) (se ainda não tiver).
    2.  Crie um "New repository" no GitHub (ex: `bot-suporte-automatizado`).
    3.  Escolha "Public" ou "Private".
    4.  Faça o upload (`git push` ou "Add file" -> "Upload files" via web) de todos os seus arquivos (`faq.json`, `main.py`, `requirements.txt`, `Procfile`) para este repositório.

### 3.3. Montando o Escritório: Criando um Web Service no Render

* **O que é:** O tipo de serviço no Render ideal para hospedar seu bot baseado em Flask.
* **Por que é crucial:** É onde o Render lerá seu código e iniciará seu bot.
* **Passo a Passo:**
    1.  No painel do Render, clique em `New` > `Web Service`.
    2.  Selecione e conecte seu repositório GitHub (ex: `bot-suporte-automatizado`).
    3.  **Configurações do Serviço Web:**
        * **Name:** `meu-bot-faq-render` (ou um nome de sua escolha).
        * **Region:** Escolha a mais próxima dos seus usuários (ex: `São Paulo` ou `Ohio`).
        * **Branch:** `main` (geralmente).
        * **Root Directory:** Deixe **vazio**.
        * **Runtime:** `Python 3`.
        * **Build Command:** `pip install -r requirements.txt`
        * **Start Command:** `gunicorn main:app`
        * **Plan Type:** Selecione `Free`.
    4.  Clique em "Create Web Service".

### 3.4. O Cofre Secreto: Adicionando Variáveis de Ambiente

* **O que é:** Um método seguro para armazenar informações sensíveis (como o `BOT_TOKEN`) sem expô-las no código público.
* **Por que é crucial:** Protege seu `BOT_TOKEN` de acesso indevido.
* **Passo a Passo:**
    1.  No painel do Render, vá para o seu serviço (ex: `meu-bot-faq-render`).
    2.  Clique na aba **`Environment`**.
    3.  Clique em "Add Environment Variable".
    4.  **Key:** `BOT_TOKEN`
    5.  **Value:** Cole o `BOT_TOKEN` que você obteve do @BotFather.
    6.  Clique em "Add Variable". O Render reiniciará o serviço automaticamente.

### 3.5. Conectando os Fios: Configurando o Webhook do Telegram

* **O que é:** A comunicação que informa ao Telegram onde enviar as mensagens recebidas pelo seu bot.
* **Por que é crucial:** Sem o webhook configurado, seu bot não receberá as mensagens dos usuários.
* **Passo a Passo:**
    1.  Após o deploy do seu serviço no Render estar "Live", copie o **URL público** do seu bot (ex: `https://meu-bot-faq-render.onrender.com/`).
    2.  Abra seu navegador e monte a seguinte URL, substituindo pelos seus dados:
        `https://api.telegram.org/botSEU_BOT_TOKEN/setWebhook?url=SEU_RENDER_URL/SEU_BOT_TOKEN`
        * **Exemplo:** Se seu `BOT_TOKEN` é `123456:ABC-DEF1234ghIkl-zyx57W2E1` e seu Render URL é `https://meu-bot-faq-render.onrender.com/`, a URL no navegador seria:
            `https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2E1/setWebhook?url=https://meu-bot-faq-render.onrender.com/123456:ABC-DEF1234ghIkl-zyx57W2E1`
    3.  Pressione Enter. Você deve ver uma mensagem JSON com `{"ok":true, "result":true, ...}`.

---

## 4. Fase 4: O Vigiante Noturno – Mantendo seu Bot Sempre Acordado (Plano Gratuito!)

Este passo é vital para evitar que seu bot no plano gratuito do Render "durma" por inatividade.

### 4.1. O Guarda Noturno: Configurando o UptimeRobot

* **O que é:** Um serviço que monitora a disponibilidade do seu bot e o "visita" periodicamente para mantê-lo ativo.
* **Por que é crucial:** Planos gratuitos podem suspender o bot após um tempo de inatividade, causando atrasos na resposta. O UptimeRobot evita isso.
* **Passo a Passo:**
    1.  Acesse [UptimeRobot.com](https://uptimerobot.com/) e crie uma conta gratuita.
    2.  No painel, clique em "Add New Monitor".
    3.  **Configure o Monitor:**
        * **Monitor Type:** `HTTP(s)`.
        * **Friendly Name:** `Meu Bot de FAQ - Render`.
        * **URL (or IP):** Cole o **URL do seu bot no Render** (ex: `https://meu-bot-faq-render.onrender.com/`).
        * **Monitoring Interval:** `5 minutes`.
        * **Alert Contacts:** Desmarque (a menos que queira notificações).
    4.  Clique em "Create Monitor".

---

## 5. Fase 5: O Toque Final – Testes e Refinamentos

Com tudo configurado, é hora de testar e aprimorar seu bot!

1.  **Teste Imediato:** No Telegram, envie mensagens para seu bot. Teste perguntas que estão no `faq.json` e também uma que não está (para verificar a FAQ de "Não encontrei minha dúvida").
2.  **Monitore os Logs:** Acesse a aba **`Logs`** do seu serviço no painel do Render para ver o que o bot está fazendo e identificar possíveis erros.
3.  **Refine o `faq.json`:**
    * **Ajuste Palavras-Chave:** Adicione sinônimos e variações de perguntas.
    * **Crie Novas FAQs:** Adicione respostas para dúvidas comuns que surgirem.
    * **Dica:** Cada `git push` para o seu repositório GitHub acionará um novo deploy automático no Render. Acompanhe os logs!

---

## 6. Conteúdo dos Arquivos para Você Copiar e Colar (O Tesouro!):

Aqui estão os conteúdos exatos dos seus arquivos. Crie-os e salve-os conforme as instruções acima.

### 6.1. `main.py` (Conteúdo Completo):

```python
import os
import json
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import traceback
import re
from unidecode import unidecode

app = Flask(__name__)

# --- Configuração do Token do Bot ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# --- Variável Global para o FAQ ---
faq_data = {}

# --- Função para Carregar o FAQ ---
def load_faq():
    global faq_data
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            raw_faq = json.load(f)
            faq_data = {str(k): v for k, v in raw_faq.items()}
        print(f"FAQ carregado com sucesso! Total de {len(faq_data)} entradas.")
    except FileNotFoundError:
        print("Erro crítico: Arquivo faq.json não encontrado. Certifique-se de que ele está na mesma pasta do main.py.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: Verifique a sintaxe do arquivo. Erro: {e}")
    except Exception as e:
        print(f"Erro inesperado ao carregar FAQ: {e}")

load_faq()

# --- Função para Normalizar Texto ---
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    return unidecode(text).lower()

# --- Função para Encontrar a Melhor FAQ ---
def find_faq_answer(query):
    normalized_query = normalize_text(query)
    best_match_id = None
    max_score = 0
    found_by_direct_keyword = False

    for faq_id, faq in faq_data.items():
        normalized_keywords = [normalize_text(kw) for kw in faq.get('palavras_chave', [])]
        for kw in normalized_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', normalized_query):
                best_match_id = faq_id
                found_by_direct_keyword = True
                break
        if found_by_direct_keyword:
            break
    
    if found_by_direct_keyword:
        return best_match_id, found_by_direct_keyword

    for faq_id, faq in faq_data.items():
        normalized_pergunta = normalize_text(faq.get('pergunta', ''))
        score = 0
        query_words = normalized_query.split()
        
        for word in query_words:
            if word and word in normalized_pergunta:
                score += 1

        if score > max_score:
            max_score = score
            best_match_id = faq_id

    return best_match_id, found_by_direct_keyword

# --- Função para Gerar Botões de Perguntas Relacionadas ---
def get_related_buttons(query, primary_faq_id=None, max_buttons=5):
    normalized_query = normalize_text(query)
    related_faqs_candidates = []
    seen_ids = set()

    if primary_faq_id:
        seen_ids.add(primary_faq_id)

    for faq_id, faq in faq_data.items():
        if faq_id in seen_ids:
            continue

        normalized_keywords = [normalize_text(kw) for kw in faq.get('palavras_chave', [])]
        normalized_pergunta = normalize_text(faq.get('pergunta', ''))
        
        is_relevant = False
        
        for kw in normalized_keywords:
            if kw and kw in normalized_query:
                is_relevant = True
                break
        
        if not is_relevant:
            if any(word and word in normalized_pergunta for word in normalized_query.split()):
                is_relevant = True

        if not is_relevant:
            if any(re.search(r'\b' + re.escape(q_word) + r'\b', kw) for q_word in normalized_query.split() for kw in normalized_keywords):
                is_relevant = True
            if not is_relevant and any(re.search(r'\b' + re.escape(q_word) + r'\b', normalized_pergunta) for q_word in normalized_query.split()):
                is_relevant = True

        if is_relevant:
            related_faqs_candidates.append({'id': faq_id, 'pergunta': faq['pergunta']})

    selected_buttons = []
    for faq_item in related_faqs_candidates:
        if len(selected_buttons) < max_buttons:
            button_text = faq_item['pergunta']
            if len(button_text.encode('utf-8')) > 60:
                button_text = button_text[:25] + "..."
            
            selected_buttons.append(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=str(faq_item['id'])
                )
            )

    if '54' in faq_data and '54' not in seen_ids:
        if not selected_buttons or len(selected_buttons) < max_buttons:
            selected_buttons.append(
                InlineKeyboardButton(
                    text=faq_data['54']['pergunta'],
                    callback_data='54'
                )
            )

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*selected_buttons)
    return markup

# --- Handler para Mensagens de Texto (Quando o Usuário Digita) ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_query = message.text

    print(f"Mensagem recebida do chat {chat_id}: '{user_query}'")

    if not faq_data:
        bot.send_message(chat_id, "Desculpe, meu banco de dados de FAQs não foi carregado. Por favor, tente novamente mais tarde ou contate o suporte técnico.")
        print("ERRO: FAQ_DATA está vazio. Bot não pode responder.")
        return

    if '54' in faq_data:
        keywords_54 = [normalize_text(kw) for kw in faq_data['54'].get('palavras_chave', [])]
        pergunta_54 = normalize_text(faq_data['54'].get('pergunta', ''))
        
        if normalize_text(user_query) in keywords_54 or normalize_text(user_query) == pergunta_54:
            response_text = faq_data['54']['resposta']
            bot.send_message(chat_id, response_text, parse_mode='Markdown')
            print(f"----> Resposta enviada para ID 54 por query direta para o chat {chat_id}.")
            return

    best_match_id, _ = find_faq_answer(user_query)

    if best_match_id:
        response_text = faq_data[best_match_id]['resposta']
        markup = get_related_buttons(user_query, primary_faq_id=best_match_id)
        
        bot.send_message(chat_id, response_text, parse_mode='Markdown', reply_markup=markup)
        print(f"----> Resposta enviada para ID {best_match_id} com botões relacionados para o chat {chat_id}.")
    else:
        if '54' in faq_data:
            response_text = faq_data['54']['resposta']
            bot.send_message(chat_id, response_text, parse_mode='Markdown')
            print(f"----> Nenhuma FAQ correspondente encontrada. Enviando resposta padrão (ID 54) para o chat {chat_id}.")
        else:
            bot.send_message(chat_id, "Desculpe, não consegui encontrar uma resposta para sua pergunta e a opção de suporte não está disponível. Por favor, tente reformular sua pergunta.")
            print(f"----> ERRO: Nenhuma FAQ correspondente e ID 54 não disponível. Chat {chat_id}.")

# --- Handler para Callback Queries (Cliques nos Botões Inline) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chat_id = call.message.chat.id
    callback_data = call.data
    
    print(f"Callback Query recebida do chat {chat_id} com dados: '{callback_data}'")

    bot.answer_callback_query(call.id, text="Carregando resposta...") 

    if callback_data in faq_data:
        response_text = faq_data[callback_data]['resposta']
        markup = get_related_buttons(faq_data[callback_data]['pergunta'], primary_faq_id=callback_data)
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=response_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
        print(f"----> Resposta da Callback Query enviada com sucesso para o chat {chat_id}.")
    else:
        bot.send_message(chat_id, "Desculpe, não encontrei a informação solicitada pelo botão.", parse_mode='Markdown')
        print(f"----> ERRO: FAQ ID '{callback_data}' não encontrado para Callback Query.")

# --- Rota do Webhook para o Render ---
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        
        try:
            bot.process_new_updates([update])
            print("Update processado com sucesso pelo Telebot.")
        except Exception as e:
            print(f"ERRO ao processar update do webhook: {e}")
            print(traceback.format_exc())
        
        return 'OK', 200
    else:
        return 'Método não permitido', 405

# --- Rota Inicial (para verificar se o bot está rodando) ---
@app.route('/')
def index():
    return 'Bot de FAQ está online e rodando!'

# --- Execução Principal do Aplicativo Flask ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

### 6.2. `requirements.txt` (Conteúdo Completo):

Flask==2.3.2
pyTelegramBotAPI==4.10.0
gunicorn==20.1.0
unidecode==1.3.6


### 6.3. `Procfile` (Conteúdo Completo):

web: gunicorn main:app


### 6.4. `faq.json` (Amostra - Adapte com suas 55 FAQs!):

```json
{
  "1": {
    "id": 1,
    "pergunta": "Boas-vindas / Início de Conversa",
    "resposta": "Olá! Eu sou o **Bot de Suporte Rápido**, aqui para te ajudar com suas dúvidas. \n\nPosso te ajudar com:\n➡️ *Como pedir um orçamento?*\n➡️ *Quais os horários de atendimento?*\n➡️ *Problemas técnicos comuns?*\n\nOu digite sua pergunta específica!",
    "palavras_chave": [
      "oi", "olá", "bom dia", "boa tarde", "boa noite", "ajuda", "começar", "início", "saudação", "menu"
    ]
  },
  "15": {
    "id": 15,
    "pergunta": "Como solicitar um orçamento ou agendar um serviço?",
    "resposta": "Para solicitar um orçamento ou agendar um serviço, por favor, visite nosso site em [www.suaempresa.com.br/orcamento](https://www.suaempresa.com.br/orcamento) ou entre em contato via WhatsApp pelo número (XX) XXXXX-XXXX. Nossa equipe está pronta para te atender!",
    "palavras_chave": [
      "orçamento", "agendar", "solicitar", "preço", "custo", "serviço", "agendamento", "cotação", "valores"
    ]
  },
  "28": {
    "id": 28,
    "pergunta": "Quais são os horários de atendimento do suporte técnico?",
    "resposta": "Nosso suporte técnico funciona de segunda a sexta, das 8h às 18h. Para emergências fora do horário comercial, temos plantão de atendimento no WhatsApp.",
    "palavras_chave": [
      "horário", "atendimento", "suporte", "funcionamento", "plantão", "horários", "expediente", "abre"
    ]
  },
  "52": {
    "id": 52,
    "pergunta": "Quais são os contatos para suporte em emergências (plantão)?",
    "resposta": "Para suporte em emergências fora do horário comercial (finais de semana e feriados), você pode entrar em contato pelo telefone (XX) YYYYY-YYYY ou via WhatsApp no mesmo número. Este serviço é dedicado a casos urgentes.",
    "palavras_chave": [
      "emergência", "plantão", "contato urgente", "fim de semana", "feriado", "socorro", "problema agora"
    ]
  },
  "54": {
    "id": 54,
    "pergunta": "Não encontrei minha dúvida. Como posso falar com um humano?",
    "resposta": "Sentimos muito que você não tenha encontrado a resposta! Para falar com um de nossos atendentes, por favor, entre em contato via WhatsApp através do link: [Fale Conosco](https://wa.me/55XXYYYYYYYYY?text=Ol%C3%A1%2C+preciso+de+ajuda+com+uma%C3%BAd%C3%BAvida).",
    "palavras_chave": [
      "não encontrei", "humano", "falar com atendente", "contato", "atendimento pessoal", "emergência", "urgente"
    ]
  }
  // ... continue adicionando suas outras FAQs aqui, mantendo a estrutura!
}
