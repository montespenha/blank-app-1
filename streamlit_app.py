import streamlit as st
import datetime
import pandas as pd
import requests

st.set_page_config(page_title="Alerta Trader", page_icon="⏰", layout="centered")

# --- CONFIGURAÇÕES DE ENVIOS (PREENCHA AQUI) ---
# Telegram: Crie seu bot no @BotFather para conseguir o Token e use o @userinfobot para ver seu Chat ID
TELEGRAM_TOKEN = st.sidebar.text_input("Token do Telegram Bot", type="password")
TELEGRAM_CHAT_ID = st.sidebar.text_input("Seu Chat ID do Telegram")

# WhatsApp: Pegue suas chaves de teste gratuitas no site da Twilio
TWILIO_SID = st.sidebar.text_input("Twilio Account SID", type="password")
TWILIO_AUTH_TOKEN = st.sidebar.text_input("Twilio Auth Token", type="password")
SEU_CELULAR_WHATSAPP = st.sidebar.text_input("Seu Celular (Ex: +5521999999999)")

def enviar_telegram(mensagem):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            pass

def enviar_whatsapp(mensagem):
    if TWILIO_SID and TWILIO_AUTH_TOKEN and SEU_CELULAR_WHATSAPP:
        url = f"https://twilio.com{TWILIO_SID}/Messages.json"
        # O número "from" é o número padrão do Sandbox de testes da Twilio
        payload = {
            "From": "whatsapp:+14155238886",
            "To": f"whatsapp:{SEU_CELULAR_WHATSAPP}",
            "Body": mensagem
        }
        try:
            requests.post(url, data=payload, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
        except Exception as e:
            pass

# --- FIM DA CONFIGURAÇÃO ---

# Configura o fuso horário de Brasília
diferenca_horas = datetime.timedelta(hours=-3)
fuso_br = datetime.timezone(diferenca_horas)
agora = datetime.datetime.now(fuso_br)

st.title("⏰ Alerta de Aberturas e Notícias")
st.write(f"**Horário de Brasília:** {agora.strftime('%H:%M:%S')}")

# 1. MONITOR DE ABERTURAS
st.subheader("🏦 Status de Abertura")
status_euro = "🟢 ABERTO (Foco: EUR/USD)" if 4 <= agora.hour < 13 else "🔴 FECHADO"
status_ouro = "🟢 ABERTO (Foco: OURO)" if 9 <= agora.hour < 18 else "🔴 FECHADO"
status_asia = "🟢 ABERTO (Foco: USD/JPY)" if agora.hour >= 20 or agora.hour < 5 else "🔴 FECHADO"

st.markdown(f"**Europa (04:00):** {status_euro}")
st.markdown(f"**EUA (09:00):** {status_ouro}")
st.markdown(f"**Ásia (20:00):** {status_asia}")

# 2. CALENDÁRIO DE NOTÍCIAS DE ALTO IMPACTO
st.subheader("⚠️ Próximas Notícias de Alto Impacto")
dados_noticias = [
    {"Hora": "09:30", "Moeda": "USD", "Evento": "CPI (Inflação EUA)", "Impacto": "🔥 ALTO"},
    {"Hora": "11:00", "Moeda": "USD", "Evento": "Discurso do Fed", "Impacto": "🔥 ALTO"},
    {"Hora": "21:30", "Moeda": "AUD", "Evento": "Taxa de Desemprego", "Impacto": "🔥 ALTO"},
]

df = pd.DataFrame(dados_noticias)
st.dataframe(df, use_container_width=True)

# 3. SISTEMA DE ALERTA EXATO DE 2 MINUTOS COM DISPAROS
st.subheader("🔔 Avisos de Última Hora")
alerta_ativo = False

# Cria uma chave para não repetir o envio na mesma hora
if "ultima_noticia_enviada" not in st.session_state:
    st.session_state.ultima_noticia_enviada = ""

for noticia in dados_noticias:
    hora_noticia = datetime.datetime.strptime(noticia["Hora"], "%H:%M").time()
    dt_noticia = datetime.datetime.combine(agora.date(), hora_noticia, tzinfo=fuso_br)
    diferenca = dt_noticia - agora
    minutos_restantes = diferenca.total_seconds() / 60
    
    if 0 <= minutos_restantes <= 2:
        texto_alerta = f"🚨 ALERTA TRADER: Faltam 2 minutos para {noticia['Evento']} ({noticia['Moeda']}) às {noticia['Hora']}!"
        st.error(texto_alerta)
        alerta_ativo = True
        
        # Envia apenas uma vez para o celular
        if st.session_state.ultima_noticia_enviada != noticia["Evento"]:
            enviar_telegram(texto_alerta)
            enviar_whatsapp(texto_alerta)
            st.session_state.ultima_noticia_enviada = noticia["Evento"]

if not alerta_ativo:
    st.success("✅ Mercado sob controle nos próximos 2 minutos.")
