import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback
from fuzzywuzzy import fuzz # Para encontrar similaridades no FAQ

app = Flask(__name__)

# --- Configurações do Bot Telegram ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    exit(1) # Sair se o token não estiver configurado
bot = telebot.TeleBot(BOT_TOKEN)

# --- Variável global para armazenar o FAQ ---
faq_data = {}

def load_faq():
    global faq_data
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            # Garante que as chaves do dicionário FAQ sejam strings
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

# --- Função para encontrar a melhor correspondência no FAQ ---
def find_faq_answer(query):
    # Se o FAQ não foi carregado, não há respostas para encontrar.
    if not faq_data:
        return None, None

    normalized_query = query.lower()
    best_match_id = None
    best_score = 0
    # Limiar para considerar uma correspondência boa o suficiente (0-100)
    # Ajuste este valor: maior = mais rigoroso, menor = mais flexível
    MATCH_THRESHOLD = 75 

    for faq_id, entry in faq_data.items():
        keywords = [k.lower() for k in entry.get('palavras_chave', [])]
        
        # Tentativa de correspondência exata ou muito alta primeiro
        for keyword in keywords:
            if keyword == normalized_query:
                return entry.get('resposta'), faq_id # Correspondência exata, retornar imediatamente
            
            # Usar fuzz.ratio para similaridade geral da frase
            score_ratio = fuzz.ratio(normalized_query, keyword)
            if score_ratio > best_score:
                best_score = score_ratio
                best_match_id = faq_id

            # Usar fuzz.partial_ratio para verificar se parte da query corresponde à keyword
            score_partial_ratio = fuzz.partial_ratio(normalized_query, keyword)
            if score_partial_ratio > best_score:
                best_score = score_partial_ratio
                best_match_id = faq_id

            # Usar fuzz.token_sort_ratio para lidar com ordem de palavras diferente
            score_token_sort = fuzz.token_sort_ratio(normalized_query, keyword)
            if score_token_sort > best_score:
                best_score = score_token_sort
                best_match_id = faq_id

    if best_score >= MATCH_THRESHOLD and best_match_id:
        return faq_data[best_match_id].get('resposta'), best_match_id
    
    return None, None # Nenhuma correspondência boa encontrada no FAQ

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
                markup = None # Sem botões dinâmicos por padrão para manter "enxuto"

                if text:
                    # Tenta encontrar no FAQ
                    faq_answer, faq_id_matched = find_faq_answer(text)

                    if faq_answer:
                        response_text = faq_answer
                        print(f"----> Resposta encontrada no FAQ (ID: {faq_id_matched}): '{response_text}'")
                    else:
                        response_text = "Desculpe, não consegui encontrar uma resposta para sua pergunta no meu FAQ. Por favor, tente perguntar de outra forma ou consulte nosso site oficial."
                        print(f"----> Nenhuma resposta encontrada no FAQ para: '{text}'. Enviando fallback genérico.")

                    try:
                        # Tenta enviar como Markdown, mas com tratamento de erro
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        if "Can't parse message text" in str(e):
                            print("DICA: Texto pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                            bot.send_message(chat_id, response_text, parse_mode=None)
                        else:
                            # Re-raise other API exceptions if you want to handle them specifically
                            pass
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

            elif update.callback_query:
                # Esta seção é acionada por cliques em botões inline
                callback_query = update.callback_query
                chat_id = callback_query.message.chat.id
                callback_data = callback_query.data

                print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")
                bot.answer_callback_query(callback_query.id) # Remove o "carregando" do botão

                # Se o callback_data for um ID de FAQ, tentar responder com ele
                if callback_data in faq_data:
                    response_text = faq_data[callback_data].get('resposta')
                    bot.send_message(chat_id, response_text, parse_mode='Markdown')
                    print(f"----> Resposta da Callback Query enviada com sucesso para o chat {chat_id}.")
                else:
                    bot.send_message(chat_id, "Opção de botão não reconhecida ou FAQ não encontrado.", parse_mode='Markdown')
                    print(f"----> ERRO: FAQ ID '{callback_data}' não encontrado para Callback Query.")
                
            else:
                print("----> Update recebido sem as chaves 'message' ou 'callback_query'.")

        except Exception as e:
            print(f"ERRO INESPERADO no processamento do webhook: {e}")
            print(traceback.format_exc()) # Imprime o stack trace completo do erro

        print("Update processado. Retornando 200 OK.")
        return 'OK', 200
    else:
        return 'Método não permitido', 405

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
