import streamlit as st
import datetime
import pytz
import pandas as pd

st.set_page_config(page_title="Alerta Trader", page_icon="⏰", layout="centered")

# Configura o fuso horário de Brasília
fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.datetime.now(fuso_br)

st.title("⏰ Alerta de Aberturas e Notícias")
st.write(f"**Horário de Brasília:** {agora.strftime('%H:%M:%S')}")

# 1. MONITOR DE ABERTURAS (Horários de Verão Atuais - Junho de 2026)
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
