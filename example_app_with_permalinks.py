import streamlit as st

import streamlit_permalink as stp

is_checked = stp.checkbox('checkbox', url_key='checkbox')
is_checked_default = stp.checkbox('checkbox default', value=True, url_key='checkbox_default')
radio = stp.radio('radio', ['Option A', 'Option B', 'Option C'], url_key='radio')
selectbox = stp.selectbox('selectbox', ['Option A', 'Option B', 'Option C'], url_key='selectbox')
# multiselect = stp.multiselect('multiselect', ['Zażółć gęślą jaźń', 'A', 'Grzegżółka', 'B', 'Brzęczyszczykiewicz',
#                                               '/%^&+$#@!~`\"\'[]{}'], default=['A', 'B'], url_key='multiselect')
slider = stp.slider('slider', min_value=1, max_value=100, value=[42, 67], url_key='slider')
select_slider = stp.select_slider('select_slider', ['apple', 'banana', 'mango', 'orange'], value='banana',
                                  url_key='select_slider')
text_input = stp.text_input('text_input', value='xxx', url_key='text_input')
number_input = stp.number_input('number_input', min_value=1, max_value=100, value=42, url_key='number_input')
text_area = stp.text_area('text_area', url_key='text_area')
date_input = stp.date_input('date_input', url_key='date_input')
time_input = stp.time_input('time_input', url_key='time_input')
color_picker = stp.color_picker('color_picker', value='#00EEFF', url_key='color_picker')

with st.sidebar:
    st.write(dict(
        is_checked=is_checked,
        is_checked_default=is_checked_default,
        radio=radio,
        selectbox=selectbox,
        # multiselect=multiselect,
        slider=slider,
        select_slider=select_slider,
        text_input=text_input,
        number_input=number_input,
        text_area=text_area,
        date_input=date_input,
        time_input=time_input,
        color_picker=color_picker,
    ))

with stp.form('form'):
    selectbox = stp.selectbox('selectbox', ['Option A', 'Option B', 'Option C'], url_key='form_selectbox')
    text_input = stp.text_input('text_input', value='xxx', url_key='form_text_input')
    time_input = stp.time_input('time_input', url_key='form_time_input')
    stp.form_submit_button('Submit')

with st.sidebar:
    st.write(dict(
        selectbox=selectbox,
        text_input=text_input,
        time_input=time_input,
    ))
