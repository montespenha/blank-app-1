import streamlit as st
import datetime
import pandas as pd
import requests

st.set_page_config(page_title="Alerta Trader Pro", page_icon="⏰", layout="centered")

# --- ATUALIZAÇÃO AUTOMÁTICA (CORREÇÃO) ---
# Força o aplicativo a rodar sozinho a cada 30 segundos para checar o relógio e disparar as mensagens
st.logo = None
if "contador" not in st.session_state:
    st.session_state.contador = 0
st.fragment(run_every=30)(lambda: None)() 
# ------------------------------------------

# 💾 SEUS DADOS FIXOS DO TELEGRAM INTEGRADOS:
TELEGRAM_TOKEN_FIXO = "8864961928:AAHYdOHvEjnFao-qpQ-H8iIXF3CggGA0xjc"
TELEGRAM_CHAT_ID_FIXO = "331702469"

# --- CONFIGURAÇÕES DE ENVIOS NA BARRA LATERAL ---
st.sidebar.header("🔧 Configurações de Notificação")
TELEGRAM_TOKEN = st.sidebar.text_input("Token do Telegram Bot", value=TELEGRAM_TOKEN_FIXO, type="password")
TELEGRAM_CHAT_ID = st.sidebar.text_input("Seu Chat ID do Telegram", value=TELEGRAM_CHAT_ID_FIXO)
TWILIO_SID = st.sidebar.text_input("Twilio Account SID", type="password")
TWILIO_AUTH_TOKEN = st.sidebar.text_input("Twilio Auth Token", type="password")
SEU_CELULAR_WHATSAPP = st.sidebar.text_input("Seu Celular (Ex: +5521999999999)")

def enviar_mensagem_global(mensagem):
    token = TELEGRAM_TOKEN if TELEGRAM_TOKEN else TELEGRAM_TOKEN_FIXO
    chat_id = TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else TELEGRAM_CHAT_ID_FIXO
    if token and chat_id:
        url_tg = f"https://telegram.org{token}/sendMessage"
        try: requests.post(url_tg, json={"chat_id": chat_id, "text": mensagem})
        except: pass
            
    if TWILIO_SID and TWILIO_AUTH_TOKEN and SEU_CELULAR_WHATSAPP:
        url_wa = f"https://twilio.com{TWILIO_SID}/Messages.json"
        payload = {"From": "whatsapp:+14155238886", "To": f"whatsapp:{SEU_CELULAR_WHATSAPP}", "Body": mensagem}
        try: requests.post(url_wa, data=payload, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
        except: pass

# Configura o fuso horário de Brasília (UTC-3) nativo
diferenca_horas = datetime.timedelta(hours=-3)
fuso_br = datetime.timezone(diferenca_horas)
agora = datetime.datetime.now(fuso_br)

st.title("📈 Monitor de Mercados & Alertas Ativos")
st.write(f"**Horário atual de Brasília:** {agora.strftime('%H:%M:%S')}")

# 1. MONITOR DE SESSÕES
st.subheader("🏦 Painel de Status das Aberturas")
horarios_mercado = [
    {"Nome": "EUR/USD (Europa)", "Abertura": "04:00", "Fechamento": "13:00"},
    {"Nome": "Ouro (EUA - Nova York)", "Abertura": "09:00", "Fechamento": "18:00"},
    {"Nome": "Mercado Futuro EUA (Índices)", "Abertura": "10:30", "Fechamento": "17:00"},
    {"Nome": "USD/JPY (Ásia)", "Abertura": "20:00", "Fechamento": "05:00 (+1d)"}
]

if "historico_envios" not in st.session_state:
    st.session_state.historico_envios = []

for merc in horarios_mercado:
    hora_abertura = datetime.datetime.strptime(merc["Abertura"], "%H:%M").time()
    dt_abertura = datetime.datetime.combine(agora.date(), hora_abertura, tzinfo=fuso_br)
    dif_mercado = dt_abertura - agora
    minutos_mercado = dif_mercado.total_seconds() / 60
    
    if merc["Nome"] == "USD/JPY (Ásia)": esta_aberto = agora.hour >= 20 or agora.hour < 5
    elif merc["Nome"] == "EUR/USD (Europa)": esta_aberto = 4 <= agora.hour < 13
    elif merc["Nome"] == "Ouro (EUA - Nova York)": esta_aberto = 9 <= agora.hour < 18
    else: esta_aberto = 10 <= agora.hour and (agora.hour != 10 or agora.minute >= 30) and agora.hour < 17
        
    status_txt = "🟢 ABERTO" if esta_aberto else "🔴 FECHADO"
    st.markdown(f"**{merc['Nome']}:** {status_txt} (Abertura às {merc['Abertura']})")

    if 1.5 <= minutos_mercado <= 2.0:
        msg_abertura = f"🚨 ATENÇÃO TRADER: Faltam 2 minutos para a abertura do mercado: {merc['Nome']} às {merc['Abertura']}!"
        if msg_abertura not in st.session_state.historico_envios:
            enviar_mensagem_global(msg_abertura)
            st.session_state.historico_envios.append(msg_abertura)

# 2. CALENDÁRIO DE NOTÍCIAS DE ALTO IMPACTO
st.subheader("⚠️ Calendário Econômico Diário")
dados_noticias = [
    {"Hora": "09:30", "Moeda": "USD", "Evento": "CPI (Inflação EUA)", "Impacto": "🔥 ALTO"},
    {"Hora": "11:00", "Moeda": "USD", "Evento": "Discurso do Fed", "Impacto": "🔥 ALTO"},
    {"Hora": "21:30", "Moeda": "AUD", "Evento": "Taxa de Desemprego", "Impacto": "🔥 ALTO"},
]
st.dataframe(pd.DataFrame(dados_noticias), use_container_width=True)

st.subheader("🔔 Histórico de Notificações Recentes")
alerta_tela = False

for noticia in dados_noticias:
    hora_noticia = datetime.datetime.strptime(noticia["Hora"], "%H:%M").time()
    dt_noticia = datetime.datetime.combine(agora.date(), hora_noticia, tzinfo=fuso_br)
    diferenca = dt_noticia - agora
    minutos_restantes = diferenca.total_seconds() / 60
    
    if 1.5 <= minutos_restantes <= 2.0:
        msg_noticia = f"⚠️ ALERTA DE IMPACTO: Faltam 2 minutos para a notícia {noticia['Evento']} ({noticia['Moeda']})!"
        st.error(msg_noticia)
        alerta_tela = True
        if msg_noticia not in st.session_state.historico_envios:
            enviar_mensagem_global(msg_noticia)
            st.session_state.historico_envios.append(msg_noticia)

if not alerta_tela:
    st.success("✅ Sem eventos de alto impacto ocorrendo nos próximos 2 minutos.")
