from bokeh.io import curdoc
import holoviews as hv
import os
import pandas as pd
import numpy as np
import datashader as ds
from bokeh.models import DatetimeTickFormatter
from bokeh.palettes import Category20
from holoviews.operation.datashader import datashade, dynspread
import holoviews.plotting.bokeh  # noqa (Activate backend)

def read_data():
    t = pd.date_range(start='2017-01-01', freq='1T', periods=1e6)
    x = np.arange(t.size)
    y1 = np.cos(x / 100)
    y2 = 10 + np.sin(x / 100)

    classes = list(range(1, 15))
    class_list = []
    for c in classes:
        class_list += [c] * 100
        cluster = class_list * (t.size // 100 + 1)
    df = pd.DataFrame(data=dict(cluster=cluster[:t.size],
                                T1C1=y1, T1C2=y2),
                      index=t)
    df.index.name = 'time'
    return df

df = read_data()

# Convert index to integer so datashader will work correctly.
df.index = df.index.values.astype(np.int64) / 1e6
class_names = [str(c) for c in sorted(df['cluster'].unique()) if int(c) >= 0]

def apply_formatter(plot, element):
         plot.handles['xaxis'].formatter = DatetimeTickFormatter()

def get_points_data(feature):
    d = {}
    df.index.name = 'time'
    for cluster_num in class_names:
        subset = df.loc[df['cluster'] == int(cluster_num), feature].dropna()
        d[cluster_num] = hv.Points(data=subset.reset_index(), kdims=['time', feature])
    return hv.NdOverlay(d, kdims='k')

spec = {'plot': {'RGB': {'width': 800, 'height': 300,
                              'finalize_hooks': [apply_formatter],
                              # 'tools': 'pan,box_zoom,wheel_zoom,save,hover'
                              }
                      },
             'norm': {'RGB': {'framewise': True}}}

n_clusters = df['cluster'].nunique()
if n_clusters <= 20:
    colors = Category20[n_clusters]
else:
    num_repeats = n_clusters // 20 + 1
    colors = Category20[20] * num_repeats
    colors = colors[:n_clusters]

renderer = hv.Store.renderers['bokeh'].instance(mode='server')
DataSelector = hv.streams.Stream.define('feature', feature='T1C1')
data_stream = DataSelector(feature='T1C1')
dmap_points = hv.DynamicMap(get_points_data, streams=[data_stream])
rangexy = hv.streams.RangeXY(transient=True)
plotsize = hv.streams.PlotSize()
datashaded_points = dynspread(datashade(dmap_points, color_key=colors,
                                             streams=[rangexy, plotsize],
                                             aggregator=ds.count_cat('k'),
                                             min_alpha=0.1
                                             ), threshold=0.5, max_px=10).opts(spec)


renderer = hv.Store.renderers['bokeh'].instance(mode='server')
doc = curdoc()
plot = renderer.get_plot(datashaded_points, doc=doc)

doc.add_root(plot.state)