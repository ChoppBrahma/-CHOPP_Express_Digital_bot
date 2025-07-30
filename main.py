import os
import json
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import traceback
import re
from unidecode import unidecode

app = Flask(__name__)

# --- Configuração do Token do Bot ---
# O BOT_TOKEN é uma variável de ambiente, o que é mais seguro para credenciais.
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERRO: Variável de ambiente BOT_TOKEN não definida.")
    # Se o token não estiver definido, o bot não pode funcionar.
    # Em um ambiente de produção, isso seria um erro grave.
    exit(1) # Sair do programa.

bot = telebot.TeleBot(BOT_TOKEN)

# --- Variável Global para o FAQ ---
# Isso armazena as perguntas e respostas carregadas do faq.json.
faq_data = {}

# --- Função para Carregar o FAQ ---
# Tenta carregar o arquivo faq.json quando o bot inicia.
def load_faq():
    global faq_data # Indica que estamos modificando a variável global
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            # Carrega o JSON. Chaves são convertidas para string para garantir compatibilidade
            # com o callback_data dos botões do Telegram, que são strings.
            raw_faq = json.load(f)
            faq_data = {str(k): v for k, v in raw_faq.items()}
        print(f"FAQ carregado com sucesso! Total de {len(faq_data)} entradas.")
    except FileNotFoundError:
        print("Erro crítico: Arquivo faq.json não encontrado. Certifique-se de que ele está na mesma pasta do main.py.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do faq.json: Verifique a sintaxe do arquivo. Erro: {e}")
    except Exception as e:
        print(f"Erro inesperado ao carregar FAQ: {e}")

# --- Carrega o FAQ ao iniciar a aplicação ---
load_faq()

# --- Função para Normalizar Texto ---
# Remove acentos e converte para minúsculas para facilitar a comparação
# e tornar a busca menos sensível a erros de digitação e variações.
def normalize_text(text):
    if not isinstance(text, str): # Garante que o input é uma string
        return ""
    return unidecode(text).lower()

# --- Função para Encontrar a Melhor FAQ ---
# Procura a FAQ mais relevante com base na pergunta do usuário.
def find_faq_answer(query):
    normalized_query = normalize_text(query)
    best_match_id = None
    max_score = 0
    found_by_direct_keyword = False # Flag para indicar correspondência forte

    # Prioridade 1: Busca por correspondência exata de palavras-chave
    # Isso dá peso maior para termos específicos que o usuário pode estar procurando.
    for faq_id, faq in faq_data.items():
        normalized_keywords = [normalize_text(kw) for kw in faq.get('palavras_chave', [])]
        for kw in normalized_keywords:
            # re.search busca a palavra-chave inteira, não apenas substrings.
            # r'\b' garante que a correspondência é de palavra inteira (word boundary)
            if re.search(r'\b' + re.escape(kw) + r'\b', normalized_query):
                best_match_id = faq_id
                found_by_direct_keyword = True
                break # Encontrou uma correspondência forte, pode parar de buscar.
        if found_by_direct_keyword:
            break
    
    if found_by_direct_keyword:
        return best_match_id, found_by_direct_keyword

    # Prioridade 2: Busca por palavras na pergunta da FAQ
    # Se nenhuma palavra-chave direta foi encontrada, tenta por palavras que aparecem nas perguntas das FAQs.
    for faq_id, faq in faq_data.items():
        normalized_pergunta = normalize_text(faq.get('pergunta', ''))
        score = 0
        query_words = normalized_query.split() # Divide a query do usuário em palavras individuais.
        
        for word in query_words:
            # Pontua cada palavra da query que é encontrada na pergunta da FAQ.
            if word and word in normalized_pergunta: # 'word' não pode ser vazia
                score += 1

        if score > max_score: # Se encontrou uma FAQ com mais palavras correspondentes, atualiza.
            max_score = score
            best_match_id = faq_id

    return best_match_id, found_by_direct_keyword # Retorna o ID e a flag.

# --- Função para Gerar Botões de Perguntas Relacionadas ---
# Cria botões interativos para o usuário explorar tópicos relacionados.
def get_related_buttons(query, primary_faq_id=None, max_buttons=5):
    normalized_query = normalize_text(query)
    related_faqs_candidates = []
    seen_ids = set() # Para evitar duplicar FAQs ou sugerir a principal novamente.

    if primary_faq_id:
        seen_ids.add(primary_faq_id) # Não sugerir a FAQ que acabou de ser respondida.

    # Itera sobre todas as FAQs para encontrar aquelas que são relevantes à query original.
    for faq_id, faq in faq_data.items():
        if faq_id in seen_ids: # Pula IDs já processados ou a FAQ principal.
            continue

        normalized_keywords = [normalize_text(kw) for kw in faq.get('palavras_chave', [])]
        normalized_pergunta = normalize_text(faq.get('pergunta', ''))
        
        is_relevant = False
        
        #
