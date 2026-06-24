import streamlit as st
import datetime
import pandas as pd

st.set_page_config(page_title="Alerta Trader", page_icon="⏰", layout="centered")

# Configura o fuso horário de Brasília (UTC-3)
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
    {"Hora": "21:30", "Moeda": "AUD", "Evento": "Taxa de Desemplego", "Impacto": "🔥 ALTO"},
]

df = pd.DataFrame(dados_noticias)
st.dataframe(df, use_container_width=True)

# 3. SISTEMA DE ALERTA EXATO DE 2 MINUTOS
st.subheader("🔔 Avisos de Última Hora")
alerta_ativo = False

for noticia in dados_noticias:
    # Converte o horário da notícia para comparação
    hora_noticia = datetime.datetime.strptime(noticia["Hora"], "%H:%M").time()
    
    # Calcula a diferença exata em minutos para o dia de hoje
    dt_noticia = datetime.datetime.combine(agora.date(), hora_noticia, tzinfo=fuso_br)
    diferenca = dt_noticia - agora
    minutos_restantes = diferenca.total_seconds() / 60
    
    # Ativa o aviso se faltar entre 0 e 2 minutos para o evento ocorrer
    if 0 <= minutos_restantes <= 2:
        st.error(f"🚨 **ALERTA MÁXIMO:** Faltam menos de 2 minutos para a notícia: **{noticia['Evento']} ({noticia['Moeda']})** às {noticia['Hora']}!")
        alerta_ativo = True

if not alerta_ativo:
    st.success("✅ Nenhuma notícia de alto impacto nos próximos 2 minutos. Mercado sob controle.")
