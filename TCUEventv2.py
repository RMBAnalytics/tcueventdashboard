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
    .css-1d391kg, .css-1v0mbdj, .st-af, .st-ag, .st-ah, .st-ai {
        background-color: #4D1979 !important;
        color: white !important;
    }
    .stDataFrame th, .stDataFrame td {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load TCU logo (replace 'tcu_logo.png' with your actual file path)
logo_path = "tcu_logo.png"
try:
    logo = Image.open(logo_path)
    st.image(logo, width=150)
except:
    st.warning("Logo not found: please add 'tcu_logo.png' to the project directory.")

# Load data
df = pd.read_excel("FY25 Event Registrants 7-7v2.xlsx", sheet_name=0)
df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col])
df['Paid'] = df['Paid'].map({'Yes': True, 'No': False})

# Sidebar Filters
st.sidebar.subheader("Filters")

# One-click toggle for chapter selection
if st.sidebar.button("Select All Chapters/Groups"):
    selected_chapters = df['Chapter/Club/Group'].unique().tolist()
else:
    selected_chapters = st.sidebar.multiselect("Select Chapters/Groups", df['Chapter/Club/Group'].unique())

selected_types = st.sidebar.multiselect("Select Event Types", df['Event Type'].unique(), default=list(df['Event Type'].unique()))
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
col1.metric("Total Registrants", total_registrants)
col2.metric("Known Registrants", total_known)
col3.metric("Number of Events", total_events)

# Charts
st.subheader("Registrants by Chapter/Group")
chapter_chart = alt.Chart(
    filtered_df.groupby('Chapter/Club/Group')['Registrants'].sum().reset_index()
).mark_bar().encode(
    x=alt.X('Registrants:Q', title='Total Registrants'),
    y=alt.Y('Chapter/Club/Group:N', sort='-x', title='Chapter/Group'),
    tooltip=['Chapter/Club/Group', 'Registrants']
).properties(height=400)

st.altair_chart(chapter_chart, use_container_width=True)

st.subheader("Registrants by Event Type")
type_chart = alt.Chart(
    filtered_df.groupby('Event Type')['Registrants'].sum().reset_index()
).mark_bar().encode(
    x=alt.X('Registrants:Q', title='Total Registrants'),
    y=alt.Y('Event Type:N', sort='-x'),
    tooltip=['Event Type', 'Registrants']
).properties(height=300)

st.altair_chart(type_chart, use_container_width=True)

st.subheader("Event Table")
st.dataframe(filtered_df.sort_values(by='Event start date'))
