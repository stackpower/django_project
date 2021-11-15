from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from Option_Trading import settings
import time
import os
import pandas_datareader as pdr
import pandas as pd
import tulipy
import numpy as np
import json
import datetime
import holidays
from dateutil.relativedelta import relativedelta
from yahoo_fin import options
from yahoo_fin import stock_info
from broker_app.models import Account
from broker_app.models import Security
from broker_app.models import Journal
# Create your views here.

class data_model:
    def __init__(self, user_id, security_id):
        self.user_id = user_id
        self.security_id = security_id
        self.history_data = []
        self.bar_data = []
        self.sma_data = []
        self.ratio_data =[]
        self.atr_data = []
        self.long_short_data = []
        self.index_list = []
        self.last_price = {}
        self.symbol_list = []
        self.sector_list = {}
        self.industry_list = {}
        self.long_short_temp = []
        self.low_temp = []
        self.close_temp = []
        #self.relate_data = []

        self.read_security_list()
        self.get_history_data()
        #self.make_download_file()

    def get_history_data(self):
        self.security = Security.objects.filter(id=self.security_id, user_id=self.user_id).values()[0]
        #self.symbol_list = self.security['symbols'].split(",")
        self.rest_date = get_rest_trading_days(self.security['trading_day'])
        #print(self.rest_date)
        #print(self.security['data_size'])
        start_date = self.security['trading_day'] - datetime.timedelta(days=(int((self.rest_date + self.security['data_size']) / 5 + self.rest_date) * 7))
        #print(start_date)
        #print(start_date)
        #print(int((self.rest_date + self.security['data_size']) / 5 + 10) * 7)
        #print("data load start time", datetime.datetime.now())
        #logging.info("data load start time")
        self.history_data = pdr.get_data_yahoo(self.symbol_list, start=start_date, end=datetime.datetime.today())
        #print((self.security['data_size'] + self.rest_date - len(self.history_data.index.tolist())) *7)
        if len(self.history_data.index.tolist()) <= self.security['data_size'] + self.rest_date:
            new_start = start_date - datetime.timedelta(days=(int(self.security['data_size'] + self.rest_date - len(self.history_data.index.tolist())) *7))
            #print(new_start)
            self.history_data = pdr.get_data_yahoo(self.symbol_list, start=new_start, end=datetime.datetime.today())
        #print(self.history_data)
        #print("load data end time", datetime.datetime.now())
        #logging.info("load data end time")
        del self.history_data['Volume']
        del self.history_data['Adj Close']
        self.history_data = self.history_data.iloc[len(self.history_data.index.tolist()) - self.rest_date - self.security['data_size'] or 0:]
        self.history_data = self.history_data.fillna(0)
        self.index_list = list(self.history_data.index.tolist())
        #print(len(self.index_list))
        #logging.info("cal start time")
        #print(len(self.index_list))
        if self.security['type'] == "STOCK":
            for symbol in self.symbol_list:
                try:
                    '''
                    temp_data = pdr.get_data_yahoo(symbol, start=start_date, end=datetime.datetime.today())
                    del temp_data['Volume']
                    del temp_data['Adj Close']
                    date_list = temp_data.index.tolist()
                    data_size = len(date_list)
                    #print("symbol data size", data_size)
                    if data_size > self.rest_date + self.security['data_size']:
                        temp_data = temp_data.iloc[data_size - self.rest_date - self.security['data_size']:]
                    # temp_dict = temp_data.to_dict()
                    # print(temp_data)
                    #self.history_data.append({
                    #    "symbol": symbol,
                    #    "data": temp_data
                    #})
                    #print(len(temp_data['Open'].values))
                    high_list = []
                    low_list = []
                    close_list = []
                    for i in range(self.rest_date, self.rest_date + self.security['data_size']):
                        high_list.append(max([temp_data['High'].values[j] for j in range(i-self.rest_date,i)]))
                        low_list.append(min([temp_data['Low'].values[j] for j in range(i-self.rest_date,i)]))
                        close_list.append(min([temp_data['Close'].values[j] for j in range(i-self.rest_date,i)]))
                    
                    if self.rest_date > 0:
                        data = {
                            "Open": list(tulipy.sma(temp_data['Open'].values, self.rest_date)),
                            "High": high_list,
                            "Low": low_list,
                            "Close": close_list
                        }
                    else:
                        data = {
                            "Open": list(temp_data['Open'].values),
                            "High": list(temp_data['High'].values),
                            "Low": list(temp_data['Low'].values),
                            "Close": list(temp_data['Close'].values)
                        }
                        '''
                    high_list = []
                    low_list = []
                    close_list = []
                    high_temp = []
                    low_temp = []
                    np_high = np.array(self.history_data['High'][symbol].values)
                    np_low = np.array(self.history_data['Low'][symbol].values)
                    np_close = np.array(self.history_data['Close'][symbol].values)
                    #print(self.history_data['High'][symbol].values)
                    #print(np_high)

                    for i in range(self.rest_date, self.rest_date + self.security['data_size']+1):
                        #print([np_high[j] for j in range(i - self.rest_date, i)])
                        high_list.append(max([np_high[j] for j in range(i - self.rest_date, i)]))
                        low_list.append(min([np_low[j] for j in range(i - self.rest_date, i)]))
                        close_list.append(min([np_close[j] for j in range(i - self.rest_date, i)]))

                    ############# temp for long short data ##################
                    for i in range(self.rest_date, self.rest_date + self.security['data_size']):
                        high_temp.append(max([np_high[j] for j in range(i - self.rest_date, i+1)]))
                        low_temp.append(min([np_low[j] for j in range(i - self.rest_date, i+1)]))

                    self.long_short_temp.append({
                        "symbol": symbol,
                        "high": high_temp,
                        "low": low_temp,
                        "close": np_close.tolist()
                    })

                    #for i in range(self.rest_date, self.rest_date + self.security['data_size'] + 1):
                    #    high_list.append(max([self.history_data['High'][symbol].values[j] for j in range(i - self.rest_date, i)]))
                    #    low_list.append(min([self.history_data['Low'][symbol].values[j] for j in range(i - self.rest_date, i)]))
                    #    close_list.append(min([self.history_data['Close'][symbol].values[j] for j in range(i - self.rest_date, i)]))
                    #print("hlc data end time", datetime.datetime.now())
                    if self.rest_date > 0:
                        data = {
                            "Open": list(tulipy.sma(self.history_data['Open'][symbol].values, self.rest_date)),
                            "High": high_list,
                            "Low": low_list,
                            "Close": close_list
                        }
                        #print("o data end time", datetime.datetime.now())
                    else:
                        data = {
                            "Open": list(self.history_data['Open'][symbol].values),
                            "High": list(self.history_data['High'][symbol].values),
                            "Low": list(self.history_data['Low'][symbol].values),
                            "Close": list(self.history_data['Close'][symbol].values)
                        }
                    #print("222222222222222222222222222")
                    self.bar_data.append({
                        "symbol": symbol,
                        "data": data
                    })
                    #print("33333333333333333333333333")
                    #print(self.bar_data)
                    self.sma_data.append({
                        "symbol": symbol,
                        "data": data['Close']
                    })
                    #print("44444444444444444444444")
                    #print(self.sma_data)
                    self.last_price[symbol] = self.history_data['Close'][symbol].values[-1]
                except Exception as e:
                    print("bar sheet error")
                    print(e)
                    pass

            #print("bar sheet end time", datetime.datetime.now())
            #logging.info("bar sheet end time")
            #print([item['symbol'] for item in self.bar_data])
            for i in range(len(self.sma_data)):
                bbb = []
                if i > 0:
                    for k in range(i):
                        bbb.append(0)
                bbb.append(1.0)
                for j in range(i + 1, len(self.sma_data)):
                    aaa = np.corrcoef(self.sma_data[i]['data'], self.sma_data[j]['data'])
                    bbb.append(aaa[0][1])
                self.ratio_data.append({
                    "symbol": self.sma_data[i]['symbol'],
                    "data": bbb
                })
            #print("ratio end time", datetime.datetime.now())
            #print(self.ratio_data)
            temp_ratio_dict = {}
            for item1 in self.ratio_data:
                for i in range(len(item1['data'])):
                    if item1['data'][i] != 1 and item1['data'][i] != 0:
                        temp_ratio_dict["{}:{}".format(item1['symbol'], self.symbol_list[i])] = item1['data'][i]
            temp1 = {k: v for k, v in sorted(temp_ratio_dict.items(), key=lambda item: item[1])}
            #print(temp1)
            self.relate_data = [[list(temp1)[0], list(temp1.values())[0]], [list(temp1)[1], list(temp1.values())[1]], [list(temp1)[2], list(temp1.values())[2]], [list(temp1)[-1], list(temp1.values())[-1]], [list(temp1)[-2], list(temp1.values())[-2]], [list(temp1)[-3], list(list(temp1.values()))[-3]]]
            #print(self.relate_data)

            '''
            for symbol_data in self.bar_data:
                short_data = []
                long_data = []
                for i in range(len(self.sma_data[0]['data'])):
                    if i > 0:
                        short = max(symbol_data['data']['High'][i] - symbol_data['data']['Low'][i],
                                    abs(symbol_data['data']['High'][i] - symbol_data['data']['Close'][i - 1]),
                                    abs(symbol_data['data']['Low'][i] - symbol_data['data']['Close'][i - 1]))
                    else:
                        short = symbol_data['data']['High'][i] - symbol_data['data']['Low'][i]
                    long = abs(float(symbol_data['data']['Open'][i] - symbol_data['data']['Close'][i]))
                    short_data.append(float(format(short, '.4f')))
                    long_data.append(float(format(long, '.4f')))
                self.long_short_data.append({
                    "symbol": symbol_data['symbol'],
                    "data": {
                        "short": short_data,
                        "long": long_data
                    }
                })
            #print("long short end time", datetime.datetime.now())
            #print(self.long_short_data)
            '''
            ################################# long short temp #######################################



            ################################# long short sheet ######################################
            '''
            for j in range(len(self.bar_data)):
                symbol_data = self.bar_data[j]
                short_data = []
                long_data = []
                if len(self.sma_data[0]['data']) > self.rest_date and self.rest_date > 0:
                    #for i in range(self.rest_date, len(self.sma_data[0]['data'])):
                    for i in range(self.rest_date, len(self.sma_data[0]['data'])):
                        #long = abs(float(symbol_data['data']['Close'][i]) - float(symbol_data['data']['Close'][i - self.rest_date]))
                        long = abs(float(self.history_data['Close']['Close'][i]) - float(symbol_data['data']['Close'][i - self.rest_date]))
                        short = max(abs(float(symbol_data['data']['High'][i]) - float(symbol_data['data']['Close'][i - self.rest_date])), abs(float(symbol_data['data']['Low'][i]) - float(symbol_data['data']['Close'][i - self.rest_date])), long)
                        long_data.append(float(format(long, '.4f')))
                        short_data.append(float(format(short, '.4f')))
                    self.long_short_data.append({
                        "symbol": symbol_data['symbol'],
                        "data": {
                            "short": short_data,
                            "long": long_data
                        }
                    })
            '''
            #print(len(self.long_short_temp[0]['high']), len(self.long_short_temp[0]['close']))
            for symbol_data in self.long_short_temp:
                short_data = []
                long_data = []
                for i in range(len(symbol_data['high'])):
                    #print("1111111111111")
                    long = abs(float(symbol_data['close'][i+self.rest_date]) - float(symbol_data['close'][i]))
                    #print("22222222222222")
                    short = max(abs(float(symbol_data['high'][i]) - float(symbol_data['close'][i])), abs(float(symbol_data['low'][i]) - float(symbol_data['close'][i])), long)
                    #print("33333333333333333")
                    long_data.append(round(long, 4))
                    short_data.append(round(short, 4))
                self.long_short_data.append({
                    "symbol": symbol_data['symbol'],
                    "data": {
                        "short": short_data,
                        "long": long_data
                    }
                })

            #print("success long_short data", len(self.long_short_data), self.long_short_data)
            '''
            security = Security.objects.filter(id=self.security_id, user_id=self.user_id).values()[0]
            rest_date = get_rest_trading_days(security['expire_date'])
            for i in range(rest_date - 1, len(self.bar_data)):
                symbol_data = self.bar_data[i]
                short_data = []
                long_data = []
                for i in range(len(self.sma_data[0]['data'])):
                    if i > 0:
                        short = max(symbol_data['data']['High'][i] - symbol_data['data']['Low'][i],
                                    abs(symbol_data['data']['High'][i] - symbol_data['data']['Close'][i - 1]),
                                    abs(symbol_data['data']['Low'][i] - symbol_data['data']['Close'][i - 1]))
                    else:
                        short = symbol_data['data']['High'][i] - symbol_data['data']['Low'][i]
                    long = abs(float(symbol_data['data']['Open'][i] - symbol_data['data']['Close'][i]))
                    short_data.append(float(format(short, '.4f')))
                    long_data.append(float(format(long, '.4f')))
                self.long_short_data.append({
                    "symbol": symbol_data['symbol'],
                    "data": {
                        "short": short_data,
                        "long": long_data
                    }
                })
            '''
            ##################################### ATR sheet #########################################
            short_temp = []
            long_temp = []
            for item in self.long_short_data:
                short_min = min(item['data']['short'])
                short_max = max(item['data']['short'])
                long_min = min(item['data']['long'])
                long_max = max(item['data']['long'])
                #print("aaaaaaaaaaaaaaaa")
                #print(item['data']['short'])
                #print(item['data']['long'])
                short_price_unit = (short_max - short_min) / 90
                long_price_unit = (long_max - long_min) / 90
                short_last = item['data']['short'][-1] or 0.0
                long_last = item['data']['long'][-1] or 0.0
                try:
                    if short_last == short_max:
                        short_percent = 95
                    else:
                        short_percent = (short_last - short_min) / (short_max - short_min) * 90 + 5
                except:
                    short_percent = 5.0
                try:
                    if long_last == long_max:
                        long_percent = 95
                    else:
                        long_percent = (long_last - long_min) / (long_max - long_min) * 90 + 5
                except:
                    long_percent = 5.0
                #print("cccccccccccccccccccccccc")
                short_temp.append(short_percent)
                long_temp.append(long_percent)
                self.atr_data.append({
                    "symbol": item['symbol'],
                    "short": {
                        "max": short_max,
                        "min": short_min,
                        "price_percent": float(format(short_price_unit, '.4f')),
                        "last": short_last,
                        "last_percent": float(format(short_percent, '.4f')),

                    },
                    "long":{
                        "max": long_max,
                        "min": long_min,
                        "price_percent": float(format(long_price_unit, '.4f')),
                        "last": long_last,
                        "last_percent": float(format(long_percent, '.4f'))
                    },
                    "last_price": float(format(self.last_price.get(item['symbol']), '.4f'))
                })

            #print("atr end time", datetime.datetime.now())
            #print(self.atr_data)
            self.short_min = format(min(short_temp), '.4f')
            self.short_max = format(max(short_temp), '.4f')
            self.long_min = format(min(long_temp), '.4f')
            self.long_max = format(max(long_temp), '.4f')
            #print(self.atr_data)
            #print("cal end time", datetime.datetime.now())
        else:
            return None

    def make_download_file(self):
        symbol_index = []
        date_index = []
        number_index  = []
        open_data = []
        high_data = []
        low_data = []
        close_data = []
        ratio_min_list = []
        ratio_max_list = []
        ######################### Make Data sheet ###############################
        for item in self.symbol_list:
            for i in range(len(self.index_list)):
                symbol_index.append(item)

        for i in range(len(self.symbol_list)):
            date_index += self.index_list

        for item1 in self.symbol_list:
            open_data += list(self.history_data['Open'][item1].values)
            high_data += list(self.history_data['High'][item1].values)
            low_data += list(self.history_data['Low'][item1].values)
            close_data += list(self.history_data['Close'][item1].values)
            
        df = pd.DataFrame({
            "symbol": symbol_index,
            "Date": date_index,
            "Open": open_data,
            "High": high_data,
            "Low": low_data,
            "Close": close_data
        })

        self.download_data_sheet = df.set_index(["Date", "symbol"]).stack().unstack([1, 2])

        #print("data excel success")
        #self.download_data_sheet.to_excel(settings.MEDIA_ROOT + "/security/security_{}_data.xlsx".format(self.security['id']))

        ############################### Make Bars sheet ##########################################
        symbol_index = []
        open_data = []
        high_data = []
        low_data = []
        close_data = []

        for symbol in self.symbol_list:
            for j in range(len(self.bar_data[0]['data']['Open'])):
                symbol_index.append(symbol)
                number_index.append(j+1)

        for bar_data in self.bar_data:
            open_data += bar_data['data']['Open']
            high_data += bar_data['data']['High']
            low_data += bar_data['data']['Low']
            close_data += bar_data['data']['Close']

        df = pd.DataFrame({
            "symbol": symbol_index,
            "Index": number_index,
            "Open": open_data,
            "High": high_data,
            "Low": low_data,
            "Close": close_data
        })

        self.download_bars_sheet = df.set_index(["Index", "symbol"]).stack().unstack([1, 2])
        #print("bar sheet success")
        #print(self.download_bars_sheet)

        ############################# Make Ratios Sheet ####################################
        #self.download_ratios_sheet = pd.DataFrame(self.ratio_data, index=self.symbol_list, columns=self.symbol_list)
        self.download_ratios_sheet = pd.DataFrame(data={item['symbol']: item['data'] for item in self.ratio_data}, index=self.symbol_list)

        #print("ratio excel success")
        #print(self.download_ratios_sheet)
        ############################ Make ATR Sheet #############################################
        symbol_index = []
        number_index = []
        atr_index = []
        short_data = []
        long_data = []
        for item in self.symbol_list:
            for i in range(len(self.long_short_data[0]['data']['short'])):
                symbol_index.append(item)
                number_index.append(i + 1)
        #print(len(symbol_index))
        #print((number_index))
        #for i in range(2):
        #    for j in range(len(self.long_short_data[0]['data']['short'])):
        #        number_index.append(str(j+1))
        for item in self.long_short_data:
            short_data += item['data']['short']
            long_data += item['data']['long']

        df = pd.DataFrame({
            "symbol": symbol_index,
            "Index": number_index,
            "Short": short_data,
            "Long": long_data
        })

        symbol_index = []
        short_data = []
        long_data = []
        for item in self.symbol_list:
            for i in range(5):
                symbol_index.append(item)

        for i in range(len(self.symbol_list)):
            atr_index += ["Max(95%)", "Min(5%)", "$ as 1%", "Last bar", "Last bar in %"]
        #print("ccccccccccccccccccccc")
        #print(self.atr_data[0]['short'])
        for item in self.atr_data:
            short_data += item['short'].values()
            #print(item['data']['short'].values())
            long_data += item['long'].values()
        df1 = pd.DataFrame({
            "symbol": symbol_index,
            "Label": atr_index,
            "Short": short_data,
            "Long": long_data
        })
        self.download_long_short_sheet = df.set_index(["Index", "symbol"]).stack().unstack([1, 2])
        #self.download_atr_sheet1 = self.download_atr_sheet1.sort_index(ignore_index=True)
        self.download_atr_sheet = df1.set_index(["Label", "symbol"]).stack().unstack([1, 2])
        #print("atr excel success")
        #print(settings.STATICFILES_DIRS)
        #################### Write to file ########################
        self.download_data_sheet.to_excel(settings.MEDIA_ROOT + "/security/security_{}_price.xlsx".format(self.security['id']), sheet_name="Data")
        #print("write price file success")
        self.download_bars_sheet.to_excel(settings.MEDIA_ROOT + "/security/security_{}_bars.xlsx".format(self.security['id']), sheet_name="Bars")
        self.download_ratios_sheet.to_excel(settings.MEDIA_ROOT + "/security/security_{}_ratios.xlsx".format(self.security['id']), sheet_name="Ratios")
        self.download_long_short_sheet.to_excel(settings.MEDIA_ROOT + "/security/security_{}_short_long.xlsx".format(self.security['id']), sheet_name="Short Long")
        self.download_atr_sheet.to_excel(settings.MEDIA_ROOT + "/security/security_{}_atr.xlsx".format(self.security['id']), sheet_name="ATR")
        #pd.concat([self.download_atr_sheet1, self.download_atr_sheet2], axis=1).to_excel(settings.MEDIA_ROOT + "/security/security_{}_atr.xlsx".format(self.security['id']))
        #print(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(self.security['id']))
        writer = pd.ExcelWriter(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(self.security['id']), engine="xlsxwriter")
        self.download_data_sheet.to_excel(writer, sheet_name="Data")
        self.download_bars_sheet.to_excel(writer, sheet_name="Bars")
        self.download_ratios_sheet.to_excel(writer, sheet_name="Ratios")
        #pd.concat([self.download_atr_sheet1, self.download_atr_sheet2], axis=1).to_excel(writer, sheet_name="ATR")
        self.download_long_short_sheet.to_excel(writer, sheet_name="Short Long")
        self.download_atr_sheet.to_excel(writer, sheet_name="ATR")
        writer.save()

    def read_security_list(self):
        aaa = pd.read_excel(settings.MEDIA_ROOT + "/security/security_list_{}.xlsx".format(self.security_id))
        self.symbol_list = aaa['Ticker'].tolist()
        bbb = aaa['Sector'].tolist()
        ccc = aaa['Industry'].tolist()
        for i in range(len(self.symbol_list)):
            self.sector_list[self.symbol_list[i]] = bbb[i]
            self.industry_list[self.symbol_list[i]] = ccc[i]
        #self.sector_list = aaa['Sector'].tolist()
        #self.industry_list = aaa['Industry'].tolist()


def get_symbol_list():
    stock_list = []
    cfd_list = []
    cfd_index_list = []
    forex_list = []
    ticker_list = []
    stock_str = ""
    cfd_str = ""
    cfd_index_str = ""
    forex_str = ""

    stock_path = settings.MEDIA_ROOT + "/saxo/stock"
    cfd_path = settings.MEDIA_ROOT + "/saxo/cfd"
    cfd_index_path = settings.MEDIA_ROOT + "/saxo/cfd_index"
    forex_path = settings.MEDIA_ROOT + "/saxo/" + "forex"

    for file in os.listdir(stock_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(stock_path, file)) as ticker_file:
                    data = json.load(ticker_file)
                ticker_list = data['ticker']
                for ticker in ticker_list.split(','):
                    if ticker not in stock_list:
                        stock_list.append(ticker)
                        if stock_str =="":
                            stock_str += ticker
                        else:
                            stock_str += "," + ticker
            except Exception as e:
                print(file)

    for file in os.listdir(cfd_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(cfd_path, file)) as ticker_file:
                    data = json.load(ticker_file)
                ticker_list = data['ticker']
                for ticker in ticker_list.split(','):
                    if ticker not in cfd_list:
                        cfd_list.append(ticker)
                        if cfd_str =="":
                            cfd_str += ticker
                        else:
                            cfd_str += "," + ticker
            except Exception as e:
                print(file)

    for file in os.listdir(cfd_index_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(cfd_index_path, file)) as ticker_file:
                    data = json.load(ticker_file)
                ticker_list = data['ticker']
                for ticker in ticker_list.split(','):
                    if ticker not in cfd_index_list:
                        cfd_index_list.append(ticker)
                        if cfd_index_str =="":
                            cfd_index_str += ticker
                        else:
                            cfd_index_str += "," + ticker
            except Exception as e:
                print(file)

    for file in os.listdir(forex_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(forex_path, file)) as ticker_file:
                    data = json.load(ticker_file)
                ticker_list = data['ticker']
                for ticker in ticker_list.split(','):
                    if ticker not in forex_list:
                        forex_list.append(ticker)
                        if forex_str =="":
                            forex_str += ticker
                        else:
                            forex_str += "," + ticker
            except Exception as e:
                print(file)

    return stock_str, cfd_str, cfd_index_str, forex_str

def get_rest_trading_days(expire_date):
    today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
    time_now = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%H:%M:%S")
    open_time = "09:30:00"
    rest_date = np.busday_count(today_date, expire_date)
    time_delta = datetime.datetime.strptime(open_time, "%H:%M:%S") - datetime.datetime.strptime(time_now, "%H:%M:%S")
    if time_delta.days == 0:
        rest_date += 1
    return rest_date

def write_to_json(data_model, security_id):
    #color_list = {'Basic Materials': '#f44336', 'Conglomerates': '#e91e63', 'Consumer Goods': '#9c27b0', 'Financial': '#673ab7', 'Healthcare': '#', 'Industrial Goods': '#', 'Services': '#', 'Technology': '#', 'Utilities': '', 'Others': ''}
    #color_list = {'Basic Materials': 'red-500', 'Conglomerates': 'pink-500', 'Consumer Goods': 'purple-500', 'Financial': 'deep-purple-500', 'Healthcare': 'indigo-500', 'Industrial Goods': 'blue-500', 'Services': 'cyan-500', 'Technology': 'teal-500', 'Utilities': 'green-500', 'Others': 'lime-500'}
    #color_list = {'Basic Materials': 'text-primary', 'Conglomerates': 'text-success', 'Consumer Goods': 'text-info', 'Financial': 'text-warn', 'Healthcare': 'text-warning', 'Industrial Goods': 'text-danger', 'Services': 'text-accent', 'Technology': 'text-blue', 'Utilities': 'text-white', 'Others': 'text-black'}
    color_list = {'Technology': 'rgba(255, 65, 70, 0.85)', 'Consumer Cyclical': 'rgba(255, 147, 0, 0.85)', 'Communication Services': 'rgba(255, 225, 0, 0.85)', 'Financial': 'rgba(52, 170, 0, 0.85)', 'Healthcare': 'rgba(0, 209, 109, 0.85)', 'Consumer Defensive': 'rgba(24, 163, 224, 0.85)', 'Energy': 'rgba(89, 99, 209, 0.85)', 'Utilities': 'rgba(148, 37, 194, 0.85)', 'Basic Materials': 'rgba(255, 128, 255, 0.85)', 'Industrials': 'rgba(255, 88, 136, 0.85)', 'Real Estate': 'rgba(255, 65, 70, 0.85)'}
    result = []
    history_data = data_model.history_data
    atr_data = data_model.atr_data
    sector_list = data_model.sector_list
    industry_list = data_model.industry_list
    journal_list = Journal.objects.filter(user_id=data_model.user_id).values()
    #name_list = "<option value=''></option>"
    name_list = []
    for item in journal_list:
        #name_list += "<option value='" + str(item['id']) + "'>" + item['name'] +"</option>"
        name_list.append([item['id'], item['name']])

    for item in atr_data:
        temp_data = {}
        symbol = item['symbol']
        last_price = history_data['Close'][symbol].values.tolist()[-1]
        long_last_price = float(format(item['long']['last'], '.2f'))
        short_last_price = float(format(item['short']['last'], '.2f'))
        '''
        try:
            call_option_price = 0
            put_option_price = 0
            option_price = 0
            call_open_interest = 0
            put_open_interest = 0
            chain = options.get_options_chain(symbol,  str(Security.objects.filter(id=security_id).values()[0]['trading_day']))
            calls = chain['calls'].values.tolist()
            calls_column = [item for item in chain['calls']]
            puts = chain['puts'].values.tolist()
            puts_column = [item for item in chain['puts']]
            for i in range(len(calls) - 1):
                if last_price > calls[i][calls_column.index("Strike")] and last_price <= calls[i + 1][calls_column.index("Strike")]:
                    call_option_price = (calls[i + 1][calls_column.index("Ask")] + calls[i + 1][calls_column.index("Bid")]) / 2
                    #call_strike_price = calls[i][calls_column.index("Strike")]
                    call_open_interest = calls[i + 1][calls_column.index("Open Interest")]
                    break
            for i in range(len(puts) - 1):
                if last_price > puts[i][puts_column.index("Strike")] and last_price <= puts[i + 1][puts_column.index("Strike")]:
                    put_option_price = (puts[i][puts_column.index("Ask")] + puts[i][puts_column.index("Bid")]) / 2
                    put_open_interest = puts[i][puts_column.index("Open Interest")]
                    break
            option_price = float(format(call_option_price + put_option_price, '.2f'))
            if long_last_price >= option_price:
                #temp_data['alert'] = '<span class="text-blue">' + str(option_price) + '</span>'
                temp_data['alert'] = ["text-blue", str(option_price)]
            elif long_last_price < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) / 4):
                #temp_data['alert'] = '<span class="text-primary">' + str(option_price) + '</span>'
                temp_data['alert'] = ["text-primary", str(option_price)]
            elif (long_last_price + (short_last_price - long_last_price) / 4) < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) / 2):
                ##temp_data['alert'] = '<span class="text-warn">' + str(option_price) + '</span>'
                temp_data['alert'] = ["text-warn", str(option_price)]
            elif(long_last_price + (short_last_price - long_last_price) / 2) < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) * 3 / 4):
                #temp_data['alert'] = '<span class="text-warning">' + str(option_price) + '</span>'
                temp_data['alert'] = ["text-warning", str(option_price)]
            elif (long_last_price + (short_last_price - long_last_price) * 3 / 4) < option_price and option_price <= short_last_price:
                #temp_data['alert'] = '<span class="text-danger">' + str(option_price) + '</span>'
                temp_data['alert'] = ["text-danger", str(option_price)]
            elif short_last_price < option_price:
                #temp_data['alert'] = '<span class="text-accent">' + str(option_price) + '</span>'
                temp_data['alert'] = ["text-accent", str(option_price)]
            else:
                #temp_data['alert'] = "No Signal"
                temp_data['alert'] = ["", "No Signal"]
            temp_data['call_open'] = call_open_interest
            temp_data['put_open'] = put_open_interest
        except Exception as e:
            temp_data['alert'] = ["", "No Signal"]
            temp_data['call_open'] = "No Value"
            temp_data['put_open'] = "No Value"
            pass
        '''
        #temp_data['symbol'] = '<span class="' + color_list[sector_list[item['symbol']]] + '" title="' + industry_list[item['symbol']] + '">' + item['symbol'] + '</span>'
        temp_data['symbol'] = [color_list[sector_list[item['symbol']]], industry_list[item['symbol']], item['symbol']]
        #print(temp_data['symbol'])
        temp_data['sector'] = sector_list[item['symbol']]
        temp_data['last_price'] = format(item['last_price'], '.2f')
        temp_data['beta'] = stock_info.get_quote_table(item['symbol'])['Beta (5Y Monthly)']
        temp_data['short_min'] = format(item['short']['min'], '.2f')
        temp_data['short_max'] = format(item['short']['max'], '.2f')
        #temp_data['short_price_percent'] = format(item['short']['price_percent'], '.2f')
        temp_data['short_last'] = format(item['short']['last'], '.2f')
        temp_data['short_last_percent'] = format(item['short']['last_percent'], '.2f')
        temp_data['action1'] = name_list
        #temp_data['action1'] = '<select style="background-color: rgb(72,87,103);" class="form-control" id="' + 'watchlist_' + str(security_id) + '_' + item["symbol"] + '_short' + '" onchange="add_symbol_to_watchlist(\'' + str(security_id) + '\',\'' + item["symbol"] + '\',\'short\')">{}</select>'.format(name_list)
        # temp_data['action1'] = "<select required style='background-color: rgb(72,87,103);' class='form-control' id='" + "watchlist_" + format(security_id) + "_" + item['symbol'] + "_short" + "' onclick='add_symbol_to_watchlist(\'" + format(security_id) + "\',\'" + item['symbol'] + "\',short)'>{}</select>".format(name_list)
        # temp_data['action1'] = '<select required style="background-color: rgb(72,87,103);" class="form-control" id="{}" onclick="add_symbol_to_watchlist({}, {}, {})">{}</select>'.format("watchlist_" + format(security_id) + "_" + item["symbol"] + "_short", format(security_id), item["symbol"], "short", name_list)
        try:
            temp_data['s_l'] = format(item['short']['last'] / item['long']['last'], '.2f')
        except:
            temp_data['s_l'] = "0"
        temp_data['long_min'] = format(item['long']['min'], '.2f')
        temp_data['long_max'] = format(item['long']['max'], '.2f')
        #temp_data['long_price_percent'] = format(item['long']['price_percent'], '.2f')
        temp_data['long_last'] = format(item['long']['last'], '.2f')
        temp_data['long_last_percent'] = format(item['long']['last_percent'], '.2f')
        #temp_data['action2'] = '<select style="background-color: rgb(72,87,103);" class="form-control" id="' + 'watchlist_' + str(security_id) + '_' + item["symbol"] + '_long' + '" onchange="add_symbol_to_watchlist(\'' + str(security_id) + '\',\'' + item["symbol"] + '\',\'long\')">{}</select>'.format(name_list)
        temp_data['action2'] = name_list
        result.append(temp_data)

    return result
    #print("eeeeeeeeeeeeeeee")
    #result_json = {"aaData": result}
    #path = settings.MEDIA_ROOT + "/security/security_" + str(security_id) + ".json"

    #print(path)
    #with open(path, 'w', encoding="utf-8") as f:
    #    json.dump(result_json, f)

def get_security_symbol_count(id):
    aaa = pd.read_excel(settings.MEDIA_ROOT + "/security/security_list_{}.xlsx".format(id))
    bbb = aaa['Ticker'].tolist()
    #print(bbb)
    return len(bbb)

def check_security(import_file):
    try:
        aaa = pd.read_excel(import_file)
        #print("check security result", aaa)
        if "Ticker" in aaa and "Sector" in aaa and "Industry" in aaa:
            bbb = aaa['Ticker'].tolist()
            for item1 in bbb:
                if bbb.count(item1) > 1:
                    return False
            return True
        else:
            return False
    except:
        return False


############## URL Request ##################
def login(request):
    template = loader.get_template('pages/landingpage/login.html')
    context = {}
    return HttpResponse(template.render(context, request))

def login_account(request):
    if request.method == "POST":
        user_name = request.POST['user_name']
        password = request.POST['password']
        try:
            #id = Account.objects.filter(user_id=user_name, password=password).values("id")
            #status = Account.objects.filter(user_id=user_name, password=password).values("status")
            #expire_date = Account.objects.filter(user_id=user_name, password=password).values("expire_date")
            account = Account.objects.filter(user_id=user_name, password=password).values()[0]
        except:
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "Username and Password are incorrect"}
            return HttpResponse(template.render(context, request))
        if account['user_id'] != [] and account['status'] == "enable":
            today = datetime.date.today()
            if account['expire_date'] > today:
                request.session.flush()
                try:
                    del request.session['permission']
                except:
                    pass
                try:
                    del request.session['user_id']
                except:
                    pass
                permission = account['permission']
                request.session['permission'] = permission
                request.session['user_id'] = account['id']
                #request.session.set_expiry(600)
                #s_account = session_account(account['id'])
                #request.session['account'] = s_account
                if permission == 1:
                    #return HttpResponseRedirect(reverse('admin_dashboard'))
                    return redirect('admin_dashboard', id='all')
                elif permission == 2:
                    #return HttpResponseRedirect(reverse('dashboard', id='all'))
                    return redirect('dashboard', id='all')
            else:
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "Your account are expired. Please ask administrator."}
                return HttpResponse(template.render(context, request))

        else:
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "Username and Password are incorrect"}
            return HttpResponse(template.render(context, request))

def dashboard(request, id):
    try:
        permission = request.session['permission']
        #print(permission)
        user_id = request.session['user_id']
        #print(user_id)
        today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
        if permission == 2:
            account = Account.objects.filter(id=user_id).values()[0]
            if id == "all":
                #print("ccccccccccccccccccccccc")
                template = loader.get_template('pages/user/html/dashboard.html')
                #stock_list, cfd_list, cfd_index_list, forex_list = get_symbol_list()
                temp_list = Security.objects.filter(user_id=user_id).values()
                security_list = []
                for security in temp_list:
                    rest_date = get_rest_trading_days(security['trading_day'])
                    #symbol_count = len(security['symbols'].split(","))
                    if rest_date > 0:
                        security['rest_days'] = rest_date
                    else:
                        security['rest_days'] = "Expired"
                    security['symbol_count'] = get_security_symbol_count(security['id'])
                    security_list.append(security)
                request.session['permission'] = 2
                request.session['user_id'] = request.session['user_id']
                context = {
                    "today": today_date,
                    "security_list": security_list,
                    "security_length": len(security_list),
                    #"stock_list": stock_list,
                    #"cfd_list": cfd_list,
                    #"cfd_index_list": cfd_index_list,
                    #"forex_list": forex_list
                }
                return HttpResponse(template.render(context, request))
            elif id == "filter":
                security_id = request.POST['security_id']
                security = Security.objects.filter(id=security_id, user_id=user_id).values()[0]
                data = data_model(user_id, security_id)
                history_data = data.history_data
                color_list = {'Basic Materials': 'text-primary', 'Conglomerates': 'text-success', 'Consumer Goods': 'text-info', 'Financial': 'text-warn', 'Healthcare': 'text-warning', 'Industrial Goods': 'text-danger', 'Services': 'text-accent', 'Technology': 'text-blue', 'Utilities': 'text-white', 'Others': 'text-black'}
                sector_list = data.sector_list
                industry_list = data.industry_list
                journal_list = Journal.objects.filter(user_id=data.user_id).values()
                name_list = "<option value=''></option>"
                for item in journal_list:
                    name_list += "<option value='" + str(item['id']) + "'>" + item['name'] + "</option>"

                template = loader.get_template('pages/user/html/admin_dashboard_view.html')
                short_min = request.POST['short_min']
                short_max = request.POST['short_max']
                long_min = request.POST['long_min']
                long_max = request.POST['long_max']
                operator = request.POST['operator']
                result = []
                atr_data = data.atr_data
                for item in atr_data:
                    temp_data = {}
                    symbol = item['symbol']
                    last_price = history_data['Close'][symbol].values.tolist()[-1]
                    long_last_price = float(format(item['long']['last'], '.2f'))
                    short_last_price = float(format(item['short']['last'], '.2f'))
                    try:
                        call_option_price = 0
                        put_option_price = 0
                        option_price = 0
                        call_open_interest = 0
                        put_open_interest = 0
                        chain = options.get_options_chain(symbol, str(Security.objects.filter(id=security_id).values()[0]['trading_day']))
                        calls = chain['calls'].values.tolist()
                        calls_column = [item for item in chain['calls']]
                        puts = chain['puts'].values.tolist()
                        puts_column = [item for item in chain['puts']]
                        for i in range(len(calls) - 1):
                            if last_price > calls[i][calls_column.index("Strike")] and last_price <= calls[i + 1][calls_column.index("Strike")]:
                                call_option_price = (calls[i + 1][calls_column.index("Ask")] + calls[i + 1][calls_column.index("Bid")]) / 2
                                # call_strike_price = calls[i][calls_column.index("Strike")]
                                call_open_interest = calls[i + 1][calls_column.index("Open Interest")]
                                break
                        for i in range(len(puts) - 1):
                            if last_price > puts[i][puts_column.index("Strike")] and last_price <= puts[i + 1][puts_column.index("Strike")]:
                                put_option_price = (puts[i][puts_column.index("Ask")] + puts[i][puts_column.index("Bid")]) / 2
                                put_open_interest = puts[i][puts_column.index("Open Interest")]
                                break
                        option_price = float(format(call_option_price + put_option_price, '.2f'))
                        if long_last_price >= option_price:
                            # temp_data['alert'] = '<span class="text-blue">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-blue", str(option_price)]
                        elif long_last_price < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) / 4):
                            # temp_data['alert'] = '<span class="text-primary">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-primary", str(option_price)]
                        elif (long_last_price + (short_last_price - long_last_price) / 4) < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) / 2):
                            ##temp_data['alert'] = '<span class="text-warn">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-warn", str(option_price)]
                        elif (long_last_price + (short_last_price - long_last_price) / 2) < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) * 3 / 4):
                            # temp_data['alert'] = '<span class="text-warning">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-warning", str(option_price)]
                        elif (long_last_price + (short_last_price - long_last_price) * 3 / 4) < option_price and option_price <= short_last_price:
                            # temp_data['alert'] = '<span class="text-danger">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-danger", str(option_price)]
                        elif short_last_price < option_price:
                            # temp_data['alert'] = '<span class="text-accent">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-accent", str(option_price)]
                        else:
                            # temp_data['alert'] = "No Signal"
                            temp_data['alert'] = ["", "No Signal"]
                        temp_data['call_open'] = call_open_interest
                        temp_data['put_open'] = put_open_interest
                    except Exception as e:
                        temp_data['alert'] = ["", "No Signal"]
                        temp_data['call_open'] = "No Value"
                        temp_data['put_open'] = "No Value"
                        pass
                    # temp_data['symbol'] = '<span class="' + color_list[sector_list[item['symbol']]] + '" title="' + industry_list[item['symbol']] + '">' + item['symbol'] + '</span>'
                    temp_data['symbol'] = [color_list[sector_list[item['symbol']]], industry_list[item['symbol']], item['symbol']]
                    # print(temp_data['symbol'])
                    temp_data['sector'] = sector_list[item['symbol']]
                    temp_data['last_price'] = format(item['last_price'], '.2f')
                    temp_data['beta'] = stock_info.get_quote_table(item['symbol'])['Beta (5Y Monthly)']
                    temp_data['short_min'] = format(item['short']['min'], '.2f')
                    temp_data['short_max'] = format(item['short']['max'], '.2f')
                    # temp_data['short_price_percent'] = format(item['short']['price_percent'], '.2f')
                    temp_data['short_last'] = format(item['short']['last'], '.2f')
                    temp_data['short_last_percent'] = format(item['short']['last_percent'], '.2f')
                    temp_data['action1'] = name_list
                    # temp_data['action1'] = '<select style="background-color: rgb(72,87,103);" class="form-control" id="' + 'watchlist_' + str(security_id) + '_' + item["symbol"] + '_short' + '" onchange="add_symbol_to_watchlist(\'' + str(security_id) + '\',\'' + item["symbol"] + '\',\'short\')">{}</select>'.format(name_list)
                    # temp_data['action1'] = "<select required style='background-color: rgb(72,87,103);' class='form-control' id='" + "watchlist_" + format(security_id) + "_" + item['symbol'] + "_short" + "' onclick='add_symbol_to_watchlist(\'" + format(security_id) + "\',\'" + item['symbol'] + "\',short)'>{}</select>".format(name_list)
                    # temp_data['action1'] = '<select required style="background-color: rgb(72,87,103);" class="form-control" id="{}" onclick="add_symbol_to_watchlist({}, {}, {})">{}</select>'.format("watchlist_" + format(security_id) + "_" + item["symbol"] + "_short", format(security_id), item["symbol"], "short", name_list)
                    try:
                        temp_data['s_l'] = format(item['short']['last'] / item['long']['last'], '.2f')
                    except:
                        temp_data['s_l'] = "0"
                    temp_data['long_min'] = format(item['long']['min'], '.2f')
                    temp_data['long_max'] = format(item['long']['max'], '.2f')
                    # temp_data['long_price_percent'] = format(item['long']['price_percent'], '.2f')
                    temp_data['long_last'] = format(item['long']['last'], '.2f')
                    temp_data['long_last_percent'] = format(item['long']['last_percent'], '.2f')
                    # temp_data['action2'] = '<select style="background-color: rgb(72,87,103);" class="form-control" id="' + 'watchlist_' + str(security_id) + '_' + item["symbol"] + '_long' + '" onchange="add_symbol_to_watchlist(\'' + str(security_id) + '\',\'' + item["symbol"] + '\',\'long\')">{}</select>'.format(name_list)
                    temp_data['action2'] = name_list
                    # result.append(temp_data)

                    if operator == "and":
                        if (item['short']['last_percent'] >= float(short_min) and item['short']['last_percent'] <= float(short_max)) and (item['long']['last_percent'] >= float(long_min) and item['long']['last_percent'] <= float(long_max)):
                            result.append(temp_data)
                    elif operator == "or":
                        if (item['short']['last_percent'] >= float(short_min) and item['short']['last_percent'] <= float(short_max)) or (item['long']['last_percent'] >= float(long_min) and item['long']['last_percent'] <= float(long_max)):
                            result.append(temp_data)

                # result_json = {"aaData": result}
                # path = settings.MEDIA_ROOT + "/security/security_" + str(security_id) + ".json"
                rest_date = get_rest_trading_days(security['trading_day'])
                # with open(path, 'w', encoding="utf-8") as f:
                #    json.dump(result_json, f)
                temp_security_list = Security.objects.filter(user_id=user_id).values()
                security_list = []
                for item in temp_security_list:
                    temp1 = get_rest_trading_days(item['trading_day'])
                    # symbol_count = len(security['symbols'].split(","))
                    if temp1 > 0:
                        security_list.append(item)

                download_list = {
                    "price": "/media/security/security_{}_price.xlsx".format(security['id']),
                    "bar": "/media/security/security_{}_bars.xlsx".format(security['id']),
                    "correlation": "/media/security/security_{}_ratios.xlsx".format(security['id']),
                    "short_long": "/media/security/security_{}_short_long.xlsx".format(security['id']),
                    "atr": "/media/security/security_{}_atr.xlsx".format(security['id']),
                    "all": "/media/security/security_{}_all.xlsx".format(security['id']),
                }
                context = {
                    "short_min": short_min,
                    "short_max": short_max,
                    "long_min": long_min,
                    "long_max": long_max,
                    "rest_date": rest_date,
                    "security": security,
                    "symbol_list": data.symbol_list,
                    "download_list": download_list,
                    "journal_list": journal_list,
                    "table_data": result,
                    "data_length": len(result),
                    "security_list": security_list,

                }
                return HttpResponse(template.render(context, request))
            else:
                try:
                    security = Security.objects.filter(id=id, user_id=user_id).values()[0]
                    data = data_model(user_id, id)
                    #data.get_history_data()
                    data.make_download_file()
                    rest_date = get_rest_trading_days(security['trading_day'])
                    template = loader.get_template('pages/user/html/dashboard_view.html')
                    table_data = write_to_json(data, security['id'])
                    #download_list = []
                    download_list = {
                        "price": "/media/security/security_{}_price.xlsx".format(security['id']),
                        "bar": "/media/security/security_{}_bars.xlsx".format(security['id']),
                        "correlation": "/media/security/security_{}_ratios.xlsx".format(security['id']),
                        "short_long": "/media/security/security_{}_short_long.xlsx".format(security['id']),
                        "atr": "/media/security/security_{}_atr.xlsx".format(security['id']),
                        "all": "/media/security/security_{}_all.xlsx".format(security['id']),
                    }
                    journal_list = Journal.objects.filter(user_id=user_id).values()
                    temp_security_list = Security.objects.filter(user_id=user_id).values()
                    security_list = []
                    for security in temp_security_list:
                        rest_date = get_rest_trading_days(security['trading_day'])
                        # symbol_count = len(security['symbols'].split(","))
                        if rest_date > 0:
                            security_list.append(security)
                    context = {
                        "id": id,
                        "rest_date": rest_date,
                        "security": security,
                        "symbol_list": data.symbol_list,
                        "download_list": download_list,
                        "journal_list": journal_list,
                        "security_list": security_list,
                        "table_data": table_data,
                        "data_length": len(table_data),
                    }
                    return HttpResponse(template.render(context, request))
                except Exception as e:
                    print("security view error")
                    print(e)
                    request.session.flush()
                    template = loader.get_template('pages/landingpage/login.html')
                    context = {'login_error': "There is a error on calculating volatility. Please ask to administrator"}
                    return HttpResponse(template.render(context, request))
        else:
            return redirect('login')
    except Exception as e:
        print(e)
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def admin_dashboard(request, id):
    try:
        permission = request.session['permission']
        user_id = request.session['user_id']
        today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
        if request.session['permission'] == 1:
            if id == "all":
                template = loader.get_template('pages/user/html/admin_dashboard.html')
                #stock_list, cfd_list, cfd_index_list, forex_list = get_symbol_list()
                temp_list = Security.objects.filter(user_id=user_id).values()

                security_list = []
                for security in temp_list:
                    rest_date = get_rest_trading_days(security['trading_day'])
                    rest_date_1 = get_rest_trading_days(security['expire_date_1'])
                    rest_date_2 = get_rest_trading_days(security['expire_date_2'])
                    rest_date_3 = get_rest_trading_days(security['expire_date_3'])
                    #symbol_count = len(security['symbols'].split(","))
                    if rest_date > 0 :
                        security['trading_day'] = rest_date
                    else:
                        security['trading_day'] = "Expired"
                    if rest_date_1 > 0 :
                        security['expire_date_1'] = rest_date_1
                    else:
                        security['expire_date_1'] = "Expired"
                    if rest_date_2 > 0 :
                        security['expire_date_2'] = rest_date_2
                    else:
                        security['expire_date_2'] = "Expired"
                    if rest_date_3 > 0 :
                        security['expire_date_3'] = rest_date_3
                    else:
                        security['expire_date_3'] = "Expired"
                    #security['symbol_count'] = symbol_count
                    security['symbol_count'] = get_security_symbol_count(security['id'])
                    security_list.append(security)
                '''
                security_list = []
                for security in temp_list:
                    security['symbol_count'] = get_security_symbol_count(security['id'])
                    security_list.append(security)
                '''
                request.session['permission'] = 1
                request.session['user_id'] = request.session['user_id']
                context = {
                    "today": today_date,
                    "security_list": security_list,
                    "security_length": len(security_list),
                    #"stock_list": stock_list,
                    #"cfd_list": cfd_list,
                    #"cfd_index_list": cfd_index_list,
                    #"forex_list": forex_list
                }
                return HttpResponse(template.render(context, request))
            elif id == "filter":
                security_id = request.POST['security_id']
                security = Security.objects.filter(id=security_id, user_id=user_id).values()[0]
                data = data_model(user_id, security_id)
                history_data = data.history_data
                color_list = {'Basic Materials': 'text-primary', 'Conglomerates': 'text-success', 'Consumer Goods': 'text-info', 'Financial': 'text-warn', 'Healthcare': 'text-warning', 'Industrial Goods': 'text-danger', 'Services': 'text-accent', 'Technology': 'text-blue', 'Utilities': 'text-white', 'Others': 'text-black'}
                sector_list = data.sector_list
                industry_list = data.industry_list
                journal_list = Journal.objects.filter(user_id=data.user_id).values()
                name_list = "<option value=''></option>"
                for item in journal_list:
                    name_list += "<option value='" + str(item['id']) + "'>" + item['name'] + "</option>"

                template = loader.get_template('pages/user/html/admin_dashboard_view.html')
                short_min = request.POST['short_min']
                short_max = request.POST['short_max']
                long_min = request.POST['long_min']
                long_max = request.POST['long_max']
                operator = request.POST['operator']
                result = []
                atr_data = data.atr_data
                for item in atr_data:
                    temp_data = {}
                    symbol = item['symbol']
                    last_price = history_data['Close'][symbol].values.tolist()[-1]
                    long_last_price = float(format(item['long']['last'], '.2f'))
                    short_last_price = float(format(item['short']['last'], '.2f'))
                    try:
                        call_option_price = 0
                        put_option_price = 0
                        option_price = 0
                        call_open_interest = 0
                        put_open_interest = 0
                        chain = options.get_options_chain(symbol, str(Security.objects.filter(id=security_id).values()[0]['trading_day']))
                        calls = chain['calls'].values.tolist()
                        calls_column = [item for item in chain['calls']]
                        puts = chain['puts'].values.tolist()
                        puts_column = [item for item in chain['puts']]
                        for i in range(len(calls) - 1):
                            if last_price > calls[i][calls_column.index("Strike")] and last_price <= calls[i + 1][calls_column.index("Strike")]:
                                call_option_price = (calls[i + 1][calls_column.index("Ask")] + calls[i + 1][calls_column.index("Bid")]) / 2
                                # call_strike_price = calls[i][calls_column.index("Strike")]
                                call_open_interest = calls[i + 1][calls_column.index("Open Interest")]
                                break
                        for i in range(len(puts) - 1):
                            if last_price > puts[i][puts_column.index("Strike")] and last_price <= puts[i + 1][puts_column.index("Strike")]:
                                put_option_price = (puts[i][puts_column.index("Ask")] + puts[i][puts_column.index("Bid")]) / 2
                                put_open_interest = puts[i][puts_column.index("Open Interest")]
                                break
                        option_price = float(format(call_option_price + put_option_price, '.2f'))
                        if long_last_price >= option_price:
                            # temp_data['alert'] = '<span class="text-blue">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-blue", str(option_price)]
                        elif long_last_price < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) / 4):
                            # temp_data['alert'] = '<span class="text-primary">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-primary", str(option_price)]
                        elif (long_last_price + (short_last_price - long_last_price) / 4) < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) / 2):
                            ##temp_data['alert'] = '<span class="text-warn">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-warn", str(option_price)]
                        elif (long_last_price + (short_last_price - long_last_price) / 2) < option_price and option_price <= (long_last_price + (short_last_price - long_last_price) * 3 / 4):
                            # temp_data['alert'] = '<span class="text-warning">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-warning", str(option_price)]
                        elif (long_last_price + (short_last_price - long_last_price) * 3 / 4) < option_price and option_price <= short_last_price:
                            # temp_data['alert'] = '<span class="text-danger">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-danger", str(option_price)]
                        elif short_last_price < option_price:
                            # temp_data['alert'] = '<span class="text-accent">' + str(option_price) + '</span>'
                            temp_data['alert'] = ["text-accent", str(option_price)]
                        else:
                            # temp_data['alert'] = "No Signal"
                            temp_data['alert'] = ["", "No Signal"]
                        temp_data['call_open'] = call_open_interest
                        temp_data['put_open'] = put_open_interest
                    except Exception as e:
                        temp_data['alert'] = ["", "No Signal"]
                        temp_data['call_open'] = "No Value"
                        temp_data['put_open'] = "No Value"
                        pass
                    # temp_data['symbol'] = '<span class="' + color_list[sector_list[item['symbol']]] + '" title="' + industry_list[item['symbol']] + '">' + item['symbol'] + '</span>'
                    temp_data['symbol'] = [color_list[sector_list[item['symbol']]], industry_list[item['symbol']], item['symbol']]
                    # print(temp_data['symbol'])
                    temp_data['sector'] = sector_list[item['symbol']]
                    temp_data['last_price'] = format(item['last_price'], '.2f')
                    temp_data['beta'] = stock_info.get_quote_table(item['symbol'])['Beta (5Y Monthly)']
                    temp_data['short_min'] = format(item['short']['min'], '.2f')
                    temp_data['short_max'] = format(item['short']['max'], '.2f')
                    # temp_data['short_price_percent'] = format(item['short']['price_percent'], '.2f')
                    temp_data['short_last'] = format(item['short']['last'], '.2f')
                    temp_data['short_last_percent'] = format(item['short']['last_percent'], '.2f')
                    temp_data['action1'] = name_list
                    # temp_data['action1'] = '<select style="background-color: rgb(72,87,103);" class="form-control" id="' + 'watchlist_' + str(security_id) + '_' + item["symbol"] + '_short' + '" onchange="add_symbol_to_watchlist(\'' + str(security_id) + '\',\'' + item["symbol"] + '\',\'short\')">{}</select>'.format(name_list)
                    # temp_data['action1'] = "<select required style='background-color: rgb(72,87,103);' class='form-control' id='" + "watchlist_" + format(security_id) + "_" + item['symbol'] + "_short" + "' onclick='add_symbol_to_watchlist(\'" + format(security_id) + "\',\'" + item['symbol'] + "\',short)'>{}</select>".format(name_list)
                    # temp_data['action1'] = '<select required style="background-color: rgb(72,87,103);" class="form-control" id="{}" onclick="add_symbol_to_watchlist({}, {}, {})">{}</select>'.format("watchlist_" + format(security_id) + "_" + item["symbol"] + "_short", format(security_id), item["symbol"], "short", name_list)
                    try:
                        temp_data['s_l'] = format(item['short']['last'] / item['long']['last'], '.2f')
                    except:
                        temp_data['s_l'] = "0"
                    temp_data['long_min'] = format(item['long']['min'], '.2f')
                    temp_data['long_max'] = format(item['long']['max'], '.2f')
                    # temp_data['long_price_percent'] = format(item['long']['price_percent'], '.2f')
                    temp_data['long_last'] = format(item['long']['last'], '.2f')
                    temp_data['long_last_percent'] = format(item['long']['last_percent'], '.2f')
                    # temp_data['action2'] = '<select style="background-color: rgb(72,87,103);" class="form-control" id="' + 'watchlist_' + str(security_id) + '_' + item["symbol"] + '_long' + '" onchange="add_symbol_to_watchlist(\'' + str(security_id) + '\',\'' + item["symbol"] + '\',\'long\')">{}</select>'.format(name_list)
                    temp_data['action2'] = name_list
                    #result.append(temp_data)

                    if operator == "and":
                        if (item['short']['last_percent'] >= float(short_min) and item['short']['last_percent'] <= float(short_max)) and (item['long']['last_percent'] >= float(long_min) and item['long']['last_percent'] <= float(long_max)):
                            result.append(temp_data)
                    elif operator == "or":
                        if (item['short']['last_percent'] >= float(short_min) and item['short']['last_percent'] <= float(short_max)) or (item['long']['last_percent'] >= float(long_min) and item['long']['last_percent'] <= float(long_max)):
                            result.append(temp_data)

                #result_json = {"aaData": result}
                #path = settings.MEDIA_ROOT + "/security/security_" + str(security_id) + ".json"
                rest_date = get_rest_trading_days(security['trading_day'])
                #with open(path, 'w', encoding="utf-8") as f:
                #    json.dump(result_json, f)
                temp_security_list = Security.objects.filter(user_id=user_id).values()
                security_list = []
                for item in temp_security_list:
                    temp1 = get_rest_trading_days(item['trading_day'])
                    # symbol_count = len(security['symbols'].split(","))
                    if temp1 > 0:
                        security_list.append(item)

                download_list = {
                    "price": "/media/security/security_{}_price.xlsx".format(security['id']),
                    "bar": "/media/security/security_{}_bars.xlsx".format(security['id']),
                    "correlation": "/media/security/security_{}_ratios.xlsx".format(security['id']),
                    "short_long": "/media/security/security_{}_short_long.xlsx".format(security['id']),
                    "atr": "/media/security/security_{}_atr.xlsx".format(security['id']),
                    "all": "/media/security/security_{}_all.xlsx".format(security['id']),
                }
                context = {
                    "short_min": short_min,
                    "short_max": short_max,
                    "long_min": long_min,
                    "long_max": long_max,
                    "rest_date": rest_date,
                    "security": security,
                    "symbol_list": data.symbol_list,
                    "download_list": download_list,
                    "journal_list": journal_list,
                    "table_data": result,
                    "data_length": len(result),
                    "security_list": security_list,

                }
                return HttpResponse(template.render(context, request))
            else:
                try:
                    #print("3333333333333333333")
                    security = Security.objects.filter(id=id, user_id=user_id).values()[0]
                    '''
                    hist_data = []
                    bar_data = []
                    sma_data = []
                    ratio_data = []
                    atr_data = []
                    symbol_list = security['symbols'].split(",")
                    rest_date = get_rest_trading_days(security['expire_date'])
                    start_date = security['expire_date'] - datetime.timedelta(days=(int((rest_date + security['data_size']) / 5 + 10) * 7))
                    for symbol in symbol_list:
                        temp_data = pdr.get_data_yahoo(symbol, start=start_date, end=datetime.datetime.today())
                        #del temp_data['Volume']
                        #del temp_data['Adj Close']
                        date_list = temp_data.index.tolist()
                        data_size = len(date_list)
                        if data_size > rest_date + security['data_size']:
                            temp_data = temp_data.iloc[data_size - rest_date - security['data_size']:]
                        #temp_dict = temp_data.to_dict()
                        if rest_date > 0:
                            data = {
                                "Open": list(tulipy.sma(temp_data['Open'].values, rest_date)),
                                "High": list(tulipy.sma(temp_data['High'].values, rest_date)),
                                "Low": list(tulipy.sma(temp_data['Low'].values, rest_date)),
                                "Close": list(tulipy.sma(temp_data['Close'].values, rest_date))
                            }
                        else:
                            data = {
                                "Open": list(temp_data['Open'].values),
                                "High": list(temp_data['High'].values),
                                "Low": list(temp_data['Low'].values),
                                "Close": list(temp_data['Close'].values)
                            }
                        bar_data.append({
                            "symbol": symbol,
                            "data": data
                        })
                        sma_data.append({
                            "symbol": symbol,
                            "data": data['Close']
                        })

                    for i in range(len(sma_data)):
                        bbb = []
                        if i > 0:
                            for k in range(i):
                                bbb.append(0)
                        bbb.append(1.0)
                        for j in range(i+1, len(sma_data)):
                            aaa = np.corrcoef(sma_data[i]['data'], sma_data[j]['data'])
                            bbb.append(aaa[0][1])
                        ratio_data.append(bbb)

                    for symbol_data in bar_data:
                        short_data = []
                        long_data = []
                        for i in range(len(sma_data[0]['data'])):
                            if i > 0:
                                short = max(symbol_data['data']['High'][i] - symbol_data['data']['Close'][i], abs(symbol_data['data']['High'][i] - symbol_data['data']['Close'][i-1]), abs(symbol_data['data']['Low'][i] - symbol_data['data']['Close'][i-1]))
                            else:
                                short = symbol_data['data']['High'][i] - symbol_data['data']['Low'][i]
                            long = abs(float(symbol_data['data']['Open'][i] - symbol_data['data']['Close'][i]))
                            short_data.append(short)
                            long_data.append(long)
                        atr_data.append({
                            "symbol": symbol_data['symbol'],
                            "data": {
                                "short": short_data,
                                "long": long_data
                            }
                        })



                        #ratio_data.append([np.corrcoef(sma_data[i]['data'], sma_data[i]['data']), ""]):
                    '''
                    data = data_model(user_id, id)
                    #print("2222222222222222")
                    #data.get_history_data()
                    data.make_download_file()
                    #print("download write end", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    rest_date = get_rest_trading_days(security['trading_day'])
                    template = loader.get_template('pages/user/html/admin_dashboard_view.html')
                    table_data = write_to_json(data, security['id'])
                    #print("write json end", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    #download_list = []
                    download_list = {
                        "price": "/media/security/security_{}_price.xlsx".format(security['id']),
                        "bar": "/media/security/security_{}_bars.xlsx".format(security['id']),
                        "correlation": "/media/security/security_{}_ratios.xlsx".format(security['id']),
                        "short_long": "/media/security/security_{}_short_long.xlsx".format(security['id']),
                        "atr": "/media/security/security_{}_atr.xlsx".format(security['id']),
                        "all": "/media/security/security_{}_all.xlsx".format(security['id']),
                    }
                    journal_list = Journal.objects.filter(user_id=user_id).values()
                    temp_security_list = Security.objects.filter(user_id=user_id).values()
                    security_list = []
                    #print("11111111111111111111111111111")
                    for item in temp_security_list:
                        temp1 = get_rest_trading_days(item['trading_day'])
                        # symbol_count = len(security['symbols'].split(","))
                        if temp1 > 0:
                            security_list.append(item)

                    context = {
                        "id": id,
                        "rest_date": rest_date,
                        #"expire_date": security["expire_date"],
                        "security": security,
                        "symbol_list": data.symbol_list,
                        "download_list": download_list,
                        "journal_list": journal_list,
                        "security_list": security_list,
                        "table_data": table_data,
                        "data_length": len(table_data),
                    }
                    #time.sleep(20)
                    return HttpResponse(template.render(context, request))
                except Exception as e:
                    print("security view error")
                    print(e)
                    request.session.flush()
                    template = loader.get_template('pages/landingpage/login.html')
                    context = {'login_error': "There is a error on calculating volatility. Please ask to administrator"}
                    return HttpResponse(template.render(context, request))
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def admin_user_setting(request):
    if request.session['permission'] == 1:
        user_list = Account.objects.all().values()
        template = loader.get_template('pages/user/html/admin_user_settings.html')
        today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
        context = {
            "today": today_date,
            "user_list": user_list
        }
        return HttpResponse(template.render(context, request))
    else:
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def account_setting(request):
    if request.session['permission'] == 2:
        user_id = request.session['user_id']
        account_info = Account.objects.filter(id=user_id).values()[0]
        template = loader.get_template('pages/user/html/account_setting.html')
        today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
        context = {
            "today": today_date,
            "account_info": account_info
        }
        return HttpResponse(template.render(context, request))
    else:
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def admin_account_setting(request):
    if request.session['permission'] == 1:
        user_id = request.session['user_id']
        account_info = Account.objects.filter(id=user_id).values()[0]
        template = loader.get_template('pages/user/html/admin_account_setting.html')
        today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
        context = {
            "today": today_date,
            "account_info": account_info
        }
        return HttpResponse(template.render(context, request))
    else:
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def account_info_update(request, id):
    if request.method == "POST":
        user_id = request.session['user_id']
        if id == "saxo":
            saxo_token = request.POST['token']
            saxo_account_key = request.POST['account_key']
            Account.objects.filter(id=user_id).update(saxo_token=saxo_token, saxo_account_key=saxo_account_key)
            messages.success(request, "Update Saxo Bank information successfully.")
        #if permission == 1:
        #    return redirect('admin_account_setting')
        #elif permission == 2:
        #    return redirect('account_setting')
        context = {
            "result": "success"
        }
        return JsonResponse(context)


def add_user(request):
    if request.method == "POST":
        if request.session['permission'] == 1:
            sure_name = request.POST['sure_name']
            user_id = request.POST['user_id']
            password = request.POST['password']
            status = request.POST['status']
            phone = request.POST['phone_number']
            expire = request.POST['expire_date']
            ib_name = request.POST['ib_user_name']
            ib_id = request.POST['ib_id']
            ib_port = request.POST['ib_port']
            saxo_token = request.POST['saxo_token']
            saxo_account_key = request.POST['saxo_account_key']
            new_user = Account(sure_name=sure_name, user_id=user_id, password=password, status=status,
                                                 phone_number=phone, expire_date=expire, ib_user_name=ib_name,
                                                 ib_id=ib_id, ib_port=ib_port, saxo_token=saxo_token, saxo_account_key=saxo_account_key)
            new_user.save()
            messages.success(request, "Add new user successfully.")
            return redirect('admin_user_setting')
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to create new user."}
            return HttpResponse(template.render(context, request))

def get_user_info(request):
    if request.method == "POST":
        if request.session['permission'] == 1:
            id = request.POST['id']
            user = Account.objects.filter(id=id).values()[0]
            context = {
                "user": user
            }
            return JsonResponse(context)
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def update_user(request):
    if request.method == "POST":
        if request.session['permission'] == 1:
            id = request.POST['edit_id']
            sure_name = request.POST['edit_sure_name']
            user_id = request.POST['edit_user_id']
            password = request.POST['edit_password']
            status = request.POST['edit_status']
            phone = request.POST['edit_phone_number']
            expire = request.POST['edit_expire_date']
            ib_name = request.POST['edit_ib_user_name']
            ib_id = request.POST['edit_ib_id']
            ib_port = request.POST['edit_ib_port']
            saxo_token = request.POST['edit_saxo_token']
            saxo_account_key = request.POST['edit_saxo_account_key']
            Account.objects.filter(id=id).update(sure_name=sure_name, user_id=user_id, password=password, status=status, phone_number=phone, expire_date=expire, ib_user_name=ib_name, ib_id=ib_id, ib_port=ib_port, saxo_token=saxo_token, saxo_account_key=saxo_account_key)
            messages.success(request, "Update user information successfully.")
            return redirect('admin_user_setting')
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def add_security(request):
    if request.method == "POST" :
        try:
            permission = request.session['permission']
            user_id = request.session['user_id']
            #print(permission)
            #print(user_id)
            if permission > 0:
                name = request.POST['security_name']
                security_type = request.POST['security_type']
                trading_day = request.POST['trading_day']
                expire1 = request.POST['expire_date_1']
                expire2 = request.POST['expire_date_2']
                expire3 = request.POST['expire_date_3']
                #symbol = request.POST['symbol_list']
                data_size = request.POST['bar_size']
                import_file = request.FILES['import_file']

                if Security.objects.filter(name=name, user_id=user_id).values():
                    messages.warning(request, " Duplicated security name exist. Don't duplicate same serucirty name")
                    if permission == 1:
                        return redirect('admin_dashboard', id='all')
                    elif permission == 2:
                        return redirect('dashboard', id='all')

                new_security = Security(user_id=user_id, name=name, type=security_type, trading_day=trading_day, expire_date_1=expire1, expire_date_2=expire2, expire_date_3=expire3, data_size=data_size)
                new_security.save()
                security_id = Security.objects.filter(user_id=user_id, name=name).values()[0]['id']
                #print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                #print("security id", security_id)

                #print(import_file.name)
                try:
                    fs = FileSystemStorage(location=settings.MEDIA_ROOT + "/security")
                    # fs = FileSystemStorage()
                    # print(fs.url)
                    # print(import_file.name)
                    fs.save("security_list_{}.xlsx".format(security_id), import_file)
                    # fs.save(import_file.name, import_file)
                    # print("success file save")
                    #messages.success(request, "Add new security successfully.")
                except Exception as e:
                    print(e)
                    Security.objects.filter(id=security_id).delete()
                    messages.warning(request, "There is some issue in creating Security List.")

                if check_security(import_file) == False:
                    Security.objects.filter(id=security_id).delete()
                    os.remove(settings.MEDIA_ROOT + "/security/security_list_{}.xlsx".format(security_id))
                    messages.warning(request, "There is some issue in creating Security List. Please check Excel file with what you are going to create security.")
                    return redirect('admin_dashboard', id='all')
                messages.success(request, "Add new security successfully.")

                #context = {
                #    "permission": permission
                #}
                if permission == 1:
                    return redirect('admin_dashboard', id='all')
                elif permission == 2:
                    return redirect('dashboard', id='all')
            else:
                request.session.flush()
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "You have no permission to connect this link."}
                return HttpResponse(template.render(context, request))

        except Exception as e:
            print(e)
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def update_security(request):
    if request.method == "POST" :
        try:
            permission = request.session['permission']
            user_id = request.session['user_id']
            if permission > 0:
                id = request.POST['id']
                name = request.POST['name']
                security_type = request.POST['type']
                trading_day = request.POST['trading_day']
                expire_1 = request.POST['expire_1']
                expire_2 = request.POST['expire_2']
                expire_3 = request.POST['expire_3']
                #symbol = request.POST['symbol']
                data_size = request.POST['bar_size']
                Security.objects.filter(id=id, user_id=user_id).update(name=name, type=security_type, trading_day=trading_day, expire_date_1=expire_1, expire_date_2=expire_2, expire_date_3=expire_3, data_size=data_size)
                messages.success(request, "Update security successfully.")
                context = {}
                return JsonResponse(context)
            else:
                request.session.flush()
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "You have no permission to connect this link."}
                return HttpResponse(template.render(context, request))

        except:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def update_security_ticker(request):
    if request.method == "POST" :
        try:
            permission = request.session['permission']
            user_id = request.session['user_id']
            if permission > 0:
                id = request.POST['id']
                ticker = request.POST['ticker'].split("|")
                sector = request.POST['sector'].split("|")
                industry = request.POST['industry'].split("|")
                df = pd.DataFrame(data={
                    "Ticker": ticker,
                    "Sector": sector,
                    "Industry": industry,
                })

                #os.remove(settings.MEDIA_ROOT + "/security/security_list_{}.xlsx".format(str(id)))
                df.to_excel(settings.MEDIA_ROOT + "/security/security_list_{}.xlsx".format(id))#, sheet_name="Bars")
                messages.success(request, "Update security successfully.")
                context = {}
                return JsonResponse(context)
            else:
                request.session.flush()
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "You have no permission to connect this link."}
                return HttpResponse(template.render(context, request))

        except Exception as e:
            print(e)
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))


def get_security_info(request):
    if request.method == "POST":
        permission = request.session['permission']
        user_id = request.session['user_id']
        if permission > 0:
            id = request.POST['id']
            security_list = Security.objects.filter(user_id=user_id, id=id).values()
            if security_list == []:
                messages.warning(request, "There is a problem in your action. Please ask Administrator")
                context = {}
            else:
                security = security_list[0]
                request.session['permission'] = permission
                request.session['user_id'] = user_id
                #symbol = security['symbols'].split(",")
                #security['symbols'] = symbol
                security_result = []
                aaa = pd.read_excel(settings.MEDIA_ROOT + "/security/security_list_{}.xlsx".format(security['id']))
                ddd = aaa['Ticker'].tolist()
                bbb = aaa['Sector'].tolist()
                ccc = aaa['Industry'].tolist()
                for i in range(len(ddd)):
                    security_result.append([ddd[i], bbb[i], ccc[i]])
                context = {
                    "security": security,
                    "ticker_list": security_result
                }

            return  JsonResponse(context)
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def delete_security(request, id):
    try:
        user_permission = request.session['permission']
        request.session['permission'] = user_permission
        user_id = request.session['user_id']
        request.session['user_id'] = user_id
    except:
        return HttpResponseRedirect(reverse('login'))
    try:
        user_id = request.session['user_id']
        security_list = Security.objects.filter(user_id=user_id, id=id).values()
        permission = Account.objects.filter(id=user_id).values()[0]['permission']
        if security_list == []:
            messages.warning(request, "There is a problem in deleting security. Please ask Administrator")
        else:
            Security.objects.filter(id=id, user_id=user_id).delete()
            update_journal_when_security_delete(user_id, id)
            os.remove(settings.MEDIA_ROOT + "/security/security_list_{}.xlsx".format(str(id)))
            messages.success(request, "Delete security successfully.")
        #print("journal success")
        if permission == 1:
            return redirect('admin_dashboard', id='all')
        else:
            return redirect('dashboard', id='all')
    except Exception as e:
        print(e)
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "Now you are unauthorized user. Please login with your account."}
        return HttpResponse(template.render(context, request))

def update_journal_when_security_delete(user_id, security_id):
    journal_list = Journal.objects.filter(user_id=user_id).values()
    try:
        for journal in journal_list:
            result = []
            value = ""
            journal_id = journal['id']
            if journal['value'] != "":
                value_list = journal['value'].split(",")
                for item in value_list:
                    id, symbol, side = item.split("_")
                    if id != security_id:
                        result.append(item)
                value = ','.join(result)
            Journal.objects.filter(id=journal_id).update(value=value)
    except Exception as e:
        print(e)


def percentile_filter(request):
    if request.method == "POST":
        security_id = request.POST['security_id']
        short_min = request.POST['short_min']
        short_max = request.POST['short_max']
        long_min = request.POST['long_min']
        long_max = request.POST['long_max']
        operator = request.POST['operator']
        user_id = request.session['user_id']
        data = data_model(user_id, security_id)
        print(operator)
        print(security_id)
        result = []
        atr_data = data.atr_data

        for item in atr_data:
            temp_data = {}
            temp_data['symbol'] = item['symbol']
            temp_data['last_price'] = str(item['last_price'])
            temp_data['short_min'] = str(item['short']['min'])
            temp_data['short_max'] = str(item['short']['max'])
            temp_data['short_price_percent'] = item['short']['price_percent']
            temp_data['short_last'] = str(item['short']['last'])
            temp_data['short_last_percent'] = item['short']['last_percent']
            temp_data['long_min'] = str(item['long']['min'])
            temp_data['long_max'] = str(item['long']['max'])
            temp_data['long_price_percent'] = item['long']['price_percent']
            temp_data['long_last'] = str(item['long']['last'])
            temp_data['long_last_percent'] = item['long']['last_percent']
            if operator == "and":
                if (item['short']['last_percent'] >= short_min and item['short']['last_percent'] <= short_max) and (item['long']['last_percent'] >= long_min and item['long']['last_percent'] <= long_max):
                    result.append(temp_data)
            elif operator == "or":
                if (item['short']['last_percent'] >= short_min and item['short']['last_percent'] <= short_max) or (item['long']['last_percent'] >= long_min and item['long']['last_percent'] <= long_max):
                    result.append(temp_data)

        print(result)
        result_json = {"aaData": result}
        path = settings.TEMPLATES_ROOT + "/pages/user/html/api/security_" + str(security_id) + ".json"
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(result_json, f)

        context = {
            "result": "success"
        }
        return JsonResponse(context)

def symbol_detail_graph(request):
    if request.method == "POST":
        #level = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
        level = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
        user_id = request.session['user_id']
        security_id = request.POST['id']
        rest_date = get_rest_trading_days(Security.objects.filter(id=security_id).values()[0]['trading_day'])
        symbol_list = str(request.POST['symbol']).split(",")
        length = int(request.POST['length'])

        result = []
        graph_price_index = []
        #data = data_model(user_id=user_id, security_id=security_id)
        #for item in level:
        #    long_result[str(item)] = 0
        #    short_result[str(item)] = 0
        aaa = pd.read_excel(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(security_id), sheet_name="Short Long")
        bbb = pd.read_excel(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(security_id), sheet_name="ATR")
        ccc = pd.read_excel(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(security_id), sheet_name="Data")
        ratio_data = pd.read_excel(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(security_id), sheet_name="Ratios")
        ratio_column_list = [item for item in ratio_data]
        del ratio_column_list[0]
        #ratio_index = ratio_data[ratio_column_list[0]].values
        #print("ratio column", ratio_column_list)
        #print(ratio_column_list)
        data_column_list = [name for name in ccc]
        #print([name for name in ccc].index(symbol) + 3)
        index_list = ccc['symbol'].values[2:]
        for item in index_list[-1 * length:]:
            graph_price_index.append(str(item)[:10])
        column_list = []
        for item in aaa:
            column_list.append(item)

        for symbol in symbol_list:
            call_option_price = 0
            put_option_price = 0
            call_open_interest = 0
            put_open_interest = 0
            atr_short = [0, 0, 0, 0, 0]
            atr_long = [0, 0, 0, 0, 0]
            long_result = {}
            short_result = {}
            daily_result = {}
            long_graph_price_data = []
            short_graph_price_data = []
            #long_graph_price_tooltip = []
            #short_graph_price_tooltip = []
            long_graph_level_data = []
            short_graph_level_data = []
            daily_graph_level_data = []
            long_level_sum_data = []
            short_level_sum_data = []
            daily_level_sum_data = []
            daily_data = []
            daily_volatility = []
            temp = {}
            temp['symbol'] = symbol
            for item in level:
                long_result[str(item)] = 0
                short_result[str(item)] = 0
                daily_result[str(item)] = 0
            for i in range(len(column_list)):
                if column_list[i] == symbol:
                    short_data = np.array(aaa[column_list[i]].values[-1 * length:])
                    long_data = np.array(aaa[column_list[i + 1]].values[-1 * length:])
                    atr_short = bbb[column_list[i]].values[2:]
                    atr_long = bbb[column_list[i + 1]].values[2:]
            temp['last_short'] = format(short_data[-1], '.2f')
            temp['last_long'] = format(long_data[-1], '.2f')
            for i in range(len(data_column_list)):
                if data_column_list[i] == symbol:
                    daily_data = [np.array(ccc[data_column_list[i + 1]].values[-1 * length - 1:]), np.array(ccc[data_column_list[i + 2]].values[-1 * length - 1:]), np.array(ccc[data_column_list[i + 3]].values[-1 * length - 1:])]

            temp['stock_price'] = format(daily_data[2][-1], '.2f')
            # print(short_data)
            # print(long_data)
            atr_short[4] = min(short_data)
            atr_short[3] = max(short_data)
            atr_short[0] = float(format((atr_short[3] - atr_short[4]) / 90, '.4f'))
            atr_short[1] = short_data[-1]
            if atr_short[1] == atr_short[3]:
                atr_short[2] = 95
            elif atr_short[1] == atr_short[4]:
                atr_short[2] = 5
            else:
                try:
                    atr_short[2] = float(format((atr_short[1] - atr_short[4]) / atr_short[0], '.4f')) + 5
                except:
                    atr_short[2] = 5


            # print(atr_short)
            atr_long[4] = min(long_data)
            atr_long[3] = max(long_data)
            atr_long[0] = float(format((atr_long[3] - atr_long[4]) / 90, '.4f'))
            atr_long[1] = long_data[-1]
            if atr_long[1] == atr_long[3]:
                atr_long[2] = 95
            elif atr_long[1] == atr_long[4]:
                atr_long[2] = 5
            else:
                try:
                    atr_long[2] = float(format((atr_long[1] - atr_long[4]) / atr_long[0], '.4f')) + 5
                except:
                    atr_long[2] = 5
            '''
            for i in range(len(long_data)):
                if long_data[i] == atr_long[4]:
                    long_result[str(5)] += 1
                    long_graph_price_data.append(long_data[i])
                elif long_data[i] == atr_long[3]:
                    long_result[str(95)] += 1
                    long_graph_price_data.append(long_data[i])
                else:
                    for j in range(1, len(level) - 1):
                        try:
                            temp_per = float(format((long_data[i] - atr_long[4]) / atr_long[0] + 5, '.2f'))
                        except:
                            temp_per = 5
                        if j == 1:
                            if temp_per > level[j] - 5 and temp_per < level[j] + 5:
                                long_result[str(level[j])] += 1
                                # if i >= len(long_data) - length:
                                long_graph_price_data.append(long_data[i])
                                # long_graph_price_per.append(temp_per)
                                break
                        else:
                            if temp_per >= level[j] - 5 and temp_per < level[j] + 5:
                                long_result[str(level[j])] += 1
                                # if i >= len(long_data) - length:
                                long_graph_price_data.append(long_data[i])
                                # long_graph_price_per.append(temp_per)
                                break
            
            for i in range(len(short_data)):
                if short_data[i] == atr_short[4]:
                    short_result[str(5)] += 1
                    short_graph_price_data.append(short_data[i])
                elif short_data[i] == atr_short[3]:
                    short_result[str(95)] += 1
                    short_graph_price_data.append(short_data[i])
                else:
                    for j in range(1, len(level) - 1):
                        try:
                            temp_per = float(format((short_data[i] - atr_short[4]) / atr_short[0] + 5, '.1f'))
                        except:
                            temp_per = 5
                        if j == 1:
                            if temp_per > level[j] - 5 and temp_per < level[j] + 5:
                                short_result[str(level[j])] += 1
                                #if i >= len(short_data) - length:
                                short_graph_price_data.append(short_data[i])
                                    # short_graph_price_per.append(temp_per)
                                break
                        else:
                            if temp_per >= level[j] - 5 and temp_per < level[j] + 5:
                                short_result[str(level[j])] += 1
                                #if i >= len(short_data) - length:
                                short_graph_price_data.append(short_data[i])
                                    # short_graph_price_per.append(temp_per)
                                break
            # print(short_result)
            # print(long_result)
            '''
            for i in range(len(long_data)):
                '''
                if long_data[i] == atr_long[4]:
                    long_result[str(5)] += 1
                    long_graph_price_data.append(long_data[i])
                elif long_data[i] == atr_long[3]:
                    long_result[str(95)] += 1
                    long_graph_price_data.append(long_data[i])
                else:'''
                    #for j in range(len(level) - 1):
                for j in range(len(level)):
                    try:
                        temp_per = float(format((long_data[i] - atr_long[4]) / atr_long[0] + 5, '.2f'))
                    except:
                        temp_per = 5
                    if j == 0:
                        if temp_per >= 5 and temp_per <= 7.5:
                            long_result[str(level[j])] += 1
                            # if i >= len(long_data) - length:
                            long_graph_price_data.append(long_data[i])
                            # long_graph_price_tooltip.append(temp_per)
                            break
                    elif j == (len(level) - 1):
                        if temp_per > 92.5 and temp_per <= 95:
                            long_result[str(level[j])] += 1
                            # if i >= len(long_data) - length:
                            long_graph_price_data.append(long_data[i])
                            # long_graph_price_tooltip.append(temp_per)
                            break
                    else:
                        if temp_per > level[j] - 2.5 and temp_per <= level[j] + 2.5:
                            long_result[str(level[j])] += 1
                            # if i >= len(long_data) - length:
                            long_graph_price_data.append(long_data[i])
                            # long_graph_price_tooltip.append(temp_per)
                            break

            for i in range(len(short_data)):
                '''
                if short_data[i] == atr_short[4]:
                    short_result[str(5)] += 1
                    short_graph_price_data.append(short_data[i])
                elif short_data[i] == atr_short[3]:
                    short_result[str(95)] += 1
                    short_graph_price_data.append(short_data[i])
                else:
                    for j in range(len(level) - 1):
                    '''
                for j in range(len(level)):
                    try:
                        temp_per = float(format((short_data[i] - atr_short[4]) / atr_short[0] + 5, '.1f'))
                    except:
                        temp_per = 5
                    if j == 0:
                        if temp_per >= 5 and temp_per <= 7.5:
                            short_result[str(level[j])] += 1
                            # if i >= len(short_data) - length:
                            short_graph_price_data.append(short_data[i])
                            # short_graph_price_tooltip.append(temp_per)
                            break
                    elif j == (len(level) - 1):
                        if temp_per > 92.5 and temp_per <= 95:
                            short_result[str(level[j])] += 1
                            # if i >= len(short_data) - length:
                            short_graph_price_data.append(short_data[i])
                            # short_graph_price_tooltip.append(temp_per)
                            break
                    else:
                        if temp_per > level[j] - 2.5 and temp_per <= level[j] + 2.5:
                            short_result[str(level[j])] += 1
                            # if i >= len(short_data) - length:
                            short_graph_price_data.append(short_data[i])
                            # short_graph_price_tooltip.append(temp_per)
                            break


            for key, value in long_result.items():
                long_graph_level_data.append(float(format(value / len(long_data) * 100, '.1f')))
            #for i in range(1, len(long_result)):
                #long_graph_level_data[i] += long_graph_level_data[i - 1]
            for key, value in short_result.items():
                val = float(format(value / len(short_data) * 100, '.1f'))
                if val == 0:
                    short_graph_level_data.append(0)
                else:
                    short_graph_level_data.append(-1 * val)
            #for i in range(1, len(short_graph_level_data)):
                #short_graph_level_data[i] += short_graph_level_data[i - 1]
            # print("index list", index_list)

            # print(graph_price_index)
            '''
            for i in range(len(level)):
                if i == 0:
                    if atr_long[2] == 5:
                        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                    if atr_short[2] == 5:
                        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'color': '#6887ff'}
                elif i == len(level) - 1:
                    if atr_long[2] == 95:
                        long_graph_level_data[-1] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                    if atr_short[2] == 95:
                        short_graph_level_data[-1] = {'y': short_graph_level_data[i], 'color': '#6887ff'}
                elif i == 1:
                    if atr_long[2] > 5 and atr_long[2] < 15:
                        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                    if atr_short[2] > 5 and atr_short[2] < 15:
                        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'color': '#6887ff'}
                else:
                    if atr_long[2] >= level[i] - 5 and atr_long[2] < level[i] + 5:
                        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                    if atr_short[2] >= level[i] - 5 and atr_short[2] < level[i] + 5:
                        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'color': '#6887ff'}
            '''

            ################### Daily Volatility ####################
            for i in range(1, len(daily_data[0])):
                # daily_volatility.append(float(format(max(abs(daily_data[0][i] - daily_data[2][i-1]), abs(daily_data[1][i] - daily_data[2][i-1]), abs(daily_data[0][i] - daily_data[1][i])), '.2f')))
                # daily_volatility.append(float(format(max(abs(daily_data[0][i] - daily_data[2][i - 1]), abs(daily_data[1][i] - daily_data[2][i - 1]), abs(daily_data[2][i] - daily_data[2][i - 1])), '.2f')))
                daily_volatility.append(float(format(abs(daily_data[2][i] - daily_data[2][i - 1]), '.2f')))
            daily_min = min(daily_volatility)
            daily_max = max(daily_volatility)

            daily_dif = round((daily_max - daily_min) / 90, 4)
            for i in range(len(daily_volatility)):
                try:
                    temp1 = float(format((daily_volatility[i] - daily_min) / daily_dif + 5, '.1f'))
                except:
                    temp1 = 5
                for j in range(len(level)):
                    if j == 0:
                        if temp1 >= 5 and temp1 <=7.5:
                            daily_result[str(level[j])] += 1
                            break
                    elif j == (len(level) - 1):
                        if temp1 >= 92.5 and temp1 <= 95:
                            daily_result[str(level[j])] += 1
                            break
                    else:
                        if temp1 > (level[j] - 2.5) and temp1 <= (level[j] + 2.5):
                            daily_result[str(level[j])] += 1
                            break

            for key, value in daily_result.items():
                daily_graph_level_data.append(float(format(value / length * 100, '.1f')))

            if daily_volatility[-1] == daily_min:
                last_daily_value = 5
            elif daily_volatility[-1] == daily_max:
                last_daily_value = 95
            else:
                last_daily_value = float(format((daily_volatility[-1] - daily_min) / daily_dif + 5, '.1f'))
            ########################### All Level data ############################
            for i in range(len(level)):
                temp_long_sum = 0
                temp_short_sum = 0
                temp_daily_sum = 0
                if i == 0:
                    #long_level_sum_data[str(level[i]) + '%'] = round(long_graph_level_data[i], 1)
                    long_level_sum_data.append(round(long_graph_level_data[i], 2))
                    #short_level_sum_data[str(level[i]) + '%'] = round(abs(short_graph_level_data[i]), 1)
                    short_level_sum_data.append(round(abs(short_graph_level_data[i]), 2))
                    daily_level_sum_data.append(round(daily_graph_level_data[i], 2))
                else:
                    for j in range(i+1):
                        temp_long_sum += long_graph_level_data[j]
                        temp_short_sum += abs(short_graph_level_data[j])
                        temp_daily_sum += daily_graph_level_data[j]
                    #long_level_sum_data[str(level[i]) + '%'] = round(temp_long_sum, 1)
                    long_level_sum_data.append(round(temp_long_sum, 2))
                    #short_level_sum_data[str(level[i]) + '%'] = round(temp_short_sum, 1)
                    short_level_sum_data.append(round(temp_short_sum, 2))
                    daily_level_sum_data.append(round(temp_daily_sum, 2))
            for i in range(len(level)):
                if i == 0:
                    if atr_long[2] >= 5 and atr_long[2] <= 7.5:
                        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'z': long_level_sum_data[i], 'color': '#fcc100'}
                    else:
                        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'z': long_level_sum_data[i]}
                    if atr_short[2] >= 5 and atr_short[2] <= 7.5:
                        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'z': short_level_sum_data[i], 'color': '#6887ff'}
                    else:
                        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'z': short_level_sum_data[i]}
                    if last_daily_value >= 5 and last_daily_value <= 7.5:
                        daily_graph_level_data[i] = {'y': daily_graph_level_data[i], 'z': daily_level_sum_data[i], 'color': '#6887ff'}
                    else:
                        daily_graph_level_data[i] = {'y': daily_graph_level_data[i], 'z': daily_level_sum_data[i]}
                elif i == len(level) - 1:
                    if atr_long[2] <= 95 and atr_long[2] >= 92.5:
                        long_graph_level_data[-1] = {'y': long_graph_level_data[i], 'z': long_level_sum_data[i], 'color': '#fcc100'}
                    else:
                        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'z': long_level_sum_data[i]}
                    if atr_short[2] <= 95 and atr_short[2] >= 92.5:
                        short_graph_level_data[-1] = {'y': short_graph_level_data[i], 'z': short_level_sum_data[i], 'color': '#6887ff'}
                    else:
                        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'z': short_level_sum_data[i]}
                    if last_daily_value > 92.5 and last_daily_value <= 95:
                        daily_graph_level_data[i] = {'y': daily_graph_level_data[i], 'z': daily_level_sum_data[i], 'color': '#6887ff'}
                    else:
                        daily_graph_level_data[i] = {'y': daily_graph_level_data[i], 'z': daily_level_sum_data[i]}
                #elif i == 1:
                #    if atr_long[2] > 5 and atr_long[2] < 15:
                #        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                #    if atr_short[2] > 5 and atr_short[2] < 15:
                #        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'color': '#6887ff'}
                else:
                    if atr_long[2] > level[i] - 2.5 and atr_long[2] <= level[i] + 2.5:
                        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'z': long_level_sum_data[i], 'color': '#fcc100'}
                    else:
                        long_graph_level_data[i] = {'y': long_graph_level_data[i], 'z': long_level_sum_data[i]}
                    if atr_short[2] > level[i] - 2.5 and atr_short[2] <= level[i] + 2.5:
                        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'z': short_level_sum_data[i], 'color': '#6887ff'}
                    else:
                        short_graph_level_data[i] = {'y': short_graph_level_data[i], 'z': short_level_sum_data[i]}
                    if last_daily_value > (level[i] - 2.5) and last_daily_value <= (level[i] + 2.5):
                        daily_graph_level_data[i] = {'y': daily_graph_level_data[i], 'z': daily_level_sum_data[i], 'color': '#6887ff'}
                    else:
                        daily_graph_level_data[i] = {'y': daily_graph_level_data[i], 'z': daily_level_sum_data[i]}

            #print("short graph price", short_graph_price_data)
            #print("short graph level", short_graph_level_data)
            #print("long graph price", long_graph_price_data)
            #print("long graph level", long_graph_level_data)
            ########################## Get Option prices and Open interest ################################
            symbol_close_price = float(format(ccc[data_column_list[data_column_list.index(symbol) + 3]].values[-1], '.2f'))
            #print(symbol_close_price)
            #i = 0
            '''
            try:
                chain = options.get_options_chain(symbol, str(Security.objects.filter(id=security_id).values()[0]['trading_day']))
                calls = chain['calls'].values.tolist()
                calls_column = [item for item in chain['calls']]
                puts = chain['puts'].values.tolist()
                puts_column = [item for item in chain['puts']]
                for i in range(len(calls) - 1):
                    if symbol_close_price > calls[i][calls_column.index("Strike")] and symbol_close_price <= calls[i + 1][calls_column.index("Strike")]:
                        call_option_price = (calls[i+1][calls_column.index("Ask")] + calls[i+1][calls_column.index("Bid")]) / 2
                        call_open_interest = calls[i+1][calls_column.index("Open Interest")]
                        break
                i = 0
                for i in range(len(puts) - 1):
                    if symbol_close_price > puts[i][puts_column.index("Strike")] and symbol_close_price <= puts[i + 1][puts_column.index("Strike")]:
                        put_option_price = (puts[i][puts_column.index("Ask")] + puts[i][puts_column.index("Bid")]) / 2
                        put_open_interest = puts[i][puts_column.index("Open Interest")]
                        break
                temp['option_price'] = format(call_option_price + put_option_price, '.2f')
                temp['call_open_interest'] = call_open_interest
                temp['put_open_interest'] = put_open_interest
                temp['option_success'] = 'true'
            except Exception as e:
                print(e)
                temp['option_success'] = 'true'
                temp['option_price'] = "No Value"
                temp['call_open_interest'] = "No Value"
                temp['put_open_interest'] = "No Value"
            '''

            temp_ratio_dict = {}
            ratio_temp_data = ratio_data[symbol]
            for i in range(len(ratio_temp_data)):
                if ratio_temp_data[i] == 0:
                    temp_ratio_dict["{}:{}".format(symbol, ratio_column_list[i])] = round(ratio_data[ratio_column_list[i]][ratio_column_list.index(symbol)],6)
                elif ratio_temp_data[i] != 0 and ratio_temp_data[i] != 1:
                    temp_ratio_dict["{}:{}".format(symbol, ratio_column_list[i])] = round(ratio_temp_data[i], 6)
            temp1 = {k: v for k, v in sorted(temp_ratio_dict.items(), key=lambda item: item[1])}
            # print(temp1)
            #correlate_data = [[list(temp1)[0], list(temp1.values())[0]], [list(temp1)[1], list(temp1.values())[1]], [list(temp1)[2], list(temp1.values())[2]], [list(temp1)[-1], list(temp1.values())[-1]], [list(temp1)[-2], list(temp1.values())[-2]], [list(temp1)[-3], list(list(temp1.values()))[-3]]]
            correlate_data = ["{}({})".format(list(temp1)[0], list(temp1.values())[0]), "{}({})".format(list(temp1)[1], list(temp1.values())[1]), "{}({})".format(list(temp1)[2], list(temp1.values())[2]), "{}({})".format(list(temp1)[-1], list(temp1.values())[-1]), "{}({})".format(list(temp1)[-2], list(temp1.values())[-2]), "{}({})".format(list(temp1)[-3], list(list(temp1.values()))[-3])]
            # print(self.relate_data)
            ################### Historical Price ####################
            for i in range(1,3):
                if rest_date * i <= length:
                    temp['history_data_date_' + str(i)] = graph_price_index[-1 * rest_date * i]
                    temp['history_data_price_' + str(i)] = format(daily_data[2][-1 * rest_date * i], '.2f')
                else:
                    temp['history_data_date_' + str(i)] = graph_price_index[-1 * length]
                    temp['history_data_price_' + str(i)] = format(daily_data[2][-1 * length], '.2f')
                    break
            temp['last_daily_volatility'] = format(daily_volatility[-1], '.2f')

            temp['long_graph_price_data'] = long_graph_price_data
            temp['short_graph_price_data'] = short_graph_price_data
            temp['price_index'] = graph_price_index
            temp['long_graph_level'] = long_graph_level_data
            temp['short_graph_level'] = short_graph_level_data
            temp['long_level_sum'] = long_level_sum_data
            temp['short_level_sum'] = short_level_sum_data
            temp['daily_volatility'] = daily_volatility
            temp['daily_graph_level'] = daily_graph_level_data
            temp['short_min'] = atr_short[4]
            temp['short_dif'] = atr_short[0]
            temp['long_min'] = atr_long[4]
            temp['long_dif'] = atr_long[0]
            temp['daily_min'] = daily_min
            temp['daily_dif'] = daily_dif
            ################################### append 3 high and low correlated tickers ################################
            #temp['high_1'] = "{}({})".format(list(correlate_data)[-1], list(correlate_data.values())[-1])
            #temp['high_2'] = "{}({})".format(list(correlate_data)[-2], list(correlate_data.values())[-2])
            #temp['high_3'] = "{}({})".format(list(correlate_data)[-3], list(correlate_data.values())[-3])
            #temp['low_1'] = "{}({})".format(list(correlate_data)[0], list(correlate_data.values())[0])
            #temp['low_2'] = "{}({})".format(list(correlate_data)[1], list(correlate_data.values())[1])
            #temp['low_3'] = "{}({})".format(list(correlate_data)[2], list(correlate_data.values())[2])
            temp['correlate_data'] = correlate_data
            result.append(temp)
        context = {
            "result": result
        }
        '''
        context = {
            "long_graph_price_data": long_graph_price_data,
            #"long_graph_price_per": long_graph_price_per,
            "short_graph_price_data": short_graph_price_data,
            #"short_graph_price_per": short_graph_price_per,
            "price_index": graph_price_index,
            "long_graph_level": long_graph_level_data,
            "short_graph_level": short_graph_level_data,
        }

        
        print(len(long_graph_price_data), long_graph_price_data)
        print(len(short_graph_price_data), short_graph_price_data)
        print(len(long_graph_level_data), long_graph_level_data)
        print(len(short_graph_level_data), short_graph_level_data)
        print(len(graph_price_index),  graph_price_index)        
        #print("data length", len(data.long_short_data[0]['data']['long']))
        print("long length", sum(long_result.values()))
        print("short length", sum(short_result.values()))
        print(long_result)
        print(short_result)
        '''
        #print(result)
        return JsonResponse(context)

def add_journal_watch(request):
    if request.method == "POST":
        #security_id = request.POST['security_id']
        user_id = request.session['user_id']
        journal_name = request.POST['name']
        new_journal = Journal(name=journal_name, value="", user_id=user_id)
        new_journal.save()
        #messages.success(request, "Add new Journal watch list successfully.")
        journal = Journal.objects.filter(name=journal_name, user_id=user_id).values()[0]

        context = {
            "result": "success",
            "id": journal['id']
        }
        return JsonResponse(context)

def add_symbol_to_watchlist(request):
    if request.method == "POST":
        security_id = request.POST['security_id']
        symbol = request.POST['symbol']
        journal_id = request.POST['journal_id']
        side = request.POST['side']
        value = Journal.objects.filter(id=journal_id).values()[0]['value']
        if value == "":
            Journal.objects.filter(id=journal_id).update(value=security_id + "_" + symbol + "_" + side)
        else:
            Journal.objects.filter(id=journal_id).update(value=value + "," + security_id + "_" + symbol + "_" + side)
        context = {"result": "success"}
        return JsonResponse(context)

def view_journal_watchlist(request):
    if request.method == "POST":
        journal_id = request.POST['journal_id']
        symbol_list = Journal.objects.filter(id=journal_id).values()[0]['value'].split(",")
        print(symbol_list)
        result = []
        graph = []
        if symbol_list:
            for item in symbol_list:
                temp = []
                security_id, symbol, side = item.split("_")
                expire_date = Security.objects.filter(id=security_id).values()[0]['trading_day']
                rest_days = get_rest_trading_days(expire_date)
                atr_data = pd.read_excel(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(security_id), sheet_name="ATR")
                column_list = []
                for item in atr_data:
                    column_list.append(item)
                for i in range(len(column_list)):
                    if column_list[i] == symbol:
                        if side == "short":
                            atr = atr_data[column_list[i]].values[2:]
                        elif side == "long":
                            atr = atr_data[column_list[i + 1]].values[2:]
                '''
                temp['security_id'] = security_id
                temp['symbol'] = symbol
                temp['side'] = str(side).upper()
                temp['expire_date'] = expire_date
                temp['rest_days'] = rest_days
                temp['percent_price'], temp['last_bar'], temp['last_percent'], temp['max'], temp['min'] = atr
                '''
                temp.append(str(security_id))
                temp.append(str(symbol))
                temp.append(str(side.upper()))
                temp.append(str(expire_date))
                temp.append(str(rest_days))
                for item in atr:
                    temp.append(str(item))
                result.append(temp)
            context = {
                "result": result
            }
            #print(result)
            return JsonResponse(context)
        else:
            context = {"result": []}
            return JsonResponse(context)

def delete_journal_watchlist(request):

    if request.method == "POST":
        user_id = request.session['user_id']
        journal_id = request.POST['journal_id']
        try:
            Journal.objects.filter(id=journal_id, user_id=user_id).delete()
            context = {"success": "true"}
        except:
            context = {"success": "false"}

        return JsonResponse(context)

def view_journal_watch_graph(request):
    if request.method == "POST":
        security_id = request.POST['security_id']
        symbol = request.POST['symbol']
        length = 30

        level = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
        long_result = {}
        short_result = {}
        long_graph_price_data = []
        short_graph_price_data = []
        graph_price_index = []
        long_graph_level_data = []
        short_graph_level_data = []

        for item in level:
            long_result[str(item)] = 0
            short_result[str(item)] = 0
        aaa = pd.read_excel(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(security_id), sheet_name="Short Long")
        bbb = pd.read_excel(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(security_id), sheet_name="ATR")
        ccc = pd.read_excel(settings.MEDIA_ROOT + "/security/security_{}_all.xlsx".format(security_id), sheet_name="Data")
        index_list = ccc['symbol'].values[2:]
        column_list = []
        for item in aaa:
            column_list.append(item)
        for i in range(len(column_list)):
            if column_list[i] == symbol:
                short_data = aaa[column_list[i]].values[2:]
                long_data = aaa[column_list[i + 1]].values[2:]
                atr_short = bbb[column_list[i]].values[2:]
                atr_long = bbb[column_list[i + 1]].values[2:]

        long_data = long_data[-1 * length:]
        short_data = short_data[-1 * length:]
        for i in range(len(long_data)):
            if long_data[i] == atr_long[4]:
                long_result[str(5)] += 1
                long_graph_price_data.append(long_data[i])
            elif long_data[i] == atr_long[3]:
                long_result[str(95)] += 1
                long_graph_price_data.append(long_data[i])
            else:
                for j in range(1, len(level) - 1):
                    try:
                        temp_per = float(format((long_data[i] - atr_long[4]) / atr_long[0] + 5, '.2f'))
                    except:
                        temp_per = 5
                    if j == 1:
                        if temp_per > level[j] - 5 and temp_per < level[j] + 5:
                            long_result[str(level[j])] += 1
                            # if i >= len(long_data) - length:
                            long_graph_price_data.append(long_data[i])
                            # long_graph_price_per.append(temp_per)
                            break
                    else:
                        if temp_per >= level[j] - 5 and temp_per < level[j] + 5:
                            long_result[str(level[j])] += 1
                            # if i >= len(long_data) - length:
                            long_graph_price_data.append(long_data[i])
                            # long_graph_price_per.append(temp_per)
                            break

        for i in range(len(short_data)):
            if short_data[i] == atr_short[4]:
                short_result[str(5)] += 1
                short_graph_price_data.append(short_data[i])
            elif short_data[i] == atr_short[3]:
                short_result[str(95)] += 1
                short_graph_price_data.append(short_data[i])
            else:
                for j in range(1, len(level) - 1):
                    try:
                        temp_per = float(format((short_data[i] - atr_short[4]) / atr_short[0] + 5, '.1f'))
                    except:
                        temp_per = 5
                    if j == 1:
                        if temp_per > level[j] - 5 and temp_per < level[j] + 5:
                            short_result[str(level[j])] += 1
                            if i >= len(short_data) - length:
                                short_graph_price_data.append(short_data[i])
                                # short_graph_price_per.append(temp_per)
                            break
                    else:
                        if temp_per >= level[j] - 5 and temp_per < level[j] + 5:
                            short_result[str(level[j])] += 1
                            if i >= len(short_data) - length:
                                short_graph_price_data.append(short_data[i])
                                # short_graph_price_per.append(temp_per)
                            break

        for key, value in long_result.items():
            long_graph_level_data.append(float(format(value / len(long_data) * 100, '.1f')))
        for key, value in short_result.items():
            val = float(format(value / len(short_data) * 100, '.1f'))
            if val == 0:
                short_graph_level_data.append(0)
            else:
                short_graph_level_data.append(-1 * val)
        #print("last date", index_list[-1])
        for item in index_list[-1 * length:]:
            graph_price_index.append(str(item)[:10])
        for i in range(len(level)):
            if i == 0:
                if atr_long[2] == 5:
                    long_graph_level_data[i] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                if atr_short[2] == 5:
                    short_graph_level_data[i] = { 'y': short_graph_level_data[i], 'color': '#6887ff'}
            elif i == len(level) -1:
                if atr_long[2] == 95:
                    long_graph_level_data[-1] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                if atr_short[2] == 95:
                    short_graph_level_data[-1] = {'y': short_graph_level_data[i], 'color': '#6887ff'}
            elif i == 1:
                if atr_long[2] >5 and atr_long[2] <15:
                    long_graph_level_data[i] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                if atr_short[2] > 5 and atr_short[2] < 15:
                    short_graph_level_data[i] = {'y': short_graph_level_data[i], 'color': '#6887ff'}
            else:
                if atr_long[2] >= level[i] - 5 and atr_long[2] < level[i] + 5:
                    long_graph_level_data[i] = {'y': long_graph_level_data[i], 'color': '#fcc100'}
                if atr_short[2] >= level[i] - 5 and atr_short[2] < level[i] + 5:
                    short_graph_level_data[i] = {'y': short_graph_level_data[i], 'color': '#6887ff'}
        context = {
            "long_graph_price_data": long_graph_price_data,
            "short_graph_price_data": short_graph_price_data,
            "price_index": graph_price_index,
            "long_graph_level": long_graph_level_data,
            "short_graph_level": short_graph_level_data,
        }
        return JsonResponse(context)

def get_movement_chart(request):
    if request.method == "POST":
        permission = request.session['permission']
        user_id = request.session['user_id']
        if permission > 0:
            relate_open_data = []
            relate_high_data = []
            relate_low_data = []
            relate_close_data = []
            total_relate_data = []
            security_id = request.POST['id']
            ticker = request.POST['ticker']
            history_data = pdr.get_data_yahoo(ticker, start=datetime.datetime.today() - relativedelta(years=5), end=datetime.datetime.today())
            #print(history_data)
            column_list = [item for item in history_data]
            #print(column_list)
            index_list = history_data.index.tolist()
            #print(index_list)
            open_data = history_data['Open'].values
            high_data = history_data['High'].values
            low_data = history_data['Low'].values
            close_data = history_data['Close'].values
            for i in range(1, len(open_data)):
                relate_open_data.append(round(open_data[i] / open_data[i - 1], 8))
                relate_high_data.append(round(high_data[i] / high_data[i - 1], 8))
                relate_low_data.append(round(low_data[i] / low_data[i - 1], 8))
                relate_close_data.append(round(close_data[i] / close_data[i - 1], 8))
            #print(relate_high_data)
            #relate_open_data = [round(open_data[i] / open_data[i - 1], 8) for i in range(1, len(open_data))]
            #relate_high_data = [round(high_data[i] / high_data[i - 1], 8) for i in range(1, len(high_data))]
            #relate_low_data = [round(low_data[i] / low_data[i - 1], 8) for i in range(1, len(low_data))]
            #relate_close_data = [round(close_data[i] / close_data[i - 1], 8) for i in range(1, len)]
            sample_data = []
            for i in range(7, 0, -1):
                sample_data.append(relate_open_data[-1 * i])
                sample_data.append(relate_high_data[-1 * i])
                sample_data.append(relate_low_data[-1 * i])
                sample_data.append(relate_close_data[-1 * i])
            for j in range(len(relate_open_data) - 7):
                data1 = []
                for i in range(j, j + 7):
                    data1.append(relate_open_data[i])
                    data1.append(relate_high_data[i])
                    data1.append(relate_low_data[i])
                    data1.append(relate_close_data[i])
                total_relate_data.append(np.corrcoef(sample_data, data1).min())
            max_index = total_relate_data.index(max(total_relate_data))
            coefficient = round(close_data[-1] / open_data[max_index + 8], 8)
            last_data = [[open_data[i] for i in range(max_index + 8, max_index + 15)], [high_data[i] for i in range(max_index + 8, max_index + 15)], [low_data[i] for i in range(max_index + 8, max_index + 15)], [close_data[i] for i in range(max_index + 8, max_index + 15)]]
            forecast_data = []
            for i in range(7, 0, -1):
                #forecast_data.append([index_list[-1 * i], open_data[-1 * i], high_data[-1 * i], low_data[-1 * i], close_data[-1 * i]])
                if open_data[-1 * i] >= close_data[-1 * i]:
                    forecast_data.append({"x": index_list[-1 * i].timestamp() * 1000, "open": round(open_data[-1 * i], 2), "high": round(high_data[-1 * i], 2), "low": round(low_data[-1 * i], 2), "close":round(close_data[-1 * i], 2), "color": "#f44455"})
                else:
                    forecast_data.append({"x": index_list[-1 * i].timestamp() * 1000, "open": round(open_data[-1 * i], 2), "high": round(high_data[-1 * i], 2), "low": round(low_data[-1 * i], 2), "close": round(close_data[-1 * i], 2), "color": "#0cc2aa"})
                #forecast_data.append([index_list[-1 * i].timestamp() * 1000, round(open_data[-1 * i], 2), round(high_data[-1 * i], 2), round(low_data[-1 * i], 2), round(close_data[-1 * i], 2)])
            #print(forecast_data)
            last_workday = index_list[-1]
            us_holidays = holidays.UnitedStates()
            for i in range(7):
                k = 1
                while True:
                    if (last_workday + datetime.timedelta(days=k)).strftime("%A") == "Saturday" or (last_workday + datetime.timedelta(days=k)).strftime("%A") == "Sunday" or last_workday + datetime.timedelta(days=k) in us_holidays:
                        k += 1
                    else:
                        last_workday = last_workday + datetime.timedelta(days=k)
                        break
                #forecast_data.append([(index_list[-1] + datetime.timedelta(days=1 + i)).timestamp() * 1000, round(last_data[0][i] * coefficient, 2), round(last_data[1][i] * coefficient, 2), round(last_data[2][i] * coefficient, 2), round(last_data[3][i] * coefficient, 2)])
                forecast_data.append([last_workday.timestamp() * 1000, round(last_data[0][i] * coefficient, 2), round(last_data[1][i] * coefficient, 2), round(last_data[2][i] * coefficient, 2), round(last_data[3][i] * coefficient, 2)])
                if last_data[0][i] >= last_data[3][i]:
                    forecast_data.append({"x": last_workday.timestamp() * 1000, "open": round(last_data[0][i] * coefficient, 2), "high": round(last_data[1][i] * coefficient, 2), "low": round(last_data[2][i] * coefficient, 2), "close": round(last_data[3][i] * coefficient, 2), "color": "#e91e63"})#"#f44455"})
                else:
                    forecast_data.append({"x": last_workday.timestamp() * 1000, "open": round(last_data[0][i] * coefficient, 2), "high": round(last_data[1][i] * coefficient, 2), "low": round(last_data[2][i] * coefficient, 2), "close": round(last_data[3][i] * coefficient, 2), "color": "#4caf50"})
            context = {
                "result": forecast_data,
                "max": round(max(total_relate_data) * 100, 1)
            }
            #print(forecast_data)
            return JsonResponse(context)



