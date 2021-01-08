''' Create a simple stocks correlation dashboard.

Choose stocks to compare in the drop down widgets, and make selections
on the plots to update the summary and histograms accordingly.

.. note::
    Running this example requires downloading sample data. See
    the included `README`_ for more information.

Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve stocks

at your command prompt. Then navigate to the URL

    http://localhost:5006/stocks

.. _README: https://github.com/bokeh/bokeh/blob/master/examples/app/stocks/README.md

'''
from functools import lru_cache
from os.path import dirname, join

import pandas as pd
import json
import datetime

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, PreText, Select
from bokeh.plotting import figure
from bokeh.models import (Button, ColumnDataSource, CustomJS, DataTable,
                          NumberFormatter, RangeSlider, TableColumn,)
from bokeh.events import Event, ButtonClick, PanStart, PanEnd, Pan

DATA_DIR = join(dirname(__file__), 'daily')

DEFAULT_TICKERS = ['AAPL', 'GOOG', 'INTC', 'BRCM', 'YHOO']

def nix(val, lst):
    return [x for x in lst if x != val]

@lru_cache()
def load_ticker(ticker):
    fname = join(DATA_DIR, 'table_%s.csv' % ticker.lower())
    data = pd.read_csv(fname, header=None, parse_dates=['date'],
                       names=['date', 'foo', 'o', 'h', 'l', 'c', 'v'])
    data = data.set_index('date')
    return pd.DataFrame({ticker: data.c, ticker+'_returns': data.c.diff()})

origin_df1 = None
origin_df2 = None
pre_x_range_start_time = None
pre_x_range_end_time = None
# origin_df = None

@lru_cache()
def get_data(t1, t2):
    global origin_df1
    global origin_df2
    global pre_x_range_start_time
    global pre_x_range_end_time
    # global origin_df
    origin_df1 = load_ticker(t1)
    origin_df2 = load_ticker(t2)

    # origin_df = pd.concat([origin_df1, origin_df2], axis=1)
    # origin_df['t1'] = origin_df[t1]
    # origin_df['t2'] = origin_df[t2]
    # origin_df['t1_returns'] = origin_df[t1 + '_returns']
    # origin_df['t2_returns'] = origin_df[t2 + '_returns']

    # df1 = origin_df1[(origin_df1.index >= '2006-01-01') & (origin_df1.index < '2007-01-01')]
    # df2 = origin_df2[(origin_df2.index >= '2006-01-01') & (origin_df2.index < '2007-01-01')]
    df1 = origin_df1
    df2 = origin_df2
    x_range_candidate_items = [origin_df1.index.min(), origin_df1.index.max(), origin_df2.index.min(), origin_df2.index.max()]
    x_range_min = None
    x_range_max = None
    for item in x_range_candidate_items:
        if x_range_min == None or item < x_range_min:
            x_range_min = item

        if x_range_max == None or item > x_range_max:
            x_range_max = item

    x_range_end = x_range_min + datetime.timedelta(days=365)
    pre_x_range_start_time = x_range_min
    pre_x_range_end_time = x_range_end
    df1 = origin_df1[(origin_df1.index >= x_range_min) & (origin_df1.index < x_range_end)]
    df2 = origin_df2[(origin_df2.index >= x_range_min) & (origin_df2.index < x_range_end)]
    data = pd.concat([df1, df2], axis=1)
    #data = data.dropna()
    data['t1'] = data[t1]
    data['t2'] = data[t2]
    data['t1_returns'] = data[t1+'_returns']
    data['t2_returns'] = data[t2+'_returns']
    return data

def callback_plot_pan(event):
    print("Fire pan event on plot object.")
    # print('PanEvent.X = ' + event.x)
    pass


def callback_plot_panstart(event):
    print("Fire pan start event on plot object.")
    # pan_start_time = datetime.datetime.fromtimestamp(event.x / 1000).strftime('%Y-%m-%d %H:%M:%S')
    # print('PanStartEvent.X = ' + str(event.x) + ", " + pan_start_time)


def callback_plot_panend(event):
    print("Fire pan end event on plot object.")
    pan_end_time = datetime.datetime.fromtimestamp(event.x / 1000).strftime('%Y-%m-%d %H:%M:%S')
    print('PanEndEvent.X = ' + str(event.x) + ", " + pan_end_time)
    cur_plot = curdoc().get_model_by_id(event._model_id)
    x_range_start = cur_plot.x_range.start
    x_range_end = cur_plot.x_range.end
    x_range_start_time = datetime.datetime.fromtimestamp(x_range_start / 1000 - 28800)
    x_range_end_time = datetime.datetime.fromtimestamp(x_range_end / 1000 - 28800)
    print('Plot.xrange.start_time = ' + x_range_start_time.strftime('%Y-%m-%d %H:%M:%S'))
    print('Plot.xrange.end_time = ' + x_range_end_time.strftime('%Y-%m-%d %H:%M:%S'))

    t1, t2 = ticker1.value, ticker2.value
    global origin_df1
    global origin_df2
    global pre_x_range_start_time
    global pre_x_range_end_time

    print('Previous.xrange.start_time = ' + pre_x_range_start_time.strftime('%Y-%m-%d %H:%M:%S'))
    print('Previous.xrange.end_time = ' + pre_x_range_end_time.strftime('%Y-%m-%d %H:%M:%S'))

    if x_range_start_time < (pre_x_range_start_time - datetime.timedelta(days=1)):
        print('Back')

    if (pre_x_range_end_time + datetime.timedelta(days=1)) < x_range_end_time:
        print('Forward')
        df1 = origin_df1[(origin_df1.index >= pre_x_range_end_time) & (origin_df1.index < x_range_end_time)]
        df2 = origin_df2[(origin_df2.index >= pre_x_range_end_time) & (origin_df2.index < x_range_end_time)]

        pre_x_range_start_time = x_range_start_time
        pre_x_range_end_time = x_range_end_time

        new_df = pd.concat([df1, df2], axis=1)
        # data = data.dropna()
        new_df['t1'] = new_df[t1]
        new_df['t2'] = new_df[t2]
        new_df['t1_returns'] = new_df[t1 + '_returns']
        new_df['t2_returns'] = new_df[t2 + '_returns']

        if new_df.empty == True:
            return
        else:
            print("Reload new data: %s rows" % new_df.size)

        source.stream({
            'date': new_df.index,
            't1': new_df['t1'],
            't2': new_df['t2'],
            't1_returns': new_df['t1_returns'],
            't2_returns': new_df['t2_returns']
        })
        source_static.stream({
            'date': new_df.index,
            't1': new_df['t1'],
            't2': new_df['t2'],
            't1_returns': new_df['t1_returns'],
            't2_returns': new_df['t2_returns']
        })

# set up widgets

stats = PreText(text='', width=500)
ticker1 = Select(value='AAPL', options=nix('GOOG', DEFAULT_TICKERS))
ticker2 = Select(value='GOOG', options=nix('AAPL', DEFAULT_TICKERS))

# set up plots

source = ColumnDataSource(data=dict(date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
source_static = ColumnDataSource(data=dict(date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
tools = 'pan,wheel_zoom,xbox_select,reset'

corr = figure(plot_width=350, plot_height=350,
              tools='pan,wheel_zoom,box_select,reset')
corr.circle('t1_returns', 't2_returns', size=2, source=source,
            selection_color="orange", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)

ts1 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
ts1.line('date', 't1', source=source_static)
ts1.circle('date', 't1', size=1, source=source, color=None, selection_color="red")

ts1.on_event(Pan, callback_plot_pan)
ts1.on_event(PanStart, callback_plot_panstart)
ts1.on_event(PanEnd, callback_plot_panend)

ts2 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
ts2.x_range = ts1.x_range
ts2.line('date', 't2', source=source_static)
ts2.circle('date', 't2', size=1, source=source, color=None, selection_color="green")

ts2.on_event(Pan, callback_plot_pan)
ts2.on_event(PanStart, callback_plot_panstart)
ts2.on_event(PanEnd, callback_plot_panend)

# set up callbacks

def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()

def update(selected=None):
    t1, t2 = ticker1.value, ticker2.value

    df = get_data(t1, t2)
    data = df[['t1', 't2', 't1_returns', 't2_returns']]
    source.data = data
    source_static.data = data

    corr.title.text = '%s returns vs. %s returns' % (t1, t2)
    ts1.title.text, ts2.title.text = t1, t2

def update_stats(data, t1, t2):
    stats.text = str(data[[t1, t2, t1+'_returns', t2+'_returns']].describe())

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)

def selection_change(attrname, old, new):
    t1, t2 = ticker1.value, ticker2.value
    data = get_data(t1, t2)
    selected = source.selected.indices
    if selected:
        data = data.iloc[selected, :]
    update_stats(data, t1, t2)

source.selected.on_change('indices', selection_change)

button = Button(label="Download", button_type="success")
button.js_on_click(CustomJS(args=dict(source=source),
                            code=open(join(dirname(__file__), "download.js")).read()))
columns = [
    TableColumn(field="t1", title="t1"),
    TableColumn(field="t2", title="t2"),
    TableColumn(field="t1_returns", title="t1_returns"),
    TableColumn(field="t2_returns", title="t2_returns")
]

data_table = DataTable(source=source, columns=columns, width=900, auto_edit=True, editable=True)

# set up layout
# widgets = column(ticker1, ticker2, stats)
# main_row = row(corr, widgets)
# series = column(ts1, ts2, data_table, button)
# layout = column(main_row, series)
#curdoc().add_root(layout)

t1, t2 = ticker1.value, ticker2.value
origin_df1 = load_ticker(t1)
origin_df2 = load_ticker(t2)
origin_df = pd.concat([origin_df1, origin_df2], axis=1)
origin_df['t1'] = origin_df[t1]
origin_df['t2'] = origin_df[t2]
origin_df['t1_returns'] = origin_df[t1 + '_returns']
origin_df['t2_returns'] = origin_df[t2 + '_returns']

from holoviews.operation.datashader import datashade
import holoviews as hv
renderer = hv.renderer('bokeh').instance(mode='server')
ts_hv1 = hv.Curve(origin_df, kdims=['date'], vdims=['t1']).opts(height=500, width=1800)
ts_hv2 = hv.Curve(origin_df, kdims=['date'], vdims=['t2']).opts(height=500, width=1800)
ts1_plot = datashade(ts_hv1 * ts_hv2).opts(height=200, width=900)
# ts1_plot = ts_hv
plot_map_rendered = renderer.get_plot(ts1_plot, curdoc())
# curdoc().add_root(plot_map_rendered.state)

update_stats(origin_df, t1, t2)

line = column(row(ticker1, ticker2), column(plot_map_rendered.state, row(ts1, ts2)))
# line = column(plot_map_rendered.state)
line.name = 'line'
curdoc().add_root(line)

region = column(corr)
region.name = 'region'
curdoc().add_root(region)

platform =  column(stats)
platform.name = 'platform'
curdoc().add_root(platform)

table = column(data_table, button)
table.name = 'table'
curdoc().add_root(table)

# initialize
update()

curdoc().title = "Stocks"
