# coding=utf-8
from threading import Thread

from flask import Flask, render_template
from flask import request, jsonify
from bokeh.models import Button
from threading import Thread
from bokeh.server.server import Server
from bokeh.command.util import build_single_handler_application
from tornado.ioloop import IOLoop
from bokeh.settings import settings
from bokeh.embed.server import server_html_page_for_session
import os

app = Flask(__name__)

from bokeh.client import pull_session
from bokeh.embed import server_session


def bk_worker():
    """
    bokeh 后台server 启动
     :return:
    """
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    # 启动时序图handler
    settings.resources = 'server'
    settings.allowed_ws_origin = '*'
    settings.log_level = 'debug'
    settings.minified = False
    # settings.py_log_level = 'debug'
    myapp = build_single_handler_application(os.path.join(os.path.dirname(__file__), "myapp"))
    stocks = build_single_handler_application(os.path.join(os.path.dirname(__file__), "stocks"))
    export_csv = build_single_handler_application(os.path.join(os.path.dirname(__file__), "export_csv"))
    ohlc = build_single_handler_application(os.path.join('G:\\dt-boot\\bokeh\\examples\\app', "ohlc"))
    dash = build_single_handler_application(os.path.join('G:\\dt-boot\\bokeh\\examples\\app', "dash"))
    # spectrogram = build_single_handler_application(os.path.join('G:\\dt-boot\\bokeh\\examples\\app', "spectrogram"))

    server = Server({'/myapp': myapp, '/stocks': stocks, '/export_csv': export_csv, '/ohlc': ohlc, '/dash': dash}, io_loop=IOLoop(), allow_websocket_origin=["*"])
    server.start()
    server.io_loop.start()

@app.route('/command', methods=['GET'])
def bkapp_command():
    with pull_session(session_id='1234567890', url="http://localhost:5006/myapp") as session:
        session.request_server_info()
        cur_doc = session.document
        button = cur_doc.get_model_by_name('button_text')
        cur_doc.remove_root(button)
        import json
        from bokeh.events import Event
        data = '{"event_name": "document_update", "event_values" : {"x": 10, "y": 20, "sx": 200, "sy": 37}}'
        json.loads(data)
        event = json.loads(data, object_hook=Event.decode_json)
        event = json.loads(data)
        cur_doc.apply_json_event(event)
        from bokeh.protocol import Protocol
        # from bokeh.events import DocumentUpdate
        # document_update_event = DocumentUpdate()
        # protocol = Protocol()
        # message = protocol.create("PATCH-DOC", [document_update_event])
        # message.apply_to_document(cur_doc)
        #session._connection.send_message(message)

        from bokeh.document.events import MessageSentEvent
        document_patched_event = MessageSentEvent(document=cur_doc, msg_type='append_dataset', msg_data='append_dataset_data')
        protocol = Protocol()
        message = protocol.create("PATCH-DOC", [document_patched_event])
        # message.apply_to_document(cur_doc)
        session._connection.send_message(message)

    return ''

@app.route('/', methods=['GET'])
def bkapp_page():
    # script = server_document('http://localhost:5006/myapp')
    # return render_template("embed.html", script=script, template="Flask")

    name = request.args.get("app") if 'app' in request.args else 'myapp'

    with pull_session(session_id='1234567890', url="http://localhost:5006/" + name) as session:
        session.request_server_info()
        # update or customize that session
        # session.document.roots[0].children[1].title.text = "Special Sliders For A Specific User!"
        # generate a script to load the customized session

        cur_doc = session.document
        button_bokeh = Button(label="Custom Style: Bokeh Button", css_classes=['custom_button_bokeh'])
        cur_doc.add_root(button_bokeh)

        script = server_session(session_id=session.id, url='http://localhost:5006/' + name)
        # use the script in the rendered page
        template_file = "embed.html"
        if name == 'dash':
            template_file = "index.html"
        # page_source = server_html_page_for_session(session, resources=None, title='测试', template=template_file, template_variables=None)
        # page_source = page_source.replace('root.Bokeh.embed.embed_items(docs_json, render_items)', "root.Bokeh.embed.embed_items(docs_json, render_items, '/dash', 'http://localhost:5006/dash')" )
        page_source = render_template(template_file, script=script, template="Flask")
        return page_source


Thread(target=bk_worker).start()

if __name__ == '__main__':
    print('Opening single process Flask app with embedded Bokeh application on http://localhost:8000/')
    print()
    print('Multiple connections may block the Bokeh app in this configuration!')
    print('See "flask_gunicorn_embed.py" for one way to run multi-process')
    app.run(port=8000)
