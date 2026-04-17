import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="PO-Horisont med Dagsvisning", layout="wide")

st.title("📅 Detaljerad PO-Horisont")
st.write("Här kan du se exakt vilka dagar som täcks av din horisont.")

# --- INPUTS ---
st.sidebar.header("Inställningar")
horisont_manader = st.sidebar.number_input("Bindande horisont (Månader)", min_value=1, max_value=24, value=7)
idag = st.sidebar.date_input("Simulera dagens datum", date.today())
fysisk_ledtid_dagar = st.sidebar.number_input("Faktisk fysisk ledtid (Dagar)", min_value=1, max_value=500, value=70)

# --- BERÄKNINGAR ---
denna_manad_start = idag.replace(day=1)
# Vi räknar ut exakt slutdatum baserat på månader
horisont_slut = denna_manad_start + relativedelta(months=horisont_manader)
produktion_start = horisont_slut - relativedelta(days=fysisk_ledtid_dagar)
totala_dagar_horisont = (horisont_slut - denna_manad_start).days

# --- DATA FÖR GRAF ---
data = [
    dict(Fas="1. Aktuell månad", Start=denna_manad_start, Slut=denna_manad_start + relativedelta(months=1), 
         Status="Pågående", Beskrivning="Här är vi nu"),
    dict(Fas="2. PO-Horisont (Låst)", Start=denna_manad_start, Slut=horisont_slut, 
         Status="Bindande", Beskrivning=f"Totalt låst: {totala_dagar_horisont} dagar"),
    dict(Fas="3. Fysisk Produktion", Start=produktion_start, Slut=horisont_slut, 
         Status="Produktion", Beskrivning=f"Produktionstid: {fysisk_ledtid_dagar} dagar")
]

df = pd.DataFrame(data)

# --- FIGUR ---
fig = px.timeline(df, x_start="Start", x_end="Slut", y="Fas", color="Status",
                 hover_data=["Beskrivning"],
                 color_discrete_map={
                     "Pågående": "rgba(150, 150, 150, 0.3)", 
                     "Bindande": "#FF4B4B",
                     "Produktion": "#0068C9"
                 })

# --- FIXA AXELN FÖR DAGAR OCH MÅNADER ---
fig.update_xaxes(
    dtick="M1",              # En markering per månad
    tickformat="%d %b\n%Y",  # Visar "Dag Månad År" (t.ex. 01 Jan 2026)
    ticklabelmode="period",
    showgrid=True,           # Visa linjer
    gridwidth=1,
    gridcolor='LightGrey'
)

# Lägg till finare linjer för veckor (valfritt men snyggt)
fig.update_xaxes(minor=dict(dtick=7*24*60*60*1000, showgrid=True, gridcolor='WhiteSmoke'))

fig.update_yaxes(autorange="reversed")
fig.update_layout(showlegend=True, height=500)

st.plotly_chart(fig, use_container_width=True)

# --- INFO BOXAR ---
st.markdown(f"### Detaljer för din ordermatta")
col1, col2 = st.columns(2)

# Vi säkerställer att vi visar datumen snyggt oavsett format
start_str = denna_manad_start.strftime('%Y-%m-%d')
slut_str = horisont_slut.strftime('%Y-%m-%d')
prod_start_str = produktion_start.strftime('%Y-%m-%d')

with col1:
    st.info(f"**Startdatum (Beställning):** {start_str}")
    st.info(f"**Slutdatum (Leverans):** {slut_str}")
with col2:
    st.success(f"**Produktionen startar:** {prod_start_str}")
    st.warning(f"**Dagar i 'Vänteläge':** {totala_dagar_horisont - fysisk_ledtid_dagar} dagar")
