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
