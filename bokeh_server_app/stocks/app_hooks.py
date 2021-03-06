import sys
from os.path import dirname, exists, join

DATA_DIR = join(dirname(__file__), 'daily')

TICKERS = ['AAPL', 'GOOG', 'INTC', 'BRCM', 'YHOO']

def on_server_loaded(server_context):
    print('bokek server app is started.')
    if not all(exists(join(DATA_DIR, 'table_%s.csv' % x.lower())) for x in TICKERS):
        print()
        print("Due to licensing considerations, you must first run download_sample_data.py to download this data set yourself.")
        print()

        sys.exit(1)
