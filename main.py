import os
import telebot
from flask import Flask, request

# Pega o token do bot das variáveis de ambiente do Render
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Inicializa o bot
bot = telebot.TeleBot(BOT_TOKEN)

# Inicializa o Flask para o webhook
app = Flask(__name__)

# Este é o manipulador de mensagens simples
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Eu sou seu bot de teste simples. Envie qualquer mensagem para mim!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Recebi sua mensagem: " + message.text)

# Rota para o webhook do Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '!', 200 # Resposta HTTP 200 OK para o Telegram
    else:
        # Se não for JSON, é um pedido inválido
        return 'Tipo de conteúdo incorreto!', 403

# Rota de 'health check' simples para verificar se o app está online
@app.route('/')
def index():
    return 'Bot está online!', 200

# Executa o aplicativo Flask
if __name__ == '__main__':
    # Obtém a porta do ambiente Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
