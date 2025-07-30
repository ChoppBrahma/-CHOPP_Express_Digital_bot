import os
import json
from flask import Flask, request, jsonify
import telebot # Importe a biblioteca telebot

app = Flask(__name__)

# Configura o token do seu bot Telegram
# Certifique-se de que BOT_TOKEN está definido como uma variável de ambiente no Render
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    # Considere sair ou levantar uma exceção aqui se o token for crítico para o funcionamento
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Variável global para armazenar o FAQ
faq_data = {}

def load_faq():
    global faq_data
    try:
        # Certifique-se de que 'faq.json' está no mesmo diretório do seu main.py
        with open('faq.json', 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        print(f"FAQ carregado com sucesso! Tamanho do FAQ carregado: {len(faq_data)} entradas.")
    except FileNotFoundError:
        print("Erro: Arquivo faq.json não encontrado.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: {e}")
    except Exception as e:
        print(f"Erro inesperado ao carregar FAQ: {e}")

# Carrega o FAQ ao iniciar a aplicação
load_faq()

# Função para encontrar resposta no FAQ
def find_faq_answer(message_text):
    message_text_lower = message_text.lower()
    for entry_id, entry_data in faq_data.items():
        keywords = [kw.lower() for kw in entry_data.get('palavras_chave', [])]
        for keyword in keywords:
            if keyword in message_text_lower:
                return entry_data.get('resposta', "Desculpe, não encontrei uma resposta para isso no FAQ.")
    return "Desculpe, não entendi sua pergunta. Poderia reformular ou perguntar de outra forma?"

@app.route('/')
def health_check():
    print("Requisição GET recebida no / (Health Check)")
    return "Bot está funcionando!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update_json = request.get_json()
        print(f"Requisição POST recebida no /webhook")
        # print(f"JSON recebido: {json.dumps(update_json, indent=2)}") # Log completo do JSON (pode ser grande)

        try:
            # Tenta extrair a mensagem do JSON
            if 'message' in update_json:
                message = telebot.types.Update.de_json(json.dumps(update_json)).message
                chat_id = message.chat.id
                text = message.text

                # --- NOVO LOG: MENSAGEM RECEBIDA ---
                print(f"----> Mensagem recebida do chat {chat_id}: '{text}'")

                if text:
                    # Encontra a resposta no FAQ
                    response_text = find_faq_answer(text)

                    # --- NOVO LOG: RESPOSTA ENCONTRADA ---
                    print(f"----> Resposta encontrada no FAQ: '{response_text}'")

                    # Envia a resposta de volta para o Telegram
                    try:
                        bot.send_message(chat_id, response_text)
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        # Isso pode acontecer se o token estiver errado, chat_id inválido, etc.
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")
            else:
                print("----> Update recebido sem a chave 'message'. Pode ser outro tipo de atualização (ex: callback_query, edited_message).")

        except Exception as e:
            print(f"ERRO INESPERADO no processamento do webhook: {e}")
            # print(f"Erro detalhe: {traceback.format_exc()}") # Importar traceback no início para usar

        print("Update processado. Retornando 200 OK.")
        return 'OK', 200
    else:
        return 'Método não permitido', 405

if __name__ == '__main__':
    # No Render, a porta é definida pela variável de ambiente PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
