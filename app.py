import streamlit as st
from langchain.chat_models import ChatOpenAI
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Funções utilitárias
def load_profile():
    with open("profile.json") as f:
        return json.load(f)

def load_tasks():
    try:
        with open("tasks.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def tarefas_do_dia(tasks, data_hoje):
    return [t for t in tasks if t["data"] == data_hoje]

# UI Streamlit
st.set_page_config(page_title="Assistente Pessoal IA")
st.title("Assistente Pessoal IA")

# Carregar dados
profile = load_profile()
tasks = load_tasks()
data_hoje = datetime.now().strftime("%Y-%m-%d")
tarefas_hoje = tarefas_do_dia(tasks, data_hoje)

# Aba lateral para cadastro de tarefas
st.sidebar.header("Cadastrar nova tarefa")
with st.sidebar.form("form_tarefa", clear_on_submit=True):
    data = st.date_input("Data", value=datetime.now()).strftime("%Y-%m-%d")
    hora = st.time_input("Hora", value=datetime.now().time()).strftime("%H:%M")
    descricao = st.text_input("Descrição")
    submitted = st.form_submit_button("Adicionar")
    if submitted and descricao.strip():
        nova_tarefa = {"data": data, "hora": hora, "descricao": descricao}
        tasks.append(nova_tarefa)
        save_tasks(tasks)
        st.success("Tarefa adicionada com sucesso! Atualize a página.")

# Exibir tarefas do dia
st.subheader(f"Tarefas do dia {data_hoje}:")
if tarefas_hoje:
    for t in tarefas_hoje:
        st.write(f"- {t['hora']} - {t['descricao']}")
else:
    st.write("Nenhuma tarefa para hoje.")

# Chat com assistente
st.subheader("Assistente IA")
user_input = st.text_input("Como posso te ajudar? (Ex: Quais são minhas tarefas? Escreva um e-mail...)")
if user_input:
    contexto = f"""
    Você é um assistente pessoal para {profile['nome']}, {profile['profissao']}.
    Dados pessoais: {json.dumps(profile, ensure_ascii=False)}
    Tarefas do dia ({data_hoje}): {json.dumps(tarefas_hoje, ensure_ascii=False)}
    Quando for pedido um e-mail, gere um texto em formato de e-mail no tom {profile['preferencias']['tom_email']} e em {profile['preferencias']['linguagem']}.
    Seja direto e eficiente, respondendo sempre com base nesses dados.
    Pergunta/comando do usuário: {user_input}
    """
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
    resposta = llm.invoke(contexto)
    st.write(resposta.content)
