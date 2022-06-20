import streamlit as st
from datetime import date, datetime, time

import streamlit_permalink as stp

# is_checked = stp.checkbox('checkbox', url_key='checkbox')
# is_checked_default = stp.checkbox('checkbox default', value=True, url_key='checkbox_default')
# radio = stp.radio('radio', ['Option A', 'Option B', 'Option C'], url_key='radio')
# selectbox = stp.selectbox('selectbox', ['Option A', 'Option B', 'Option C'], url_key='selectbox')
# multiselect = stp.multiselect('multiselect', ['Zażółć gęślą jaźń', 'A', 'Grzegżółka', 'B', 'Brzęczyszczykiewicz', '/%^&+$#@!~`\"\'[]{}'], default=['A', 'B'], url_key='multiselect')
# slider = stp.slider('slider', min_value=1, max_value=100, value=[42, 67], url_key='slider')
# select_slider = stp.select_slider('select_slider', list(range(10)), value='5', url_key='select_slider')
# text_input = stp.text_input('text_input', value='xxx', url_key='text_input')
# number_input = stp.number_input('number_input', min_value=1, max_value=100, value=42, url_key='number_input')
# text_area = stp.text_area('text_area', url_key='text_area')
# date_input = stp.date_input('date_input', url_key='date_input')
# time_input = stp.time_input('time_input', url_key='time_input')
# color_picker = stp.color_picker('color_picker', value='#00EEFF', url_key='color_picker')

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
    "__streamlit__",
    "stp",
    "datetime",
    "date",
    "time",
]
for i in irrelevant:
    del loc[i]
st.write(loc)
