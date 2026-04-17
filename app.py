import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="PO-Horisont Visualisering", layout="wide")

st.title("📦 Visualisering: PO-horisont vs Ledtid")
st.write("Verktyg för att förklara skillnaden mellan fysisk ledtid och bindande horisont.")

# Inställningar i sidopanelen
st.sidebar.header("Parametrar")
behovs_datum = st.sidebar.date_input("När behövs materialet?", datetime(2027, 1, 15))
horisont_dagar = st.sidebar.slider("PO-horisont (dagar i SAP)", 30, 365, 210)
fysisk_ledtid = st.sidebar.slider("Faktisk fysisk ledtid (dagar)", 10, 150, 70)

# Beräkningar
order_datum = behovs_datum - timedelta(days=horisont_dagar)
produktion_start = behovs_datum - timedelta(days=fysisk_ledtid)

# Visa nyckeltal
col1, col2, col3 = st.columns(3)
col1.metric("Beställ senast (SAP)", order_datum.strftime('%Y-%m-%d'))
col2.metric("Produktionsstart", produktion_start.strftime('%Y-%m-%d'))
col3.metric("Bindande dagar extra", horisont_dagar - fysisk_ledtid)

# Skapa tidslinje
df = pd.DataFrame([
    dict(Fas="PO-Horisont (Bindande)", Start=order_datum, Slut=behovs_datum, Typ="Kontrakt"),
    dict(Fas="Fysisk Produktion", Start=produktion_start, Slut=behovs_datum, Typ="Fysiskt flöde")
])

fig = px.timeline(df, x_start="Start", x_end="Slut", y="Fas", color="Typ",
                 color_discrete_map={"Kontrakt": "#FF4B4B", "Fysiskt flöde": "#0068C9"})

fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

st.info(f"Genom att sätta {horisont_dagar} dagar i SAP låser ni ordern {horisont_dagar - fysisk_ledtid} dagar innan leverantören ens behöver börja producera.")