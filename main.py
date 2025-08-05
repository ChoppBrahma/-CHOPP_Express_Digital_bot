import os
import json
from flask import Flask, request, jsonify
import telebot
import traceback
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Importações NLTK e Scikit-learn ---
import nltk
# AQUI ESTÁ A NOVA LINHA DE AJUSTE PARA O NLTK DATA PATH
# Usamos os.path.join para construir um caminho absoluto robusto
nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
nltk.data.path.append(nltk_data_dir) # <--- LINHA AJUSTADA

# Certifique-se de que o diretório existe (para desenvolvimento local, no Render o download criará)
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir, exist_ok=True)
    print(f"DEBUG: Criado diretório para NLTK_DATA em: {nltk_data_dir}") # Apenas para debug

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
WELCOME_KEYWORDS = set() # NOVO: Para palavras-chave de boas-vindas

# --- Inicializar Stemmer e Stop Words ---
try:
    nltk.data.find('corpora/stopwords')
    print("Dados do NLTK: stopwords encontrados.")
except LookupError:
    print("ERRO: Stopwords do NLTK não encontradas. Verifique o comando de build do Render e o NLTK_DATA path.")
    exit(1)

try:
    nltk.data.find('stemmers/rslp')
    print("Dados do NLTK: rslp (stemmer para português) encontrados.")
except LookupError:
    print("ERRO: Stemmer RSLP do NLTK não encontrado. Verifique o comando de build do Render e o NLTK_DATA path.")
    exit(1)

stemmer = RSLPStemmer()
stop_words = set(stopwords.words('portuguese'))

# --- Função de Pré-processamento de Texto ---
def preprocess_text(text):
    """
    Normaliza o texto: minúsculas, remove stopwords e aplica stemming.
    """
    if not text:
        return ""
    text = str(text).lower().strip()
    words = [stemmer.stem(word) for word in text.split() if word not in stop_words and len(word) > 1]
    return " ".join(words)

# --- Função para Carregar e Vetorizar o FAQ ---
def load_faq():
    global faq_data, tfidf_vectorizer, faq_vectors, faq_ids_indexed, WELCOME_KEYWORDS
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            raw_faq = json.load(f)
            faq_data = {str(k): v for k, v in raw_faq.items()}

        if not faq_data:
            print("FAQ vazio ou não carregado. Não é possível vetorizar.")
            tfidf_vectorizer = None
            faq_vectors = None
            faq_ids_indexed = []
            WELCOME_KEYWORDS = set()
            return

        texts_to_vectorize = []
        faq_ids_indexed = []
        for faq_id, entry in faq_data.items():
            # Combine a pergunta e as palavras-chave para criar o "documento" do FAQ
            combined_text = entry.get('pergunta', '') + " " + " ".join(entry.get('palavras_chave', []))
            texts_to_vectorize.append(preprocess_text(combined_text))
            faq_ids_indexed.append(faq_id)

        tfidf_vectorizer = TfidfVectorizer()
        faq_vectors = tfidf_vectorizer.fit_transform(texts_to_vectorize)
        
        # NOVO: Carregar palavras-chave de boas-vindas para tratamento isolado
        WELCOME_KEYWORDS = set()
        if '1' in faq_data: # Verifica se o FAQ ID '1' (boas-vindas) existe
            for kw in faq_data['1'].get('palavras_chave', []):
                WELCOME_KEYWORDS.add(kw.lower()) # Adiciona em minúsculas para comparação direta
        print(f"FAQ carregado e vetorizado com sucesso! Tamanho do FAQ: {len(faq_data)} entradas.")
        print(f"Palavras-chave de boas-vindas carregadas: {WELCOME_KEYWORDS}")

    except FileNotFoundError:
        print("Erro: Arquivo faq.json não encontrado. O bot NÃO poderá responder via FAQ.")
        faq_data = {}
        tfidf_vectorizer = None
        faq_vectors = None
        faq_ids_indexed = []
        WELCOME_KEYWORDS = set()
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: {e}. Verifique a sintaxe do arquivo.")
        faq_data = {}
        tfidf_vectorizer = None
        faq_vectors = None
        faq_ids_indexed = []
        WELCOME_KEYWORDS = set()
    except Exception as e:
        print(f"Erro inesperado ao carregar ou vetorizar o FAQ: {e}")
        traceback.print_exc()
        faq_data = {}
        tfidf_vectorizer = None
        faq_vectors = None
        faq_ids_indexed = []
        WELCOME_KEYWORDS = set()

# Chama a função para carregar o FAQ quando o bot inicia
load_faq()

# --- Função para encontrar a melhor correspondência no FAQ (PLN AVANÇADO) ---
def find_faq_answer(query):
    """
    Primeiro tenta encontrar correspondência exata nas palavras-chave.
    Se não encontrar, busca por similaridade com TF-IDF + cosseno.
    """
    if not faq_data or tfidf_vectorizer is None or faq_vectors is None:
        print("DEBUG: Componentes PLN não carregados em find_faq_answer. Retornando None.")
        return None, None

    entrada = query.strip().lower()

    # 🔍 1️⃣ Verificação direta nas palavras-chave
    for faq_id, entry in faq_data.items():
        for palavra in entry.get("palavras_chave", []):
            if entrada == palavra.lower():
                print(f"DEBUG: Match direto nas palavras-chave para entrada '{entrada}' no ID {faq_id}")
                return entry.get("resposta"), faq_id

    # 🧠 2️⃣ Similaridade TF-IDF
    processed_query = preprocess_text(query)
    if not processed_query:
        print("DEBUG: Query vazia após pré-processamento. Retornando None.")
        return None, None

    try:
        query_vector = tfidf_vectorizer.transform([processed_query])
    except ValueError as e:
        print(f"DEBUG: Erro ao transformar query: {e}. Provavelmente query sem vocabulário conhecido.")
        return None, None
            
    similarities = cosine_similarity(query_vector, faq_vectors).flatten()

    best_match_index = similarities.argmax()
    best_similarity = similarities[best_match_index]

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
    """
    related_buttons_info = []
    
    processed_query_for_related = preprocess_text(query)
    query_words = processed_query_for_related.split()

    RELATED_KEYWORD_MATCH_THRESHOLD = 1 

    print(f"DEBUG: Buscando botões relacionados para query '{query}', excluindo ID '{primary_faq_id}'.")

    for faq_id, entry in faq_data.items():
        if faq_id == primary_faq_id: 
            continue

        entry_text = entry.get('pergunta', '') + " " + " ".join(entry.get('palavras_chave', []))
        processed_entry_text = preprocess_text(entry_text)
        entry_words = processed_entry_text.split()

        current_related_hits = 0
        for q_word in query_words:
            if q_word in entry_words:
                current_related_hits += 1
        
        if current_related_hits >= RELATED_KEYWORD_MATCH_THRESHOLD:
            if (faq_id, entry.get('pergunta')) not in related_buttons_info:
                related_buttons_info.append((faq_id, entry.get('pergunta')))
        
        if len(related_buttons_info) >= max_buttons: 
            break

    if related_buttons_info:
        markup = InlineKeyboardMarkup()
        for faq_id, pergunta in related_buttons_info:
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

                # --- Tratamento do comando de recarregar FAQ ---
                if text == '/recarregarfaq':
                    if ADMIN_CHAT_ID and str(chat_id) == ADMIN_CHAT_ID:
                        bot.send_message(chat_id, "Iniciando recarregamento do FAQ. Isso pode levar alguns segundos...")
                        load_faq()
                        if faq_data:
                            bot.send_message(chat_id, f"FAQ recarregado com sucesso! {len(faq_data)} entradas.")
                        else:
                            bot.send_message(chat_id, "Erro ao recarregar FAQ. Verifique os logs do servidor.")
                        return 'OK', 200
                    else:
                        bot.send_message(chat_id, "Você não tem permissão para usar este comando.")
                        return 'OK', 200

                response_text = ""
                markup = None 

                if text:
                    # --- PONTO CHAVE 1: Tratamento especial e isolado para mensagens de boas-vindas (ID 1) ---
                    # Verifica se o texto (em minúsculas) corresponde a uma das palavras-chave de boas-vindas
                    # Este é o "pulo do gato" para garantir que saudações sejam respondidas corretamente.
                    if text.lower() in WELCOME_KEYWORDS and '1' in faq_data:
                        response_text = faq_data['1']['resposta']
                        print(f"----> Resposta de Boas-vindas (ID 1) acionada diretamente para: '{text}'")
                    # --- Fim do tratamento especial para ID 1 ---
                    else:
                        # Processamento normal do FAQ para outras perguntas via PLN
                        faq_answer, faq_id_matched = find_faq_answer(text)

                        if faq_answer:
                            response_text = faq_answer
                            print(f"----> Resposta principal encontrada no FAQ (ID: {faq_id_matched}): '{response_text}'")
                            markup = get_related_buttons(text, faq_id_matched)
                            
                        else:
                            # --- PONTO CHAVE 2: Tratamento especial e isolado para respostas não encontradas (ID 2) ---
                            # Este é o fallback que entra em ação quando o bot não encontra nenhuma outra correspondência.
                            if '2' in faq_data:
                                response_text = faq_data['2']['resposta']
                                print(f"----> Nenhuma resposta principal encontrada. Usando Fallback ID 2 para: '{text}'.")
                            else:
                                # Fallback genérico padrão se o ID 2 não estiver presente no faq.json
                                response_text = "Desculpe, não consegui encontrar uma resposta precisa para sua pergunta no meu FAQ. Por favor, tente perguntar de outra forma ou consulte nosso site oficial."
                                print(f"----> Nenhuma resposta principal encontrada e ID 2 ausente. Enviando fallback genérico padrão para: '{text}'.")
                    # --- Fim do tratamento especial para ID 2 ---
                    
                    try:
                        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='Markdown')
                        print(f"----> Mensagem enviada com sucesso para o chat {chat_id}.")
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"ERRO Telegram API ao enviar mensagem: {e}")
                        if "Can't parse message text" in str(e) or "Bad Request: can't parse entities" in str(e):
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
