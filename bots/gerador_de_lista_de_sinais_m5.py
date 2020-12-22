import ast
import sys
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from dateutil import tz

from iqoptionapi.stable_api import IQ_Option


def verificar_se_fez_a_conexao(_iq: IQ_Option, _account_type: str = 'PRACTICE') -> bool:
    check, reason = _iq.connect()
    error_password = """{"code":"invalid_credentials","message":"You entered the wrong credentials. Please check that the login/password is correct."}"""
    requests_limit_exceeded = """{"code":"requests_limit_exceeded","message":"The number of requests has been exceeded. Try again in 10 minutes.","ttl":600}"""
    if check:
        print("Start your application")
        _iq.change_balance(_account_type)
        return True
    else:
        if reason == "[Errno -2] Name or service not known":
            print("No Network")
        elif reason == error_password:
            error_message = ast.literal_eval(error_password)
            print(error_message['message'])
        elif reason == requests_limit_exceeded:
            error_message = ast.literal_eval(requests_limit_exceeded)
            print(error_message['message'])

    print("Finishing application, check your data and try again.")
    return False


def format_currency_value(_currency_account: str, _value: float) -> str:
    return '$ {:,.2f}'.format(_value) if _currency_account == 'USD' else 'R$ {:,.2f}'.format(_value)


def get_color_candle(_candle: dict) -> str:
    return 'G' if _candle['open'] < _candle['close'] else 'R' if _candle['open'] > _candle['close'] else 'D'


# Aqui você faz as configurações da sua conta IQ Opetion
#:===============================================================:#
login = 'COLOQUE AQUI SEU EMAIL IQ'
password = 'COLOQUE AQUI SUA SENHA IQ'
account_type = 'PRACTICE'

# Aqui começa a configuração da API, não alterar
#:===============================================================:#
iq = IQ_Option(login, password)
if not verificar_se_fez_a_conexao(iq, account_type):
    sys.exit(0)

currency_account = iq.get_currency()
account_balance = iq.get_balance()
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M'

print('#:===============================================================:#')
print(f"This is your API version {IQ_Option.__version__}")
print('#:===============================================================:#')
print(f"Welcome: {login}")
print(f"{'Practice account balance' if account_type == 'PRACTICE' else 'Real account balance'}: {format_currency_value(currency_account, account_balance)}")
print('#:==============================================================:#')

# Aqui você faz as configurações do BOT
#:===============================================================:#
pariedades = ['EURUSD', 'AUDCAD']
quantidade_dias = 2
filtro_percentual = 80


def timestamp_converter(_timestamp: int) -> str:
    hora = datetime.strptime(datetime.utcfromtimestamp(_timestamp).strftime(DATE_TIME_FORMAT), DATE_TIME_FORMAT)
    hora = hora.replace(tzinfo=tz.gettz('GMT'))
    return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-9]


def filter_columns(_candles: list) -> list:
    return [{k: v for k, v in candle.items() if k in {'from', 'open', 'close'}} for candle in _candles]


def adjust_catalog(_pariedade: str, _candle: dict) -> dict:
    return {
        'pariedade': _pariedade,
        'hora': timestamp_converter(_candle['from']).split(' ')[1],
        'green': 1 if get_color_candle(_candle) == 'G' else 0,
        'red': 1 if get_color_candle(_candle) == 'R' else 0,
        'doji': 1 if get_color_candle(_candle) == 'D' else 0
    }


catalogacao = []
for pariedade in pariedades:
    for dia in range(quantidade_dias, -1, -1):
        if dia == 0:
            current_date = datetime(
                year=datetime.now().date().year,
                month=datetime.now().date().month,
                day=datetime.now().date().day,
                hour=datetime.now().hour,
                minute=0,
                second=0,
                microsecond=0) - timedelta(days=dia, minutes=5)
            current_timestamp = int(time.mktime(current_date.timetuple()))
            candles = iq.get_candles(pariedade, 300, datetime.now().hour * 12, current_timestamp)
            candles = [{k: v for k, v in candle.items() if k in {'from', 'open', 'close'}} for candle in candles]
            for candle in candles:
                catalogacao.append(adjust_catalog(pariedade, candle))
        else:
            current_date = datetime(
                year=datetime.now().date().year,
                month=datetime.now().date().month,
                day=datetime.now().date().day,
                hour=0,
                minute=0,
                second=0,
                microsecond=0) - timedelta(days=dia, minutes=5)
            current_timestamp = int(time.mktime(current_date.timetuple()))
            candles = iq.get_candles(pariedade, 300, 228, current_timestamp)
            for candle in filter_columns(candles):
                catalogacao.append(adjust_catalog(pariedade, candle))

df = pd.DataFrame(catalogacao)
sum_df = df.groupby(['pariedade', 'hora'], as_index=False).agg({'green': 'sum', 'red': 'sum', 'doji': 'sum'})
sum_df['total'] = sum_df['green'] + sum_df['red'] + sum_df['doji']
sum_df['green_percent'] = np.int64(sum_df['green'] / sum_df['total'] * 100)
sum_df['red_percent'] = np.int64(sum_df['red'] / sum_df['total'] * 100)
sum_df['doji_percent'] = np.int64(sum_df['doji'] / sum_df['total'] * 100)
new_df = sum_df[['pariedade', 'hora', 'green_percent', 'red_percent', 'doji_percent']]
new_df = new_df.sort_values(by='hora')
list_catalog = new_df.values.tolist()

with open('lista_sinais.txt', 'a', encoding='utf-8') as file:
    for item in list_catalog:
        if item[2] > filtro_percentual:
            file.write(item[0] + ';' + item[1] + ';' + 'CALL\n')
        if item[3] > filtro_percentual:
            file.write(item[0] + ';' + item[1] + ';' + 'PUT\n')
