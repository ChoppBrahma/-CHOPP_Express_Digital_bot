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

# --- ISTO É CRÍTICO! VOCÊ DEVE AJUSTAR ESTE DICIONÁRIO COM OS IDs E PALAVRAS-CHAVE REAIS DO SEU FAQ.JSON. ---
# Cada CHAVE (ex: "boas_vindas_ou_nao_entendi", "chopp", "entrega", "como pedir")
# deve ser uma palavra-chave OU um identificador lógico (como "boas_vindas_ou_nao_entendi")
# que você quer que dispare um conjunto ESPECÍFICO de botões.
#
# 'text': É o texto que APARECE no botão no Telegram.
# 'faq_id': É o ID EXATO (como string) de uma entrada NO SEU FAQ.JSON que será usada
#           para buscar a resposta quando esse botão for clicado.
RELATED_BUTTONS_MAP = {
    # Cenário 1: Boas-vindas ou quando o bot não entende a pergunta.
    # As palavras-chave "oi", "olá", "/start", etc., ou a ausência de correspondência,
    # cairão aqui.
    "boas_vindas_ou_nao_entendi": [
        {"text": "Quantos litros de chope?", "faq_id": "2"},  # EX: Supondo ID "2" para essa pergunta no seu faq.json
        {"text": "Horários de entrega?", "faq_id": "3"},    # EX: Supondo ID "3" para Horários de entrega
        {"text": "Preços e promoções?", "faq_id": "4"},     # EX: Supondo ID "4" para Preços e promoções
        {"text": "Lojas e regiões?", "faq_id": "6"},       # EX: Supondo ID "6" para Lojas e regiões
        {"text": "Como pedir?", "faq_id": "5"}             # EX: Supondo ID "5" para Como pedir
    ],
    # Cenário 2: Quando a palavra-chave "chopp" é detectada na mensagem do usuário.
    # A chave "chopp" AQUI deve ser uma das 'palavras_chave' que você tem em alguma entrada do seu faq.json.
    "chopp": [
        {"text": "Quantos litros de chope?", "faq_id": "2"}, # Reutiliza FAQ ID 2
        {"text": "Promoções de chope?", "faq_id": "4"},     # Reutiliza FAQ ID 4
        {"text": "Tipos de chope?", "faq_id": "7"},         # EX: Supondo que FAQ ID "7" é sobre "Tipos de Chope"
        {"text": "Como pedir meu chope?", "faq_id": "5"}    # Reutiliza FAQ ID 5
    ],
    # --- VOCÊ DEVE ADICIONAR MAIS ENTRADAS AQUI PARA PERSONALIZAR OS BOTÕES ---
    # EX: Cenário 3: Quando a palavra-chave "como pedir" ou "pedido" é detectada.
    # A CHAVE "como pedir" AQUI deve ser uma das 'palavras_chave' que você tem em alguma entrada do seu faq.json
    # que leve à resposta de como pedir.
    "como pedir": [
        {"text": "Dados para cadastro", "faq_id": "5"},     # FAQ ID da própria pergunta de "como pedir"
        {"text": "Formas de pagamento", "faq_id": "10"},    # EX: Supondo que FAQ ID "10" é para "Formas de Pagamento"
        {"text": "Horários de entrega", "faq_id": "3"},     # FAQ ID para Horários de entrega
        {"text": "Áreas de atendimento", "faq_id": "6"}     # FAQ ID para Lojas e regiões
    ],
    # EX: Cenário 4: Quando a palavra-chave "entrega" é detectada.
    # A CHAVE "entrega" AQUI deve ser uma das 'palavras_chave' que você tem em alguma entrada do seu faq.json
    # que leve à resposta sobre entregas.
    "entrega": [
        {"text": "Verificar horários de entrega", "faq_id": "3"}, # FAQ ID para Horários de entrega
        {"text": "Regiões atendidas", "faq_id": "6"},       # FAQ ID para Lojas e regiões
        {"text": "Status do meu pedido", "faq_id": "11"}    # EX: Supondo que FAQ ID "11" é sobre "Status do Pedido"
    ],
    # EX: Cenário 5: Quando a palavra-chave "preco" é detectada.
    # A CHAVE "preco" AQUI deve ser uma das 'palavras_chave' que você tem em alguma entrada do seu faq.json
    # que leve à resposta sobre preços/promoções.
    "preco": [
        {"text": "Promoções atuais", "faq_id": "4"},       # FAQ ID para Preços e promoções
        {"text": "Preço do barril de 50L", "faq_id": "12"}, # EX: Supondo que FAQ ID "12" é para "Preço do Barril de 50L"
        {"text": "Formas de pagamento", "faq_id": "10"}    # EX: Supondo que FAQ ID "10" é para "Formas de Pagamento"
    ],
    # ADICIONE MAIS CENÁRIOS CONFORME AS PALAVRAS-CHAVE DO SEU FAQ.JSON!
    # Lembre-se de que cada `faq_id` precisa existir no seu `faq.json`.
}


# Função para encontrar resposta no FAQ e botões relacionados
def find_faq_answer(message_text):
    message_text_lower = message_text.lower()
    found_answer = None
    matched_keyword_for_buttons = None # Para identificar qual palavra-chave deve disparar qual conjunto de botões

    # Primeiro, verifica se a mensagem é um comando de início ou uma saudação comum
    if message_text_lower == "/start" or any(kw in message_text_lower for kw in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        # Tenta encontrar a resposta de boas-vindas no FAQ (assumindo ID "1" para isso)
        if "1" in faq_data:
            found_answer = faq_data["1"].get('resposta')
        matched_keyword_for_buttons = "boas_vindas_ou_nao_entendi" # Usa esta chave para buscar botões padrão
    else:
        # Busca no FAQ por palavra-chave para encontrar a resposta principal
        # Prioriza a correspondência de palavras-chave mais longas para ser mais específico
        best_match_keyword = ""
        best_match_entry_id = None
        
        # Iterar sobre o FAQ para encontrar a melhor correspondência
        for entry_id, entry_data in faq_data.items():
            keywords = [kw.lower() for kw in entry_data.get('palavras_chave', [])]
            for keyword in keywords:
                # Verifica se a palavra-chave está na mensagem E se é uma correspondência mais longa/melhor
                if keyword in message_text_lower and len(keyword) > len(best_match_keyword):
                    best_match_keyword = keyword
                    best_match_entry_id = entry_id
                    # Não colocamos 'break' aqui para continuar procurando pela melhor (mais longa) correspondência
        
        if best_match_entry_id:
            found_answer = faq_data[best_match_entry_id].get('resposta')
            # A palavra-chave que será usada para o RELATED_BUTTONS_MAP deve ser a que melhor correspondeu
            matched_keyword_for_buttons = best_match_keyword


    # Se uma resposta principal foi encontrada no FAQ
    if found_answer:
        # Pega os botões relacionados usando a palavra-chave que disparou a resposta,
        # ou usa os botões padrão se não houver um mapeamento específico para essa palavra-chave.
        # Se matched_keyword_for_buttons for None (ex: se não encontrou nenhuma keyword no else branch),
        # get() retornará [] e o fallback será ativado.
        buttons_to_send = RELATED_BUTTONS_MAP.get(matched_keyword_for_buttons, [])
        
        # Se não encontrou botões específicos para a palavra-chave que ativou a resposta,
        # usa os botões padrão de "boas_vindas_ou_nao_entendi" como um fallback.
        # Isso garante que sempre haja opções, mesmo que o mapeamento para aquela palavra-chave específica esteja vazio ou ausente.
        if not buttons_to_send and matched_keyword_for_buttons != "boas_vindas_ou_nao_entendi": 
            buttons_to_send = RELATED_BUTTONS_MAP.get("boas_vindas_ou_nao_entendi", [])

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
                    if related_buttons: # Se related_buttons não for uma lista vazia
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
                        # Isso pode acontecer se houver problemas de formatação Markdown ou outros
                        if "Can't parse message text" in str(e):
                            print("DICA: Verifique se há caracteres Markdown não escapados na sua resposta. Tentando enviar sem Markdown...")
                            # Tenta enviar a mensagem sem Markdown se houver erro de parse
                            bot.send_message(chat_id, response_text, parse_mode=None)
                        else:
                            # Para outros erros de API do Telegram, simplesmente imprime o erro
                            pass # O erro já foi impresso acima
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
                        # Ao clicar em um botão, geralmente não enviamos mais botões aqui,
                        # mas você pode adicionar essa lógica se quiser "navegação" aninhada.
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
