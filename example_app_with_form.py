import streamlit as st
from datetime import date, datetime, time

import streamlit_permalink as stp

with stp.form('form'):
    selectbox = stp.selectbox('selectbox', ['Option A', 'Option B', 'Option C'], url_key='selectbox')
    text_input = stp.text_input('text_input', value='xxx', url_key='text_input')
    time_input = stp.time_input('time_input', url_key='time_input')
    stp.form_submit_button('Submit')

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
