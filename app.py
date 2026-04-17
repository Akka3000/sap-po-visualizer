import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="PO-Horisont", layout="wide")

st.title("🔄 PO-Horisont: Månadsöversikt")

# --- INPUTS ---
st.sidebar.header("Inställningar")
horisont_manader = st.sidebar.number_input("Bindande horisont (Månader)", min_value=1, max_value=24, value=7)
idag = st.sidebar.date_input("Simulera dagens datum", date.today())
fysisk_ledtid_dagar = st.sidebar.number_input("Faktisk fysisk ledtid (Dagar)", min_value=1, max_value=500, value=70)

# --- BERÄKNINGAR ---
denna_manad_start = idag.replace(day=1)
horisont_slut = denna_manad_start + relativedelta(months=horisont_manader)
produktion_start = horisont_slut - relativedelta(days=fysisk_ledtid_dagar)
totala_dagar_horisont = (horisont_slut - denna_manad_start).days

# Skapa en textsträng för månadsnummer (t.ex. "1  2  3  4  5  6  7")
manads_nummer_str = "    ".join([str(i+1) for i in range(horisont_manader)])

# --- DATA FÖR GRAF ---
data = [
    dict(Fas="1. Aktuell månad", Start=denna_manad_start, Slut=denna_manad_start + relativedelta(months=1), 
         Status="Pågående", Text="Nu"),
    dict(Fas="2. PO-Horisont (Bindande)", Start=denna_manad_start, Slut=horisont_slut, 
         Status="Låst tid", Text=manads_nummer_str),
    dict(Fas="3. Fysiskt flöde", Start=produktion_start, Slut=horisont_slut, 
         Status="Produktion", Text="Produktion")
]

df = pd.DataFrame(data)

# --- TEXT UNDER RUBRIK ---
st.markdown(f"### {horisont_manader} månader motsvarar ca **{totala_dagar_horisont} dagar**")

# --- FIGUR ---
fig = px.timeline(df, x_start="Start", x_end="Slut", y="Fas", color="Status",
                 text="Text", 
                 color_discrete_map={
                     "Pågående": "rgba(150, 150, 150, 0.3)", 
                     "Låst tid": "#FF4B4B",
                     "Produktion": "#0068C9"
                 })

# Fixa X-axeln
fig.update_xaxes(
    dtick="M1", 
    tickformat="%b %Y", 
    ticklabelmode="period",
    showgrid=True
)

# Centrera månadsnumren inuti staplarna
fig.update_traces(textposition='inside', insidetextanchor='middle', textfont_size=16)
fig.update_yaxes(autorange="reversed")
fig.update_layout(showlegend=False, height=400)

st.plotly_chart(fig, use_container_width=True)

# --- INFO-BOXAR ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total horisont", f"{horisont_manader} mån")
    st.write(f"Totalt antal dagar: **{totala_dagar_horisont}**")

with col2:
    st.metric("Fysisk ledtid", f"{fysisk_ledtid_dagar} dgr")
    st.write(f"Produktionsmånader: **{round(fysisk_ledtid_dagar/30, 1)} st**")

with col3:
    gap_dagar = totala_dagar_horisont - fysisk_ledtid_dagar
    st.metric("Leverantörens frihet", f"{gap_dagar} dgr")
    st.write(f"Tid utan produktion: **{gap_dagar} dagar**")
