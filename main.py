import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback
from fuzzywuzzy import fuzz # Para encontrar similaridades no FAQ
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton # Para botões

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
        # print("DEBUG: Primeiras entradas do FAQ carregadas:", list(faq_data.items())[:2]) # Opcional para depuração
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
    if not faq_data:
        print("DEBUG: FAQ data não carregado em find_faq_answer.")
        return None, None

    normalized_query = query.lower()
    best_match_id = None
    best_score = 0
    # Limiar para considerar uma correspondência boa o suficiente (0-100)
    MATCH_THRESHOLD = 75 

    print(f"DEBUG: Processando query '{query}' (normalizada: '{normalized_query}') na busca principal.")

    for faq_id, entry in faq_data.items():
        keywords = [k.lower() for k in entry.get('palavras_chave', [])]
        
        for keyword in keywords:
            # Prioriza correspondência exata da palavra-chave
            if keyword == normalized_query:
                print(f"DEBUG: Correspondência EXATA de keyword! FAQ ID: {faq_id}, Keyword: '{keyword}'")
                return entry.get('resposta'), faq_id
            
            # Calcula e compara os scores de similaridade
            score_ratio = fuzz.ratio(normalized_query, keyword)
            score_partial_ratio = fuzz.partial_ratio(normalized_query, keyword)
            score_token_sort = fuzz.token_sort_ratio(normalized_query, keyword)
            
            # Pega o melhor score entre as diferentes métricas de fuzzy
            current_best_for_keyword = max(score_ratio, score_partial_ratio, score_token_sort)
            
            # print(f"  DEBUG Scores para FAQ ID {faq_id} - Keyword '{keyword}': Ratio={score_ratio}, Partial={score_partial_ratio}, TokenSort={score_token_sort}")

            if current_best_for_keyword > best_score:
                best_score = current_best_for_keyword
                best_match_id = faq_id

    print(f"DEBUG: Melhor correspondência principal encontrada: ID {best_match_id} com score {best_score} (Threshold: {MATCH_THRESHOLD})")

    if best_score >= MATCH_THRESHOLD and best_match_id:
        return faq_data[best_match_id].get('resposta'), best_match_id
    
    print(f"DEBUG: Nenhuma correspondência boa encontrada na busca principal (score {best_score} abaixo do threshold {MATCH_THRESHOLD} ou sem ID).")
    return None, None

# --- Nova função para encontrar e gerar botões de perguntas relacionadas ---
def get_related_buttons(query, primary_faq_id=None, max_buttons=3):
    related_buttons = []
    normalized_query = query.lower()
    
    # Um limiar um pouco menor para sugerir tópicos relacionados
    RELATED_THRESHOLD = 60 

    print(f"DEBUG: Buscando botões relacionados para query '{query}', excluindo ID '{primary_faq_id}'.")

    for faq_id, entry in faq_data.items():
        # Ignora a pergunta principal que já foi respondida
        if faq_id == primary_faq_id: 
            continue

        keywords = [k.lower() for k in entry.get('palavras_chave', [])]
        pergunta_text = entry.get('pergunta', '').lower() # Também considera a pergunta em si

        is_related = False
        # Verifica se alguma palavra-chave ou a pergunta em si tem relação forte com a query
        for keyword in keywords + [pergunta_text]: # Combina palavras-chave e pergunta para busca
            if not keyword: continue # Pula palavras-chave vazias
            
            # Usa token_set_ratio, bom para encontrar palavras em comum em frases
            if fuzz.token_set_ratio(normalized_query, keyword) >= RELATED_THRESHOLD:
                is_related = True
                break
        
        if is_related:
            # Garante que não adiciona a mesma pergunta duas vezes se por acaso ela aparecer por keywords diferentes
            if (faq_id, entry.get('pergunta')) not in related_buttons:
                related_buttons.append((faq_id, entry.get('pergunta')))
        
        # Limita o número de botões para não sobrecarregar
        if len(related_buttons) >= max_buttons: 
            break

    if related_buttons:
        markup = InlineKeyboardMarkup()
        for faq_id, pergunta in related_buttons:
            # O callback_data deve ser uma string e geralmente é o ID do FAQ
            markup.add(InlineKeyboardButton(pergunta, callback_data=str(faq_id))) 
        print(f"DEBUG: Botões relacionados gerados: {len(related_buttons)}.")
        return markup
    print("DEBUG: Nenhum botão relacionado encontrado.")
    return None # Nenhum botão relacionado encontrado

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
                markup = None # Inicializa markup como None para cada nova mensagem

                if text:
                    # Tenta encontrar no FAQ a melhor correspondência
                    faq_answer, faq_id_matched = find_faq_answer(text)

                    if faq_answer:
                        response_text = faq_answer
                        print(f"----> Resposta principal encontrada no FAQ (ID: {faq_id_matched}): '{response_text}'")
                        
                        # Gera botões de perguntas relacionadas, excluindo a que já foi respondida
                        markup = get_related_buttons(text, faq_id_matched)
                        
                    else:
                        response_text = "Desculpe, não consegui encontrar uma resposta para sua pergunta no meu FAQ. Por favor, tente perguntar de outra forma ou consulte nosso site oficial."
                        print(f"----> Nenhuma resposta principal encontrada no FAQ para: '{text}'. Enviando fallback genérico.")
                        # Não há botões para a resposta de fallback genérico
                    
                    try:
                        # Envia a mensagem com ou sem botões (se markup for None, não envia)
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        if "Can't parse message text" in str(e):
                            print("DICA: Texto pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                            bot.send_message(chat_id, response_text, parse_mode=None, reply_markup=markup) # Tenta enviar sem Markdown
                        else:
                            pass
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

            elif update.callback_query:
                # Esta seção é acionada por cliques em botões inline
                callback_query = update.callback_query
                chat_id = callback_query.message.chat.id
                callback_data = callback_query.data # O ID do FAQ que o botão representa

                print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")
                bot.answer_callback_query(callback_query.id) # Remove o "carregando" do botão

                try:
                    # Busca a resposta para o ID do FAQ do botão clicado
                    if callback_data in faq_data:
                        response_text = faq_data[callback_data].get('resposta')
                        # Ao clicar em um botão, geralmente não enviamos mais botões aqui,
                        # mas você pode adicionar essa lógica se quiser "navegação" aninhada.
                        # Exemplo: markup = get_related_buttons(faq_data[callback_data].get('pergunta'), callback_data)
                        bot.send_message(chat_id, response_text, parse_mode='Markdown')
                        print(f"----> Resposta da Callback Query enviada com sucesso para o o chat {chat_id}.")
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
