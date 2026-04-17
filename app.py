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
fysisk_ledtid_dagar = st.sidebar.number_input("Produktion + transport ledtid (Dagar)", min_value=1, max_value=500, value=70)

# --- BERÄKNINGAR ---
denna_manad_start = idag.replace(day=1)
horisont_slut = denna_manad_start + relativedelta(months=horisont_manader)
produktion_start = horisont_slut - relativedelta(days=fysisk_ledtid_dagar)
totala_dagar_horisont = (horisont_slut - denna_manad_start).days

# --- NY LOGIK: SKAPA EN RAD PER MÅNAD FÖR ATT FÅ SIFFRORNA CENTRERADE ---
chart_data = []

# 1. Lägg till den blekta "Nu-månaden"
chart_data.append(dict(Fas="Aktuell månad", Start=denna_manad_start, Slut=denna_manad_start + relativedelta(months=1), 
                       Status="Nu-Period", Text="Aktuell Månad"))

# 2. Skapa individuella block för varje månad i horisonten
for i in range(horisont_manader):
    m_start = denna_manad_start + relativedelta(months=i)
    m_slut = m_start + relativedelta(months=1)
    chart_data.append(dict(Fas="PO-Horisont", Start=m_start, Slut=m_slut, 
                           Status="Låst tid", Text=str(i+1)))

# 3. Lägg till produktionsflödet som en egen rad längst ner
chart_data.append(dict(Fas="Produktion", Start=produktion_start, Slut=horisont_slut, 
                       Status="Produktion", Text=f"Produktion + transport ledtid ({fysisk_ledtid_dagar} dgr)"))

df = pd.DataFrame(chart_data)

# --- FIGUR ---
fig = px.timeline(df, x_start="Start", x_end="Slut", y="Fas", color="Status",
                 text="Text", 
                 color_discrete_map={
                     "Nu-Period": "#008000", 
                     "Låst tid": "#Ff0000", 
                     "Produktion": "#3399FF"
                 })

# Fixa utseendet
fig.update_xaxes(range=[denna_manad_start - relativedelta(months=1), horisont_slut + relativedelta(months=2)], dtick="M1", tickformat="%b %Y", ticklabelmode="period", showgrid=True)
fig.update_traces(textposition='inside', textfont_color="white", insidetextanchor='middle', textfont_size=18, marker_line_color="white", marker_line_width=1)
fig.update_yaxes(autorange="reversed")
fig.update_layout(showlegend=False, height=450, dragmode='pan')

st.plotly_chart(fig, use_container_width=True)

# --- INFO-BOXAR ---
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total horisont", f"{horisont_manader} mån")
    st.write(f"**{totala_dagar_horisont} dagar**")
    st.caption("Tid vi låser oss i SAP")

with col2:
    st.metric("Fysisk ledtid", f"{fysisk_ledtid_dagar} dgr")
    # Vi räknar ut månader genom att dela med 30 (snittmånad)
    prod_man = round(fysisk_ledtid_dagar / 30, 1)
    st.write(f"**{prod_man} månader**")
    st.caption("Tid för faktisk produktion")

with col3:
    gap_dagar = totala_dagar_horisont - fysisk_ledtid_dagar
    st.metric("Leverantörens frihet", f"{gap_dagar} dgr")
    # Samma här, räknar om gapet till månader
    gap_man = round(gap_dagar / 30, 1)
    st.write(f"**{gap_man} månader**")
    st.caption("Tid ordern ligger 'stilla'")
