import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback
import google.generativeai as genai # Importar para usar a API do Gemini

app = Flask(__name__)

# --- Configurações do Bot Telegram ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    exit(1)
bot = telebot.TeleBot(BOT_TOKEN)

# --- Configurações da IA (Gemini) ---
# Você precisará obter esta chave de API do Google AI Studio
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("ERRO: Variável de ambiente GEMINI_API_KEY não definida. A IA não funcionará.")
    # Exit, ou você pode configurar um fallback para uma resposta padrão
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
# Escolha o modelo que deseja usar. 'gemini-pro' é um bom ponto de partida.
model = genai.GenerativeModel('gemini-pro')

# Contexto inicial (System Instruction) para guiar a IA
# Adapte este texto para descrever o "papel" do seu bot
SYSTEM_INSTRUCTION = (
    "Você é um assistente virtual amigável e prestativo da Chopp Brahma Express. "
    "Seu objetivo é responder a perguntas sobre produtos (chope, equipamentos), "
    "serviços (entrega, instalação), promoções (Choppback), e como fazer pedidos. "
    "Mantenha as respostas concisas, diretas e sempre no tom da marca Chopp Brahma Express. "
    "Se não souber a resposta, diga que não pode ajudar no momento e sugira consultar o site oficial."
)

# --- Função para interagir com o modelo de IA ---
def get_ai_response(user_message):
    try:
        # Usamos o SYSTEM_INSTRUCTION no prompt para guiar a IA
        prompt = f"{SYSTEM_INSTRUCTION}\n\nUsuário: {user_message}\nAssistente:"
        
        # Gera a resposta usando o modelo de IA
        response = model.generate_content(prompt)
        
        # Retorna o texto da resposta. Pode ser necessário tratamento de erro se 'text' não existir.
        return response.text
    except Exception as e:
        print(f"ERRO ao chamar a API da IA: {e}")
        print(traceback.format_exc())
        return "Desculpe, estou com dificuldades para me conectar com a inteligência artificial no momento. Por favor, tente novamente mais tarde."

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

            # --- Lida apenas com mensagens de texto (para um bot mais enxuto) ---
            if update.message:
                message = update.message
                chat_id = message.chat.id
                text = message.text

                print(f"----> Mensagem recebida do chat {chat_id}: '{text}'")

                if text:
                    # Obter resposta da IA
                    response_text = get_ai_response(text)
                    
                    print(f"----> Resposta gerada pela IA: '{response_text}'")

                    # Para um bot enxuto, não vamos ter botões dinâmicos por padrão.
                    # Se você quiser um botão fixo (ex: "Menu Principal"), pode adicioná-lo aqui.
                    markup = None 
                    # Exemplo de um botão fixo, se desejar:
                    # markup = telebot.types.InlineKeyboardMarkup()
                    # markup.add(telebot.types.InlineKeyboardButton("Voltar ao Início", callback_data="start_menu"))

                    try:
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        # Caso a IA retorne texto com formatação markdown inválida, tentar sem parse_mode
                        if "Can't parse message text" in str(e):
                            print("DICA: Texto da IA pode ter Markdown inválido. Tentando enviar sem Markdown...")
                            bot.send_message(chat_id, response_text, parse_mode=None)
                        else:
                            pass
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

            # --- Lida com cliques nos botões Inline (Callback Query) ---
            # Se você não usar botões dinâmicos, essa parte será acionada apenas
            # por botões fixos (como o "start_menu" de exemplo acima).
            elif update.callback_query:
                callback_query = update.callback_query
                chat_id = callback_query.message.chat.id
                callback_data = callback_query.data

                print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")
                bot.answer_callback_query(callback_query.id) # Remove o "carregando" do botão

                if callback_data == "start_menu":
                    response_text = get_ai_response("Olá, preciso de ajuda com o menu principal.") # Pode ser uma saudação padrão
                    bot.send_message(chat_id, response_text, parse_mode='Markdown')
                else:
                    bot.send_message(chat_id, "Opção de botão não reconhecida.", parse_mode='Markdown')
                
                print(f"----> Resposta da Callback Query enviada para o chat {chat_id}.")

            else:
                print("----> Update recebido sem as chaves 'message' ou 'callback_query'.")

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
