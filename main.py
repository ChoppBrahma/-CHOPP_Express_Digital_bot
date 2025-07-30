import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)

# --- Configurações do Bot Telegram ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    exit(1)
bot = telebot.TeleBot(BOT_TOKEN)

# --- Variável global para armazenar o FAQ ---
faq_data = {}

def load_faq():
    global faq_data
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            raw_faq = json.load(f)
            faq_data = {str(k): v for k, v in raw_faq.items()}
        print(f"FAQ carregado com sucesso! Tamanho do FAQ: {len(faq_data)} entradas.")
    except FileNotFoundError:
        print("Erro: Arquivo faq.json não encontrado. O bot NÃO poderá responder via FAQ.")
        faq_data = {}
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: {e}. Verifique a sintaxe do arquivo.")
        faq_data = {}

# Chama a função para carregar o FAQ quando o bot inicia
load_faq()

# --- Função para encontrar a melhor correspondência no FAQ (MAIS DIRETA) ---
def find_faq_answer(query):
    if not faq_data:
        print("DEBUG: FAQ data não carregado em find_faq_answer.")
        return None, None

    normalized_query = query.lower().strip()

    # Prioriza correspondência EXATA da pergunta do usuário com uma palavra-chave
    for faq_id, entry in faq_data.items():
        keywords = [k.lower().strip() for k in entry.get('palavras_chave', [])]
        for keyword in keywords:
            if normalized_query == keyword:
                print(f"DEBUG: Correspondência EXATA de query com keyword! FAQ ID: {faq_id}, Keyword: '{keyword}'")
                return entry.get('resposta'), faq_id
    
    # Se não houver correspondência exata, busca por uma palavra-chave CONTIDA na pergunta
    best_faq_id_by_keyword_hits = None
    max_keyword_hits = 0
    
    MIN_HITS_THRESHOLD = 1 

    for faq_id, entry in faq_data.items():
        keywords = [k.lower().strip() for k in entry.get('palavras_chave', [])]
        current_hits = 0
        
        for keyword in keywords:
            if keyword in normalized_query or normalized_query in keyword:
                current_hits += 1
        
        pergunta_faq_normalizada = entry.get('pergunta', '').lower().strip()
        if pergunta_faq_normalizada and pergunta_faq_normalizada in normalized_query:
            current_hits += 1 

        if current_hits > max_keyword_hits:
            max_keyword_hits = current_hits
            best_faq_id_by_keyword_hits = faq_id

    print(f"DEBUG: Melhor correspondência por hits: ID {best_faq_id_by_keyword_hits} com {max_keyword_hits} hits.")

    if max_keyword_hits >= MIN_HITS_THRESHOLD and best_faq_id_by_keyword_hits:
        return faq_data[best_faq_id_by_keyword_hits].get('resposta'), best_faq_id_by_keyword_hits
    
    print("DEBUG: Nenhuma correspondência boa encontrada por hits de palavras-chave.")
    return None, None


# --- Função para encontrar e gerar botões de perguntas relacionadas (AGORA COM MAIS BOTÕES) ---
# Aumentei o max_buttons para 5. Você pode ajustar esse valor se precisar de mais.
def get_related_buttons(query, primary_faq_id=None, max_buttons=10): # <<< AQUI A MUDANÇA
    related_buttons = []
    normalized_query = query.lower().strip()
    
    RELATED_HITS_THRESHOLD = 1 

    print(f"DEBUG: Buscando botões relacionados para query '{query}', excluindo ID '{primary_faq_id}'.")

    for faq_id, entry in faq_data.items():
        if faq_id == primary_faq_id: 
            continue

        keywords = [k.lower().strip() for k in entry.get('palavras_chave', [])]
        pergunta_text = entry.get('pergunta', '').lower().strip()

        current_related_hits = 0
        for keyword in keywords + [pergunta_text]:
            if not keyword: continue
            if keyword in normalized_query or normalized_query in keyword:
                current_related_hits += 1
        
        if current_related_hits >= RELATED_HITS_THRESHOLD:
            if (faq_id, entry.get('pergunta')) not in related_buttons:
                related_buttons.append((faq_id, entry.get('pergunta')))
        
        if len(related_buttons) >= max_buttons: 
            break

    if related_buttons:
        markup = InlineKeyboardMarkup()
        for faq_id, pergunta in related_buttons:
            markup.add(InlineKeyboardButton(pergunta, callback_data=str(faq_id))) 
        print(f"DEBUG: Botões relacionados gerados: {len(related_buttons)}.")
        return markup
    print("DEBUG: Nenhum botão relacionado encontrado.")
    return None 

@app.route('/')
def health_check():
    print("Requisição GET recebida no / (Health Check)")
    return "Bot está funcionando!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
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
                    faq_answer, faq_id_matched = find_faq_answer(text)

                    if faq_answer:
                        response_text = faq_answer
                        print(f"----> Resposta principal encontrada no FAQ (ID: {faq_id_matched}): '{response_text}'")
                        markup = get_related_buttons(text, faq_id_matched)
                        
                    else:
                        response_text = "Desculpe, não consegui encontrar uma resposta para sua pergunta no meu FAQ. Por favor, tente perguntar de outra forma ou consulte nosso site oficial."
                        print(f"----> Nenhuma resposta principal encontrada no FAQ para: '{text}'. Enviando fallback genérico.")
                    
                    try:
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        if "Can't parse message text" in str(e):
                            print("DICA: Texto pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                            bot.send_message(chat_id, response_text, parse_mode=None, reply_markup=markup) 
                        else:
                            pass
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

            elif update.callback_query:
                callback_query = update.callback_query
                chat_id = callback_query.message.chat.id
                callback_data = callback_query.data 

                print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")
                bot.answer_callback_query(callback_query.id) 

                try:
                    if callback_data in faq_data:
                        response_text = faq_data[callback_data].get('resposta')
                        bot.send_message(chat_id, response_text, parse_mode='Markdown')
                        print(f"----> Resposta da Callback Query enviada com sucesso para o chat {chat_id}.")
                    else:
                        bot.send_message(chat_id, "Desculpe, não encontrei a informação solicitada pelo botão.", parse_mode='Markdown')
                        print(f"----> ERRO: FAQ ID '{callback_data}' não encontrado para Callback Query.")
                except Exception as e:
                    print(f"ERRO ao processar Callback Query para FAQ ID {callback_data}: {e}")
                    print(traceback.format_exc())
            
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
    app.run(host='0.0.0.0', port=port)
