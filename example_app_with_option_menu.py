import streamlit as st
from datetime import date, datetime, time

import streamlit_permalink as stp

# 1. as sidebar menu
with st.sidebar:
    selected = stp.option_menu("Sidebar Menu", ["Home", 'Settings'], url_key='sidebar_menu',
        icons=['house', 'gear'], menu_icon="cast", default_index=1)
    selected

# 2. horizontal menu
selected2 = stp.option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], url_key='horizontal_menu',
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")
selected2

# 3. CSS style definitions
selected3 = stp.option_menu(None, ["Home", "Upload",  "Tasks", 'Settings'], url_key='horizontal_menu2',
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"},
    }
)

loc = locals().copy()
irrelevant = [
    "__name__",
    "__doc__",
    "__package__",
    "__loader__",
    "__spec__",
    "__file__",
    "__builtins__",
    "st",
    "__streamlitmagic__",
    "stp",
    "datetime",
    "date",
    "time",
]
for i in irrelevant:
    if i in loc:
        del loc[i]
st.write(loc)
