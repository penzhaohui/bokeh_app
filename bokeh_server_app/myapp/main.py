# coding=utf-8
from bokeh.models import Button
from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot
from bokeh.themes import Theme
import numpy as np
from bokeh.events import ButtonClick, DoubleTap
#from bokeh.events import DocumentUpdate
from bokeh.document.events import DocumentPatchedEvent
# from .app_hooks import on_session_created, on_session_destroyed, on_server_loaded, on_server_unloaded
from functools import lru_cache

# coding=utf-8
def on_session_destroyed(session_context):
    ''' If present, this function is called when a session is closed. '''
    print('The on_session_destroyed event is fired for document.')
    pass

def on_periodic_callback():
    ''' If present, this function is called when a session is closed. '''
    print('The add_periodic_callback event is fired for document.')
    pass

def on_next_tick_callback():
    ''' If present, this function is called when a session is closed. '''
    print('The on_next_tick_callback event is fired for document.')
    pass

def on_button_click_event_callback(event):
    print(event._model_id)
    btn_model = curdoc().get_model_by_id(event._model_id)

def on_document_update_event_callback(event):
    print('document update event is fired.')

def on_document_patch_event_callback(event):
    print('document patch event is fired.')

def main():
    plots = [figure(title = 'Styles Demo {i}'.format(i = i + 1), plot_width = 200, plot_height = 200, tools = '') for i in range(9)]
    [plot.line(np.arange(10), np.random.random(10)) for plot in plots]

    button_bokeh = Button(label = "Custom Style: Bokeh Button", css_classes = ['custom_button_bokeh'])
    button_bokeh.name = 'button_text'
    button_bokeh.on_event(ButtonClick, on_button_click_event_callback)
    curdoc().add_root(button_bokeh)
    curdoc().add_root(gridplot(children = [plot for plot in plots], ncols = 3))

    cur_doc = curdoc()
    # cur_doc.on_event(DocumentUpdate, on_document_update_event_callback)
    cur_doc.on_event(DocumentPatchedEvent, on_document_patch_event_callback)

    cur_doc.theme = Theme(filename="G:\\dt-boot\\dt-data-analysis-visual\\app\\api\\server_visual\\timeseries-multi\\dark-theme.yaml")
    cur_doc.on_session_destroyed(on_session_destroyed)
    # cur_doc.add_periodic_callback(on_periodic_callback, 1000)
    cur_doc.add_next_tick_callback(on_next_tick_callback)

main()