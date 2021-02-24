import pandas as pd
from yahoo_fin import stock_info
import requests
from datetime import datetime, timedelta
import numpy as np

today = datetime.today().date()

gainers = stock_info.get_day_gainers()


print(gainers[:10])