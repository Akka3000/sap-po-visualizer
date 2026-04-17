import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="PO-Horisont Rolling Forecast", layout="wide")

st.title("🔄 Rolling PO-Horizon Visualizer")

# --- INPUTS I SIDOPANELEN ---
st.sidebar.header("Inställningar")

# 1. Välj bindande tid i MÅNADER (som du bad om)
horisont_manader = st.sidebar.number_input("Bindande horisont (antal månader)", min_value=1, max_value=24, value=7)

# 2. Välj nuvarande datum (för att simulera "var man befinner sig i tiden")
idag = st.sidebar.date_input("Dagens datum (Simulera nuet)", date.today())

# 3. Faktisk ledtid för artikeln
fysisk_ledtid_dagar = st.sidebar.slider("Faktisk fysisk ledtid (dagar)", 10, 150, 70)

# --- BERÄKNINGAR ---
# Start på aktuell månad
denna_manad_start = idag.replace(day=1)

# Slutet på horisonten (idag + X månader)
horisont_slut = denna_manad_start + relativedelta(months=horisont_manader)

# När måste vi börja producera för att få material vid horisontens slut?
produktion_start = horisont_slut - relativedelta(days=fysisk_ledtid_dagar)

# --- VISUALISERING ---
st.subheader(f"Din {horisont_manader} månaders 'Ordermatta'")

# Skapa data för tidslinjen
data = [
    # Den nuvarande månaden (genomskinlig/pågående)
    dict(Fas="Aktuell månad", Start=denna_manad_start, Slut=denna_manad_start + relativedelta(months=1), Status="Pågående (Genomskinlig)"),
    # Hela den bindande horisonten
    dict(Fas="PO-Horisont", Start=denna_manad_start, Slut=horisont_slut, Status="Bindande Commitment"),
    # Den fysiska produktionen i slutet av horisonten
    dict(Fas="Fysiskt flöde", Start=produktion_start, Slut=horisont_slut, Status="Produktion/Transport")
]

df = pd.DataFrame(data)

# Färgschema och transparens (opacity)
fig = px.timeline(df, x_start="Start", x_end="Slut", y="Fas", color="Status",
                 color_discrete_map={
                     "Pågående (Genomskinlig)": "rgba(100, 100, 100, 0.3)", 
                     "Bindande Commitment": "#FF4B4B",
                     "Produktion/Transport": "#0068C9"
                 })

fig.update_yaxes(autorange="reversed")
fig.update_layout(showlegend=True)

st.plotly_chart(fig, use_container_width=True)

# --- INFOTEXT ---
st.info(f"""
**Förklaring:**
* Just nu är du i **{idag.strftime('%B %Y')}**. Denna månad visas blekt eftersom den redan "rullar".
* Din horisont sträcker sig fram till **{horisont_slut.strftime('%B %Y')}**.
* Allt rött i diagrammet är material du har lovat att köpa. 
* Vid nästa månadsskifte flyttas hela den röda mattan ett steg åt höger och en ny månad läggs till i slutet.
""")
