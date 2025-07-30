import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback # Importar para logs de erro mais detalhados

app = Flask(__name__)

# Configura o token do seu bot Telegram
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    exit(1) # Sair se o token não estiver configurado, pois o bot não funcionará

bot = telebot.TeleBot(BOT_TOKEN)

# Variável global para armazenar o FAQ
faq_data = {}

def load_faq():
    global faq_data
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            # Garante que as chaves do dicionário FAQ sejam strings para corresponder ao callback_data
            raw_faq = json.load(f)
            faq_data = {str(k): v for k, v in raw_faq.items()} # Converte IDs para string chaves
        print(f"FAQ carregado com sucesso! Tamanho do FAQ carregado: {len(faq_data)} entradas.")
        # Opcional: imprimir um snippet para depuração inicial
        # for k, v in list(faq_data.items())[:3]: # Imprime as primeiras 3 entradas
        #     print(f"  ID: {k}, Pergunta: {v.get('pergunta')}")
    except FileNotFoundError:
        print("Erro: Arquivo faq.json não encontrado.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: {e}")
    except Exception as e:
        print(f"Erro inesperado ao carregar FAQ: {e}")

# Carrega o FAQ ao iniciar a aplicação
load_faq()

# --- NOVO: Mapeamento de palavras-chave para botões relacionados ---
# AJUSTE ESTE DICIONÁRIO COM OS IDs CORRETOS DO SEU FAQ.JSON!
# 'text': é o texto que aparece no botão
# 'faq_id': é o ID da pergunta no seu faq.json que será enviada quando o botão for clicado
RELATED_BUTTONS_MAP = {
    # Botões para quando o bot cumprimenta ou não entende (pode ser o mesmo conjunto)
    "boas_vindas_ou_nao_entendi": [
        {"text": "Quantos litros de chope?", "faq_id": "2"},  # ID da pergunta sobre litros
        {"text": "Horários de entrega?", "faq_id": "3"},    # ID da pergunta sobre entrega
        {"text": "Preços e promoções?", "faq_id": "4"},     # ID da pergunta sobre preços
        {"text": "Lojas e regiões?", "faq_id": "6"},       # ID da pergunta sobre lojas
        {"text": "Como pedir?", "faq_id": "5"}             # ID da pergunta sobre como pedir
    ],
    # Botões específicos para quando a palavra-chave "chopp" é encontrada
    "chopp": [
        {"text": "Quantos litros de chope?", "faq_id": "2"},
        {"text": "Promoções de chope?", "faq_id": "4"},
        {"text": "Tipos de chope?", "faq_id": "7"},         # Exemplo: Adicione um FAQ ID para tipos de chope se tiver
        {"text": "Como pedir meu chope?", "faq_id": "5"}
    ],
    # Adicione mais mapeamentos conforme necessário para outras palavras-chave
    # "entrega": [
    #    {"text": "Horário de entrega?", "faq_id": "3"},
    #    {"text": "Regiões de atendimento?", "faq_id": "6"}
    # ],
}


# Função para encontrar resposta no FAQ e botões relacionados
def find_faq_answer(message_text):
    message_text_lower = message_text.lower()
    found_answer = None
    matched_keyword = None # Para identificar qual palavra-chave disparou a correspondência

    # Primeiro, verifica se a mensagem é um comando de início ou uma saudação
    if message_text_lower == "/start" or any(kw in message_text_lower for kw in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        # Tenta encontrar a resposta de boas-vindas no FAQ (assumindo ID "1" para isso)
        if "1" in faq_data:
            found_answer = faq_data["1"].get('resposta')
        matched_keyword = "boas_vindas_ou_nao_entendi" # Usa esta chave para buscar botões
    else:
        # Busca no FAQ por palavra-chave
        for entry_id, entry_data in faq_data.items():
            keywords = [kw.lower() for kw in entry_data.get('palavras_chave', [])]
            for keyword in keywords:
                if keyword in message_text_lower:
                    found_answer = entry_data.get('resposta')
                    matched_keyword = keyword # Usa a palavra-chave encontrada para buscar botões
                    break
            if found_answer:
                break

    # Se uma resposta específica foi encontrada no FAQ
    if found_answer:
        # Verifica se há botões relacionados para a palavra-chave que disparou a resposta
        # Usa o 'matched_keyword' para buscar no RELATED_BUTTONS_MAP
        buttons_to_send = RELATED_BUTTONS_MAP.get(matched_keyword, [])
        return found_answer, buttons_to_send
    else:
        # Resposta padrão se nenhuma correspondência específica for encontrada
        default_response = "Desculpe, não entendi sua pergunta. Poderia reformular ou perguntar de outra forma?"
        # Oferece botões gerais para o cenário de "não entendi"
        buttons_to_send = RELATED_BUTTONS_MAP.get("boas_vindas_ou_nao_entendi", [])
        return default_response, buttons_to_send

@app.route('/')
def health_check():
    print("Requisição GET recebida no / (Health Check)")
    return "Bot está funcionando!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update_json = request.get_json()
        # print(f"JSON recebido: {json.dumps(update_json, indent=2)}") # Log completo do JSON (muito detalhado)
        print("Requisição POST recebida em /webhook")

        try:
            update = telebot.types.Update.de_json(json.dumps(update_json))

            # --- Lida com mensagens de texto ---
            if update.message:
                message = update.message
                chat_id = message.chat.id
                text = message.text

                print(f"----> Mensagem recebida do chat {chat_id}: '{text}'")

                if text:
                    # Encontra a resposta no FAQ e os botões relacionados
                    response_text, related_buttons = find_faq_answer(text)

                    print(f"----> Resposta encontrada no FAQ: '{response_text}'")
                    print(f"----> Botões relacionados para enviar: {related_buttons}")

                    # Cria o teclado Inline (botões) se houver botões relacionados
                    markup = None
                    if related_buttons:
                        markup = telebot.types.InlineKeyboardMarkup()
                        for btn_info in related_buttons:
                            # O callback_data deve ser uma string. Usamos o FAQ ID.
                            markup.add(telebot.types.InlineKeyboardButton(btn_info['text'], callback_data=str(btn_info['faq_id'])))

                    # Envia a mensagem com a resposta e os botões (se existirem)
                    try:
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        if "Can't parse message text" in str(e):
                            print("DICA: Verifique se há caracteres Markdown não escapados na sua resposta.")
                            bot.send_message(chat_id, response_text.replace("_", "\\_").replace("*", "\\*"), parse_mode=None) # Tenta enviar sem Markdown
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

            # --- Lida com cliques nos botões Inline (Callback Query) ---
            elif update.callback_query:
                callback_query = update.callback_query
                chat_id = callback_query.message.chat.id
                callback_data = callback_query.data # Este é o FAQ ID que definimos para o botão

                print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")

                # Responde à callback query para remover o "carregando" do botão no Telegram
                bot.answer_callback_query(callback_query.id)

                # Encontra a resposta correspondente ao callback_data (FAQ ID)
                try:
                    faq_entry = faq_data.get(callback_data) # faq_data tem chaves como strings agora
                    if faq_entry:
                        response_text = faq_entry.get('resposta', "Resposta não encontrada para este ID de FAQ.")
                        # Quando responde a um clique de botão, geralmente não envia mais botões,
                        # mas você pode chamar find_faq_answer novamente para botões aninhados se quiser.
                        # Por simplicidade, envia apenas a resposta do FAQ clicado.
                        bot.send_message(chat_id, response_text, parse_mode='Markdown')
                        print(f"----> Resposta da Callback Query enviada com sucesso para o chat {chat_id}.")
                    else:
                        bot.send_message(chat_id, "Desculpe, não encontrei a informação solicitada pelo botão.", parse_mode='Markdown')
                        print(f"----> ERRO: FAQ ID '{callback_data}' não encontrado para Callback Query.")
                except Exception as e:
                    print(f"ERRO ao processar Callback Query para FAQ ID {callback_data}: {e}")
                    print(traceback.format_exc()) # Imprime o stack trace completo do erro

            else:
                print("----> Update recebido sem as chaves 'message' ou 'callback_query'. Pode ser outro tipo de atualização (edited_message, channel_post, etc.).")

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
