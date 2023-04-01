from datetime import datetime, date, time
import streamlit as st

# Instance of UrlAwareForm or None
# used for widgets to know whether they
# are inside a form or not
_active_form = None


def to_url_value(result):
    if isinstance(result, str):
        return result
    if isinstance(result, (bool, float, int)):
        return str(result)
    if isinstance(result, (list, tuple)):
        return list(map(to_url_value, result))
    if isinstance(result, date):
        return result.isoformat()
    if isinstance(result, time):
        return result.strftime('%H:%M')
    raise TypeError(f'unsupported type: {type(result)}')


class UrlAwareWidget:
    def __init__(self, base_widget, form=None):
        self.base_widget = base_widget
        self.form = form
        self.__module__ = base_widget.__module__
        self.__name__ = base_widget.__name__
        self.__qualname__ = base_widget.__qualname__
        self.__doc__ = base_widget.__doc__
        self.__annotations__ = base_widget.__annotations__

    # Widgets inside forms in Streamlit can be created in 2 ways:
    #   form = st.form('my_form')
    #   with form:
    #       st.text_input(...)  # first way
    #   form.text_input(...)    # second, equivalent way
    # For this second way, we need to know if UrlAwareWidget has been
    # called like a method on the form object. Therefore, we use the
    # descriptor protocol to attach the form object:
    def __get__(self, form, _objtype=None):
        assert isinstance(form, UrlAwareForm)
        return UrlAwareWidget(getattr(form.base_form, self.base_widget.__name__), form)

    def __call__(self, *args, **kwargs):
        if 'url_key' not in kwargs:
            return self.base_widget(*args, **kwargs)

        if _active_form is not None or self.form is not None:
            return self.call_inside_form(self.form or _active_form, *args, **kwargs)

        url_key = kwargs.pop('url_key')
        if 'key' not in kwargs:
            kwargs['key'] = url_key
        key = kwargs['key']

        user_supplied_change_handler = kwargs.get('on_change', lambda *args, **kwargs: None)

        def on_change(*args, **kwargs):
            qp = st.experimental_get_query_params()
            qp[url_key] = to_url_value(st.session_state[key])
            st.experimental_set_query_params(**qp)
            user_supplied_change_handler(*args, **kwargs)

        kwargs['on_change'] = on_change

        qp = st.experimental_get_query_params()
        url_value = qp.get(key, None)
        if key in st.session_state:
            value = [st.session_state[key]]
        elif url_value:
            value = url_value
        else:
            value = None

        handler = getattr(self, f'handle_{self.base_widget.__name__}')
        return handler(value, *args, **kwargs)

    def call_inside_form(self, form, *args, **kwargs):
        url_key = kwargs.pop('url_key')
        if 'key' not in kwargs:
            kwargs['key'] = url_key
        key = kwargs['key']
        form.field_mapping[url_key] = key
        url = st.experimental_get_query_params()
        url_value = url.get(url_key, None)
        handler = getattr(self, f'handle_{self.base_widget.__name__}')
        return handler(url_value, *args, **kwargs)

    def handle_checkbox(self, url_value, label, value=False, *args, **kwargs):
        url_value = url_value and url_value[0]
        url_value = {'True': True, 'False': False}.get(url_value, url_value)
        if url_value is not None:
            value = url_value
        return self.base_widget(label, value, *args, **kwargs)

    def handle_radio(self, url_value, *args, **kwargs):
        return self.handle_selectbox(url_value, *args, **kwargs)

    def handle_selectbox(self, url_value, label, options, index=0, *args, **kwargs):
        options = list(map(str, options))
        if url_value is not None and len(url_value) == 1:
            try:
                index = options.index(url_value[0])
            except ValueError:
                pass
        return self.base_widget(label, options, index, *args, **kwargs)

    def handle_multiselect(self, url_value, label, options, default=None, *args, **kwargs):
        options = list(map(str, options))
        if url_value is not None:
            default = url_value
        return self.base_widget(label, options, default, *args, **kwargs)

    def handle_slider(self, url_value, label, min_value=None, max_value=None, value=None, *args, **kwargs):
        slider_type = float
        if value is not None:
            if isinstance(value, list):
                slider_type = type(value[0])
            else:
                slider_type = type(value)
        elif min_value is not None:
            slider_type = type(min_value)
        elif max_value is not None:
            slider_type = type(max_value)
        assert slider_type in (int, float), f"unsupported slider type: {slider_type}"

        if url_value is not None:
            if len(url_value) == 1:
                if isinstance(url_value[0], tuple):
                    value = [slider_type(v) for v in url_value[0]]
                else:
                    value = slider_type(url_value[0])
            else:
                value = [slider_type(v) for v in url_value]

        return self.base_widget(label, min_value, max_value, value, *args, **kwargs)

    def handle_select_slider(self, url_value, label, options, value=None, *args, **kwargs):
        options = list(map(str, options))
        if url_value is not None:
            if len(url_value) == 1:
                value = url_value[0]
            else:
                value = url_value
        return self.base_widget(label, options, value, *args, **kwargs)

    def handle_text_input(self, url_value, label, value="", *args, **kwargs):
        if url_value is not None:
            value = url_value[0]
        return self.base_widget(label, value, *args, **kwargs)

    def handle_number_input(self, url_value, label, min_value=None, max_value=None, value=None, *args, **kwargs):
        input_type = float
        if value is not None:
            input_type = type(value)
        elif min_value is not None:
            input_type = type(min_value)
        elif max_value is not None:
            input_type = type(max_value)
        assert input_type in (int, float), f"unsupported number_input type: {input_type}"

        if url_value is not None:
            value = input_type(float(url_value[0]))

        if value is None:
            return self.base_widget(label, min_value, max_value, *args, **kwargs)
        return self.base_widget(label, min_value, max_value, value, *args, **kwargs)

    def handle_text_area(self, url_value, *args, **kwargs):
        return self.handle_text_input(url_value, *args, **kwargs)

    def handle_date_input(self, url_value, label, value=None, *args, **kwargs):
        parse_date = lambda s: datetime.strptime(s, '%Y-%m-%d').date()
        if url_value is not None:
            if len(url_value) == 1:
                if isinstance(url_value[0], date):
                    value = url_value[0]
                else:
                    value = parse_date(url_value[0])
            else:
                value = [parse_date(v) for v in url_value]
        return self.base_widget(label, value, *args, **kwargs)

    def handle_time_input(self, url_value, label, value=None, *args, **kwargs):
        parse_time = lambda s: datetime.strptime(s, '%H:%M').time()
        if url_value is not None:
            if len(url_value) == 1:
                if isinstance(url_value[0], time):
                    value = url_value[0]
                else:
                    value = parse_time(url_value[0])
        return self.base_widget(label, value, *args, **kwargs)

    def handle_color_picker(self, url_value, label, value=None, *args, **kwargs):
        if url_value is not None:
            value = url_value[0]
        return self.base_widget(label, value, *args, **kwargs)


class UrlAwareFormSubmitButton:
    def __init__(self, base_widget, form=None):
        self.base_widget = base_widget
        self.form = form

    # Widgets inside forms in Streamlit can be created in 2 ways:
    #   form = st.form('my_form')
    #   with form:
    #       st.text_input(...)  # first way
    #   form.text_input(...)    # second, equivalent way
    # For this second way, we need to know if UrlAwareWidget has been
    # called like a method on the form object. Therefore, we use the
    # descriptor protocol to attach the form object:
    def __get__(self, form, _objtype=None):
        assert isinstance(form, UrlAwareForm)
        return UrlAwareFormSubmitButton(getattr(form.base_form, self.base_widget.__name__), form)

    def __call__(self, *args, **kwargs):
        if _active_form is not None or self.form is not None:
            return self.call_inside_form(self.form or _active_form, *args, **kwargs)
        return self.base_widget(*args, **kwargs)

    def call_inside_form(self, form, *args, **kwargs):
        url = st.experimental_get_query_params()
        user_supplied_click_handler = kwargs.get('on_click', lambda: None)

        def on_click(*args, **kwargs):
            for url_key, key in form.field_mapping.items():
                url[url_key] = to_url_value(getattr(st.session_state, key))
            st.experimental_set_query_params(**url)
            user_supplied_click_handler(*args, **kwargs)

        kwargs['on_click'] = on_click
        return self.base_widget(*args, **kwargs)


checkbox = UrlAwareWidget(st.checkbox)
radio = UrlAwareWidget(st.radio)
selectbox = UrlAwareWidget(st.selectbox)
multiselect = UrlAwareWidget(st.multiselect)
slider = UrlAwareWidget(st.slider)
select_slider = UrlAwareWidget(st.select_slider)
text_input = UrlAwareWidget(st.text_input)
number_input = UrlAwareWidget(st.number_input)
text_area = UrlAwareWidget(st.text_area)
date_input = UrlAwareWidget(st.date_input)
time_input = UrlAwareWidget(st.time_input)
color_picker = UrlAwareWidget(st.color_picker)
form_submit_button = UrlAwareFormSubmitButton(st.form_submit_button)


class UrlAwareForm:
    checkbox = UrlAwareWidget(st.checkbox)
    radio = UrlAwareWidget(st.radio)
    selectbox = UrlAwareWidget(st.selectbox)
    multiselect = UrlAwareWidget(st.multiselect)
    slider = UrlAwareWidget(st.slider)
    select_slider = UrlAwareWidget(st.select_slider)
    text_input = UrlAwareWidget(st.text_input)
    number_input = UrlAwareWidget(st.number_input)
    text_area = UrlAwareWidget(st.text_area)
    date_input = UrlAwareWidget(st.date_input)
    time_input = UrlAwareWidget(st.time_input)
    color_picker = UrlAwareWidget(st.color_picker)
    form_submit_button = UrlAwareFormSubmitButton(st.form_submit_button)

    def __init__(self, key, *args, **kwargs):
        self.base_form = st.form(key, *args, **kwargs)
        # map from URL query param names to streamlit widget keys
        self.field_mapping = {}

    def __enter__(self):
        global _active_form
        _active_form = self
        return self.base_form.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        global _active_form
        _active_form = None
        return self.base_form.__exit__(exc_type, exc_value, traceback)

    def __getattr__(self, attr):
        return getattr(self.base_form, attr)


form = UrlAwareForm
