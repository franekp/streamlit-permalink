from datetime import datetime, date, time
from packaging.version import parse as V
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
        if V(st.__version__) < V('1.30'):
            url = st.experimental_get_query_params()
        user_supplied_change_handler = kwargs.get('on_change', lambda *args, **kwargs: None)

        def on_change(*args, **kwargs):
            if V(st.__version__) < V('1.30'):
                url[url_key] = to_url_value(getattr(st.session_state, key))
                st.experimental_set_query_params(**url)
            else:
                st.query_params[url_key] = to_url_value(getattr(st.session_state, key))
            user_supplied_change_handler(*args, **kwargs)


        kwargs['on_change'] = on_change
        if V(st.__version__) < V('1.30'):
            url_value = url.get(url_key, None)
        else:
            url_value = st.query_params.get_all(url_key) or None
        handler = getattr(self, f'handle_{self.base_widget.__name__}')
        # TODO: remove the first return value from the handle_{widget-name}() methods
        # NOTE: do this when we gain confidence that the on_change callbacks are a
        # reliable replacement for the SessionState-based hacky solution for permalinks
        _, result = handler(url_value, *args, **kwargs)
        return result

    def call_inside_form(self, form, *args, **kwargs):
        url_key = kwargs.pop('url_key')
        if 'key' not in kwargs:
            kwargs['key'] = url_key
        key = kwargs['key']
        form.field_mapping[url_key] = key
        if V(st.__version__) < V('1.30'):
            url = st.experimental_get_query_params()
            url_value = url.get(url_key, None)
        else:
            url_value = st.query_params.get_all(url_key) or None
        handler = getattr(self, f'handle_{self.base_widget.__name__}')
        _, result = handler(url_value, *args, **kwargs)
        return result

    def handle_checkbox(self, url_value, label, value=False, *args, **kwargs):
        url_value = url_value and url_value[0]
        url_value = {'True': True, 'False': False}.get(url_value, url_value)
        if url_value is not None:
            value = url_value
        result = self.base_widget(label, value, *args, **kwargs)
        return str(result), result

    def handle_radio(self, url_value, *args, **kwargs):
        return self.handle_selectbox(url_value, *args, **kwargs)

    def handle_selectbox(self, url_value, label, options, index=0, *args, **kwargs):
        url_value = url_value and url_value[0]
        options = list(map(str, options))
        if url_value is not None:
            try:
                index = options.index(url_value)
            except ValueError:
                pass
        result = self.base_widget(label, options, index, *args, **kwargs)
        return result, result

    def handle_multiselect(self, url_value, label, options, default=None, *args, **kwargs):
        options = list(map(str, options))
        if url_value is not None:
            default = url_value
        result = self.base_widget(label, options, default, *args, **kwargs)
        return result, result

    def handle_slider(self, url_value, label, min_value=None, max_value=None, value=None, *args, **kwargs):
        if value is not None and not isinstance(value, list):
            slider_type = type(value)
        if value is not None and isinstance(value, list):
            slider_type = type(value[0])
        elif min_value is not None:
            slider_type = type(min_value)
        elif max_value is not None:
            slider_type = type(max_value)
        assert slider_type in (int, float), "unsupported slider type"
        if url_value is not None:
            if len(url_value) == 1:
                value = slider_type(float(url_value[0]))
            else:
                value = [slider_type(float(i)) for i in url_value]
        result = self.base_widget(label, min_value, max_value, value, *args, **kwargs)
        if isinstance(result, tuple):
            new_url_value = list(map(str, result))
        else:
            new_url_value = str(result)
        return new_url_value, result

    def handle_select_slider(self, url_value, label, options, value=None, *args, **kwargs):
        options = list(map(str, options))
        if url_value is not None:
            if len(url_value) == 1:
                value = url_value[0]
            else:
                value = url_value
        result = self.base_widget(label, options, value, *args, **kwargs)
        return result, result

    def handle_text_input(self, url_value, label, value="", *args, **kwargs):
        if url_value is not None:
            value = url_value[0]
        result = self.base_widget(label, value, *args, **kwargs)
        return result, result

    def handle_number_input(self, url_value, label, min_value=None, max_value=None, value=None, *args, **kwargs):
        input_type = float
        if value is not None:
            input_type = type(value)
        elif min_value is not None:
            input_type = type(min_value)
        elif max_value is not None:
            input_type = type(max_value)
        assert input_type in (int, float), "unsupported number_input type"
        if url_value is not None:
            value = input_type(float(url_value[0]))
        if value is None:
            result = self.base_widget(label, min_value, max_value, *args, **kwargs)
        else:
            result = self.base_widget(label, min_value, max_value, value, *args, **kwargs)
        return str(result), result

    def handle_text_area(self, url_value, *args, **kwargs):
        return self.handle_text_input(url_value, *args, **kwargs)

    def handle_date_input(self, url_value, label, value=None, *args, **kwargs):
        parse_date = lambda s: datetime.strptime(s,'%Y-%m-%d').date()
        if url_value is not None:
            if len(url_value) == 1:
                value = parse_date(url_value[0])
            else:
                value = list(map(parse_date, url_value))
        result = self.base_widget(label, value, *args, **kwargs)
        if isinstance(result, tuple):
            new_url_value = [d.isoformat() for d in result]
        elif result is not None:
            new_url_value = result.isoformat()
        else:
            new_url_value = result
        return new_url_value, result

    def handle_time_input(self, url_value, label, value=None, *args, **kwargs):
        parse_time = lambda s: datetime.strptime(s, '%H:%M').time()
        if url_value is not None:
            value = parse_time(url_value[0])
        result = self.base_widget(label, value, *args, **kwargs)
        if result is not None:
            return result.strftime('%H:%M'), result
        else:
            return result, result

    def handle_color_picker(self, url_value, label, value=None, *args, **kwargs):
        if url_value is not None:
            value = url_value[0]
        result = self.base_widget(label, value, *args, **kwargs)
        return result, result


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
        if V(st.__version__) < V('1.30'):
            url = st.experimental_get_query_params()
        user_supplied_click_handler = kwargs.get('on_click', lambda: None)

        def on_click(*args, **kwargs):
            for url_key, key in form.field_mapping.items():
                raw_value = getattr(st.session_state, key)
                if raw_value is not None:
                    if V(st.__version__) < V('1.30'):
                        url[url_key] = to_url_value(raw_value)
                    else:
                        st.query_params[url_key] = to_url_value(raw_value)
            if V(st.__version__) < V('1.30'):
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
