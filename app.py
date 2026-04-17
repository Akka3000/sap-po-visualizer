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

# --- DATA FÖR GRAF ---
data = [
    dict(Fas="1. Aktuell månad", Start=denna_manad_start, Slut=denna_manad_start + relativedelta(months=1), 
         Status="Pågående"),
    dict(Fas="2. PO-Horisont (Bindande)", Start=denna_manad_start, Slut=horisont_slut, 
         Status="Låst tid"),
    dict(Fas="3. Fysiskt flöde", Start=produktion_start, Slut=horisont_slut, 
         Status="Produktion")
]

df = pd.DataFrame(data)

# --- FIGUR ---
fig = px.timeline(df, x_start="Start", x_end="Slut", y="Fas", color="Status",
                 color_discrete_map={
                     "Pågående": "rgba(150, 150, 150, 0.3)", 
                     "Låst tid": "#FF4B4B",
                     "Produktion": "#0068C9"
                 })

# Fixa X-axeln för ren månadslogik
fig.update_xaxes(
    dtick="M1", 
    tickformat="%b %Y", 
    ticklabelmode="period",
    showgrid=True
)

fig.update_yaxes(autorange="reversed")
fig.update_layout(showlegend=True, height=400)

st.plotly_chart(fig, use_container_width=True)

# --- RENARE INFO-BOXAR ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total horisont", f"{horisont_manader} månader")
    st.write(f"Börjar: **{denna_manad_start.strftime('%Y-%m-%d')}**")

with col2:
    st.metric("Fysisk tid", f"{fysisk_ledtid_dagar} dagar")
    st.write(f"Produktionsstart: **{produktion_start.strftime('%Y-%m-%d')}**")

with col3:
    gap = totala_dagar_horisont - fysisk_ledtid_dagar
    st.metric("Administrativ låsning", f"{gap} dagar")
    st.write(f"Leverans: **{horisont_slut.strftime('%Y-%m-%d')}**")
