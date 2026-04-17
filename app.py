import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="PO-Horisont Visualisering", layout="wide")

st.title("🔄 Rolling PO-Horizon & Ledtid")

# --- INPUTS ---
st.sidebar.header("Inställningar")
horisont_manader = st.sidebar.number_input("Bindande horisont (Månader)", min_value=1, max_value=24, value=7)
idag = st.sidebar.date_input("Simulera dagens datum", date.today())
fysisk_ledtid_dagar = st.sidebar.number_input("Faktisk fysisk ledtid (Dagar)", min_value=1, max_value=500, value=70)

# --- BERÄKNINGAR ---
denna_manad_start = idag.replace(day=1)
horisont_slut = denna_manad_start + relativedelta(months=horisont_manader)
produktion_start = horisont_slut - relativedelta(days=fysisk_ledtid_dagar)

# Beräkna totala dagar i horisonten för jämförelse
totala_dagar_horisont = (horisont_slut - denna_manad_start).days

# --- DATA FÖR GRAF ---
data = [
    dict(Fas="1. Aktuell månad", Start=denna_manad_start, Slut=denna_manad_start + relativedelta(months=1), 
         Status="Pågående", Beskrivning="Nuvarande period"),
    dict(Fas="2. PO-Horisont (Totalt)", Start=denna_manad_start, Slut=horisont_slut, 
         Status="Bindande", Beskrivning=f"Låst i {totala_dagar_horisont} dagar"),
    dict(Fas="3. Fysiskt flöde", Start=produktion_start, Slut=horisont_slut, 
         Status="Produktion", Beskrivning=f"Faktisk tid: {fysisk_ledtid_dagar} dagar")
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

# Fixa X-axeln så den visar varje månad
fig.update_xaxes(
    dtick="M1", # "M1" betyder "varje 1 månad"
    tickformat="%b\n%Y", # Visar månadsnamn och år
    ticklabelmode="period"
)

fig.update_yaxes(autorange="reversed")
fig.update_layout(showlegend=False, height=400)

st.plotly_chart(fig, use_container_width=True)

# --- SAMMANFATTNING ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total horisont", f"{horisont_manader} mån")
    st.caption(f"Motsvarar ca {totala_dagar_horisont} dagar")
with c2:
    st.metric("Fysisk ledtid", f"{fysisk_ledtid_dagar} dagar")
    st.caption("Tid för produktion & frakt")
with c3:
    gap = totala_dagar_horisont - fysisk_ledtid_dagar
    st.metric("Administrativ väntetid", f"{gap} dagar")
    st.caption("Tid där ordern är låst men ej startad")

st.info(f"Här ser du att leverantören vill ha ordern **{gap} dagar** innan de ens behöver börja baka tårtan!")
