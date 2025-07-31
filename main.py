import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Importações NLTK e Scikit-learn ---
import nltk
# O download das stopwords e do rslp será feito no Render Build Command.
# Apenas a importação das classes é necessária aqui.
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer # Para português
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Configurações do Bot Telegram ---
app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    exit(1)
bot = telebot.TeleBot(BOT_TOKEN)

# Variável de ambiente para o ID do chat do administrador (para comandos de admin)
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
if not ADMIN_CHAT_ID:
    print("AVISO: Variável de ambiente ADMIN_CHAT_ID não definida. Comando /recarregarfaq não funcionará para administradores.")

# --- Variáveis globais para armazenar o FAQ e componentes de PLN ---
faq_data = {}
tfidf_vectorizer = None
faq_vectors = None
faq_ids_indexed = [] # Para mapear de volta do índice do vetorizador para o FAQ ID

# --- Inicializar Stemmer e Stop Words ---
# REMOVEMOS os blocos try/except nltk.downloader.DownloadError
# pois o download já é garantido no Build Command do Render.
# Se o recurso não for encontrado aqui, é um problema de ambiente no Render.
try:
    nltk.data.find('corpora/stopwords')
    print("Dados do NLTK: stopwords encontrados.")
except LookupError:
    print("ERRO: Stopwords do NLTK não encontradas após o build. Verifique o comando de build do Render.")
    exit(1) # Força o encerramento se os dados essenciais não estiverem presentes

try:
    nltk.data.find('stemmers/rslp')
    print("Dados do NLTK: rslp (stemmer para português) encontrados.")
except LookupError:
    print("ERRO: Stemmer RSLP do NLTK não encontrado após o build. Verifique o comando de build do Render.")
    exit(1) # Força o encerramento se os dados essenciais não estiverem presentes


stemmer = RSLPStemmer()
stop_words = set(stopwords.words('portuguese'))

# --- Função de Pré-processamento de Texto ---
def preprocess_text(text):
    """
    Normaliza o texto: minúsculas, remove stopwords e aplica stemming.
    """
    if not text:
        return ""
    text = str(text).lower().strip() # Garante que é string
    words = [stemmer.stem(word) for word in text.split() if word not in stop_words and len(word) > 1] # Ignorar palavras de 1 letra
    return " ".join(words)

# --- Função para Carregar e Vetorizar o FAQ ---
def load_faq():
    global faq_data, tfidf_vectorizer, faq_vectors, faq_ids_indexed
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            raw_faq = json.load(f)
            faq_data = {str(k): v for k, v in raw_faq.items()}

        if not faq_data:
            print("FAQ vazio ou não carregado. Não é possível vetorizar.")
            tfidf_vectorizer = None
            faq_vectors = None
            faq_ids_indexed = []
            return

        # Preparar textos para o vetorizador TF-IDF
        texts_to_vectorize = []
        faq_ids_indexed = []
        for faq_id, entry in faq_data.items():
            # Combine a pergunta e as palavras-chave para criar o "documento" do FAQ
            # Adicione um espaço extra para garantir que as palavras não se unam se uma estiver vazia
            combined_text = entry.get('pergunta', '') + " " + " ".join(entry.get('palavras_chave', []))
            texts_to_vectorize.append(preprocess_text(combined_text))
            faq_ids_indexed.append(faq_id)

        # Inicializar e treinar o vetorizador TF-IDF
        # fit_transform() treina o vocabulário e transforma os textos
        tfidf_vectorizer = TfidfVectorizer()
        faq_vectors = tfidf_vectorizer.fit_transform(texts_to_vectorize)
        
        print(f"FAQ carregado e vetorizado com sucesso! Tamanho do FAQ: {len(faq_data)} entradas.")
    except FileNotFoundError:
        print("Erro: Arquivo faq.json não encontrado. O bot NÃO poderá responder via FAQ.")
        faq_data = {}
        tfidf_vectorizer = None
        faq_vectors = None
        faq_ids_indexed = []
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: {e}. Verifique a sintaxe do arquivo.")
        faq_data = {}
        tfidf_vectorizer = None
        faq_vectors = None
        faq_ids_indexed = []
    except Exception as e:
        print(f"Erro inesperado ao carregar ou vetorizar o FAQ: {e}")
        traceback.print_exc()
        faq_data = {}
        tfidf_vectorizer = None
        faq_vectors = None
        faq_ids_indexed = []

# Chama a função para carregar o FAQ quando o bot inicia
load_faq()

# --- NOVA Função para encontrar a melhor correspondência no FAQ (PLN AVANÇADO) ---
def find_faq_answer(query):
    """
    Encontra a melhor resposta do FAQ usando TF-IDF e similaridade de cosseno.
    Retorna a resposta do FAQ e o ID da pergunta correspondente.
    """
    if not faq_data or tfidf_vectorizer is None or faq_vectors is None:
        print("DEBUG: Componentes PLN não carregados em find_faq_answer. Retornando None.")
        return None, None

    processed_query = preprocess_text(query)
    if not processed_query: # Se a query for apenas stop words ou muito curta após pré-processamento
        print("DEBUG: Query vazia após pré-processamento. Retornando None.")
        return None, None

    try:
        # Transforma a query do usuário em um vetor TF-IDF usando o vocabulário aprendido
        query_vector = tfidf_vectorizer.transform([processed_query])
    except ValueError as e:
        # Isso pode acontecer se a query tiver palavras que não estão no vocabulário do TF-IDF
        print(f"DEBUG: Erro ao transformar query: {e}. Provavelmente query sem vocabulário conhecido.")
        return None, None
            
    # Calcula a similaridade de cosseno entre a query e todos os itens do FAQ
    similarities = cosine_similarity(query_vector, faq_vectors).flatten()

    # Encontra o item do FAQ com a maior similaridade
    best_match_index = similarities.argmax()
    best_similarity = similarities[best_match_index]

    # Define um limiar de similaridade. AJUSTE ESTE VALOR CONFORME TESTES!
    # Um valor entre 0.35 e 0.50 é um bom ponto de partida para similaridade de cosseno com TF-IDF.
    MIN_SIMILARITY_THRESHOLD = 0.35 

    print(f"DEBUG: Melhor similaridade encontrada: {best_similarity:.4f}")

    if best_similarity >= MIN_SIMILARITY_THRESHOLD:
        best_faq_id = faq_ids_indexed[best_match_index]
        print(f"DEBUG: Correspondência encontrada com similaridade {best_similarity:.4f} para ID: {best_faq_id}")
        return faq_data[best_faq_id].get('resposta'), best_faq_id
    
    print(f"DEBUG: Nenhuma correspondência boa encontrada (similaridade {best_similarity:.4f} abaixo do limiar {MIN_SIMILARITY_THRESHOLD}).")
    return None, None

# --- Função para encontrar e gerar botões de perguntas relacionadas ---
def get_related_buttons(query, primary_faq_id=None, max_buttons=5):
    """
    Gera botões para perguntas relacionadas, evitando a pergunta principal.
    A lógica de busca de relacionados ainda pode ser aprimorada com PLN mais avançado no futuro.
    """
    related_buttons_info = [] # Lista de tuplas (faq_id, pergunta_texto)
    
    # Pré-processa a query para usar na busca de relacionados, tornando-a mais robusta
    processed_query_for_related = preprocess_text(query)
    query_words = processed_query_for_related.split()

    # Um limiar simples para considerar uma pergunta relacionada
    # Pode ser ajustado ou substituído por similaridade de cosseno no futuro
    RELATED_KEYWORD_MATCH_THRESHOLD = 1 

    print(f"DEBUG: Buscando botões relacionados para query '{query}', excluindo ID '{primary_faq_id}'.")

    for faq_id, entry in faq_data.items():
        if faq_id == primary_faq_id: 
            continue # Não adicionar a própria pergunta que já foi a resposta principal

        # Combine o texto da pergunta e as palavras-chave da entrada do FAQ
        # e pré-processe para comparação
        entry_text = entry.get('pergunta', '') + " " + " ".join(entry.get('palavras_chave', []))
        processed_entry_text = preprocess_text(entry_text)
        entry_words = processed_entry_text.split()

        current_related_hits = 0
        for q_word in query_words:
            if q_word in entry_words:
                current_related_hits += 1
        
        # Considera a pergunta relacionada se houver um número mínimo de correspondências de palavras
        if current_related_hits >= RELATED_KEYWORD_MATCH_THRESHOLD:
            # Evita duplicatas adicionando apenas se a combinação (id, pergunta) não estiver na lista
            if (faq_id, entry.get('pergunta')) not in related_buttons_info:
                related_buttons_info.append((faq_id, entry.get('pergunta')))
        
        if len(related_buttons_info) >= max_buttons: 
            break # Limita o número de botões

    if related_buttons_info:
        markup = InlineKeyboardMarkup()
        for faq_id, pergunta in related_buttons_info:
            # Truncar perguntas longas para caber no botão
            button_text = pergunta[:50] + '...' if len(pergunta) > 53 else pergunta
            markup.add(InlineKeyboardButton(button_text, callback_data=str(faq_id))) 
        print(f"DEBUG: Botões relacionados gerados: {len(related_buttons_info)}.")
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

                # --- NOVO: Tratamento do comando de recarregar FAQ ---
                if text == '/recarregarfaq':
                    if ADMIN_CHAT_ID and str(chat_id) == ADMIN_CHAT_ID:
                        bot.send_message(chat_id, "Iniciando recarregamento do FAQ. Isso pode levar alguns segundos...")
                        load_faq() # Chama a função que já temos para recarregar e vetorizar
                        if faq_data:
                            bot.send_message(chat_id, f"FAQ recarregado com sucesso! {len(faq_data)} entradas.")
                        else:
                            bot.send_message(chat_id, "Erro ao recarregar FAQ. Verifique os logs do servidor.")
                        return 'OK', 200 # Encerra o processamento do update para este comando
                    else:
                        bot.send_message(chat_id, "Você não tem permissão para usar este comando.")
                        return 'OK', 200 # Encerra o processamento do update
                # --- Fim do novo tratamento de comando ---

                response_text = ""
                markup = None 

                if text:
                    faq_answer, faq_id_matched = find_faq_answer(text) # Agora usa a nova função de PLN

                    if faq_answer:
                        response_text = faq_answer
                        print(f"----> Resposta principal encontrada no FAQ (ID: {faq_id_matched}): '{response_text}'")
                        markup = get_related_buttons(text, faq_id_matched)
                        
                    else:
                        response_text = "Desculpe, não consegui encontrar uma resposta precisa para sua pergunta no meu FAQ. Por favor, tente perguntar de outra forma ou consulte nosso site oficial."
                        print(f"----> Nenhuma resposta principal encontrada no FAQ para: '{text}'. Enviando fallback genérico.")
                    
                    try:
                        # Considerar usar parse_mode='HTML' se tiver formatações mais complexas no FAQ
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        if "Can't parse message text" in str(e) or "Bad Request: can't parse entities" in str(e):
                            print("DICA: Texto pode ter Markdown inválido. Tentando enviar sem parse_mode...")
                            bot.send_message(chat_id, response_text, parse_mode=None, reply_markup=markup) 
                        else:
                            pass # Re-raise se for outro tipo de erro que não seja de parsing
                    except Exception as e:
                        print(f"ERRO geral ao enviar mensagem: {e}")
                else:
                    print(f"----> Mensagem recebida sem texto (ex: foto, sticker). Ignorando por enquanto.")

            elif update.callback_query:
                callback_query = update.callback_query
                chat_id = callback_query.message.chat.id
                callback_data = callback_query.data 

                print(f"----> Callback Query recebida do chat {chat_id}: '{callback_data}'")
                bot.answer_callback_query(callback_query.id) # Avisa o Telegram que a query foi recebida

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
