import os
import telebot
import json
import re
from flask import Flask, request
from telebot import types

# Pega o token do bot das variáveis de ambiente do Render
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Inicializa o bot
bot = telebot.TeleBot(BOT_TOKEN)

# Inicializa o Flask para o webhook
app = Flask(__name__)

# Variável global para armazenar as perguntas frequentes
faq_data = {}

def load_faq():
    """Carrega os dados do FAQ do arquivo faq.json."""
    global faq_data
    print("Tentando carregar FAQ...") # LOG: Início do carregamento do FAQ
    try:
        # Caminho para o faq.json na raiz do projeto
        faq_file_path = os.path.join(os.path.dirname(__file__), 'faq.json')
        with open(faq_file_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        print("FAQ carregado com sucesso!") # LOG: Sucesso no carregamento
    except FileNotFoundError:
        print("Erro: faq.json não encontrado. Certifique-se de que está na raiz do projeto.") # LOG: Erro de arquivo não encontrado
        faq_data = {}
    except json.JSONDecodeError as e:
        print(f"Erro: faq.json está mal formatado. Verifique a sintaxe JSON. Erro: {e}") # LOG: Erro de formato JSON
        faq_data = {}
    print(f"Tamanho do FAQ carregado: {len(faq_data)} entradas.") # LOG: Quantidade de entradas carregadas

# Carrega o FAQ ao iniciar o aplicativo
load_faq()

def find_faq_answers(query):
    """
    Busca respostas no FAQ baseadas na query do usuário.
    Retorna uma lista de dicionários com 'id', 'pergunta' e 'resposta'.
    """
    print(f"Procurando respostas para a query: '{query}'") # LOG: Início da busca
    query_lower = query.lower()
    matching_answers = []

    for faq_id, entry in faq_data.items():
        keywords = [kw.lower() for kw in entry.get('palavras_chave', [])]
        pergunta_lower = entry.get('pergunta', '').lower()

        # Prioriza correspondência exata na pergunta ou palavra-chave
        if query_lower in pergunta_lower:
            matching_answers.append({
                "id": entry["id"],
                "pergunta": entry["pergunta"],
                "resposta": entry["resposta"]
            })
            print(f"Correspondência exata encontrada para: {entry['pergunta']}") # LOG: Correspondência exata
            continue # Já encontrou uma boa correspondência, passa para o próximo FAQ

        # Busca por palavra-chave completa ou parcial
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower) or \
               (len(keyword) > 3 and keyword in query_lower): # Correspondência parcial para palavras maiores
                matching_answers.append({
                    "id": entry["id"],
                    "pergunta": entry["pergunta"],
                    "resposta": entry["resposta"]
                })
                print(f"Palavra-chave '{keyword}' encontrada para: {entry['pergunta']}") # LOG: Palavra-chave encontrada
                break # Encontrou uma palavra-chave, passa para o próximo FAQ

    # Remove duplicatas mantendo a ordem (ou quase)
    unique_matches = []
    seen_ids = set()
    for match in matching_answers:
        if match['id'] not in seen_ids:
            unique_matches.append(match)
            seen_ids.add(match['id'])

    print(f"Total de respostas encontradas: {len(unique_matches)}") # LOG: Total de respostas
    return unique_matches

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Manipula os comandos /start e /help."""
    print(f"Comando /start ou /help recebido de {message.from_user.id}") # LOG: Comando recebido
    welcome_faq_id = "1" # ID da pergunta de boas-vindas no faq.json
    if welcome_faq_id in faq_data:
        bot.reply_to(message, faq_data[welcome_faq_id]["resposta"])
        print("Mensagem de boas-vindas enviada.") # LOG: Mensagem enviada
    else:
        bot.reply_to(message, "Olá! Eu sou o assistente virtual da Chopp Brahma Express. Por favor, me diga como posso ajudar.")
        print("Mensagem de boas-vindas padrão enviada (FAQ ID 1 não encontrado).") # LOG: Mensagem padrão enviada

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Manipula todas as outras mensagens."""
    print(f"Mensagem de texto recebida de {message.from_user.id}: '{message.text}'") # LOG: Mensagem recebida
    user_query = message.text

    # Tenta encontrar a resposta no FAQ
    answers = find_faq_answers(user_query)

    if not answers:
        # Se não encontrou nenhuma resposta
        fallback_message = faq_data.get("54", {}).get("resposta", "Desculpe, não entendi sua pergunta. Por favor, reformule ou entre em contato com nosso suporte via WhatsApp: https://wa.me/556139717502")
        bot.reply_to(message, fallback_message)
        print("Nenhuma resposta encontrada. Mensagem de fallback enviada.") # LOG: Fallback
    elif len(answers) == 1:
        # Se encontrou uma única resposta clara
        bot.reply_to(message, answers[0]["resposta"])
        print(f"Resposta única encontrada e enviada (ID: {answers[0]['id']}).") # LOG: Resposta única
    else:
        # Se encontrou múltiplas respostas, oferece desambiguação com botões
        markup = types.InlineKeyboardMarkup()
        response_text = "Encontrei mais de uma resposta possível. Qual destas se aproxima mais da sua dúvida?\n\n"
        print(f"Múltiplas respostas encontradas: {len(answers)}. Oferecendo desambiguação.") # LOG: Múltiplas respostas
        for i, ans in enumerate(answers[:5]): # Limita a 5 opções para não sobrecarregar
            response_text += f"{i+1}. {ans['pergunta']}\n"
            # Adiciona um botão para cada opção, usando o ID do FAQ como callback_data
            markup.add(types.InlineKeyboardButton(text=ans['pergunta'], callback_data=f"faq_{ans['id']}"))

        # Adiciona um botão para falar com atendente se houver muitas opções ou se o usuário quiser
        if len(answers) > 5 or "falar com atendente" in user_query.lower() or "suporte" in user_query.lower():
            response_text += "\nOu se preferir, clique abaixo para falar com um de nossos atendentes."
            markup.add(types.InlineKeyboardButton(text="Falar com Atendente", callback_data="talk_to_human"))
            print("Botão 'Falar com Atendente' adicionado.") # LOG: Botão atendente

        bot.reply_to(message, response_text, reply_markup=markup)
        print("Mensagem de desambiguação enviada.") # LOG: Desambiguação enviada

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Manipula os cliques nos botões de desambiguação."""
    print(f"Callback query recebida: {call.data}") # LOG: Callback recebida
    if call.data.startswith("faq_"):
        faq_id = call.data.split("_")[1]
        if faq_id in faq_data:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=faq_data[faq_id]["resposta"],
                reply_markup=None # Remove os botões após a seleção
            )
            print(f"Resposta FAQ do callback enviada para ID: {faq_id}") # LOG: Resposta callback
        else:
            bot.answer_callback_query(call.id, "Erro: Resposta não encontrada.")
            print(f"Erro: FAQ ID {faq_id} não encontrado no callback.") # LOG: Erro callback
    elif call.data == "talk_to_human":
        # Resposta para falar com atendente (usa FAQ ID 54)
        fallback_message = faq_data.get("54", {}).get("resposta", "Por favor, entre em contato com nosso suporte via WhatsApp: https://wa.me/556139717502")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=fallback_message,
            reply_markup=None
        )
        print("Resposta 'Falar com Atendente' enviada.") # LOG: Atendente
    bot.answer_callback_query(call.id) # Fecha o alerta de carregamento do botão

# Rota para o webhook do Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    print("Requisição POST recebida no /webhook") # LOG: Requisição Webhook
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        print(f"JSON recebido: {json_string[:200]}...") # LOG: Conteúdo do JSON (primeiros 200 chars)
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        print("Update processado. Retornando 200 OK.") # LOG: Update processado
        return '!', 200 # Resposta HTTP 200 OK para o Telegram
    else:
        print(f"Erro: Tipo de conteúdo incorreto! Header: {request.headers.get('content-type')}") # LOG: Erro de Content-Type
        return 'Tipo de conteúdo incorreto!', 403

# Rota de 'health check' simples para verificar se o app está online
@app.route('/')
def index():
    print("Requisição GET recebida no / (Health Check)") # LOG: Health Check
    return 'Bot está online!', 200

# Executa o aplicativo Flask
if __name__ == '__main__':
    # Obtém a porta do ambiente Render
    port = int(os.environ.get("PORT", 5000))
    print(f"Iniciando aplicativo Flask na porta {port}") # LOG: Início do Flask
    app.run(host='0.0.0.0', port=port)
