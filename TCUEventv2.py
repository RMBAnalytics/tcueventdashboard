import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image
import base64

# Custom CSS for purple background and white text
st.markdown("""
    <style>
    body {
        background-color: #4D1979;
        color: white;
    }
    .stApp {
        background-color: #4D1979;
        color: white;
    }
    .stDataFrame th, .stDataFrame td {
        color: black !important;
    }
    .metric-label, .metric-value {
        color: white !important;
    }
    .metric-box {
        text-align: center;
        padding: 1rem;
        background-color: transparent;
    }
    .metric-box h3, .metric-box h2 {
        margin: 0;
        padding: 0;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Load TCU logo (replace 'tcu_logo.png' with your actual file path)
logo_path = "tcu_logo.png"
try:
    logo = Image.open(logo_path)
    st.markdown("""<div style='text-align:center;'>""", unsafe_allow_html=True)
    st.image(logo, use_container_width=True)
    st.markdown("""</div>""", unsafe_allow_html=True)
except:
    st.warning("Logo not found: please add 'tcu_logo.png' to the project directory.")

# Load data
df = pd.read_excel("FY25 Event Registrants 7-7v2.xlsx", sheet_name=0)
df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col])
df['Paid'] = df['Paid'].map({'Yes': True, 'No': False})

# Sidebar Filters
st.sidebar.subheader("Filters")

# One-click toggle for chapter selection
chapter_buttons = st.sidebar.radio("Chapter Selection", ["Custom Select", "Select All", "Unselect All"], index=0)
if chapter_buttons == "Select All":
    selected_chapters = list(sorted(df['Chapter/Club/Group'].dropna().unique()))
elif chapter_buttons == "Unselect All":
    selected_chapters = []
else:
    selected_chapters = st.sidebar.multiselect("Select Chapters/Groups", sorted(df['Chapter/Club/Group'].unique()))

event_type_buttons = st.sidebar.radio("Event Type Selection", ["Custom Select", "Select All", "Unselect All"], index=0)
if event_type_buttons == "Select All":
    selected_types = list(sorted(df['Event Type'].dropna().unique()))
elif event_type_buttons == "Unselect All":
    selected_types = []
else:
    selected_types = st.sidebar.multiselect("Select Event Types", sorted(df['Event Type'].unique()), default=sorted(df['Event Type'].unique()))
paid_only = st.sidebar.checkbox("Show Only Paid Events", value=False)

filtered_df = df[df['Chapter/Club/Group'].isin(selected_chapters) if selected_chapters else df['Chapter/Club/Group'].notnull()]
filtered_df = filtered_df[filtered_df['Event Type'].isin(selected_types)]
if paid_only:
    filtered_df = filtered_df[filtered_df['Paid'] == True]

# Summary Metrics
total_registrants = filtered_df['Registrants'].sum()
total_known = filtered_df['Known Registrants'].sum()
total_events = len(filtered_df)

st.title("FY25 Event Registration Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class='metric-box'>
        <h3>Total Registrants</h3>
        <h2>{total_registrants}</h2>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class='metric-box'>
        <h3>Known Registrants</h3>
        <h2>{total_known}</h2>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class='metric-box'>
        <h3>Number of Events</h3>
        <h2>{total_events}</h2>
    </div>""", unsafe_allow_html=True)

# Charts
st.subheader("Registrants by Chapter/Group")
chapter_chart = alt.Chart(
    filtered_df.groupby('Chapter/Club/Group')['Registrants'].sum().reset_index()
).mark_bar(size=12).encode(
    x=alt.X('Registrants:Q', title='Total Registrants'),
    y=alt.Y('Chapter/Club/Group:N', sort='-x', title='Chapter/Group', axis=alt.Axis(labelLimit=1000, labelAngle=0)),
    tooltip=['Chapter/Club/Group', 'Registrants']
).properties(height=785)

st.altair_chart(chapter_chart, use_container_width=True)

st.subheader("Registrants by Event Type")
type_chart = alt.Chart(
    filtered_df.groupby('Event Type')['Registrants'].sum().reset_index()
).mark_bar(size=20).encode(
    x=alt.X('Registrants:Q', title='Total Registrants'),
    y=alt.Y('Event Type:N', sort='-x', axis=alt.Axis(labelLimit=1000, labelAngle=0)),
    tooltip=['Event Type', 'Registrants']
).properties(height=400)

st.altair_chart(type_chart, use_container_width=True)

st.subheader("Event Table")
st.markdown("""
    <style>
    .scrollable-table-container {
        max-height: 500px;
        overflow-y: auto;
        overflow-x: auto;
        border: 1px solid #ccc;
        padding: 5px;
        background-color: white;
        white-space: nowrap;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("<div class='scrollable-table-container'>", unsafe_allow_html=True)
st.dataframe(filtered_df.sort_values(by='Event start date'))
st.markdown("</div>", unsafe_allow_html=True)
