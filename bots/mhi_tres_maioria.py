import ast
import sys
import time
from datetime import datetime

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


# Aqui você faz as configurações do BOT
# #:===============================================================:#
valor_entrada_incial = 100
stop_loss = 1200
stop_win = 800
quantidade_martigale = 2
pariedade = 'EURUSD-OTC'
tipo_pariedade = 'DIGITAL'

# Aqui você faz as configurações da sua conta IQ Opetion
# #:===============================================================:#
login = 'COLOQUE AQUI SEU EMAIL IQ'
password = 'COLOQUE AQUI SUA SENHA IQ'
account_type = 'PRACTICE'

# Aqui começa a configuração da API, não alterar
# #:===============================================================:#
iq = IQ_Option(login, password)
if not verificar_se_fez_a_conexao(iq, account_type):
    sys.exit(0)

currency_account = iq.get_currency()
account_balance = iq.get_balance()

print('#:===============================================================:#')
print(f"This is your API version {IQ_Option.__version__}")
print('#:===============================================================:#')
print(f"Welcome: {login}")
print(
    f"{'Practice account balance' if account_type == 'PRACTICE' else 'Real account balance'}: {format_currency_value(currency_account, account_balance)}")
print('#:===============================================================:#')

# Variáveis de controle do BOT, não alterar
# #:===============================================================:#
lucro_atual = 0
valor_entrada_atual = valor_entrada_incial
quantidade_martigale_executado = -1
executar_martingale = False

print('#:===============================================================:#')
print(f'Executando estratégia MHI 3')
print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:M')}")
print(f'Pariedade: {pariedade}')
print(f'Valor Entrada: {format_currency_value(currency_account, valor_entrada_incial)}')
print(f'Stop loss: {format_currency_value(currency_account, stop_loss)}')
print(f'Stop Win: {format_currency_value(currency_account, stop_win)}')
print(f'Maximo Marigales: {quantidade_martigale}')
print('#:===============================================================:#')


def verificar_stops(_stop_loss: float, _stop_win: float, _lucro_atual: float, _valor_entrada_atual: float,
                    _show_message: bool = True) -> bool:
    if _lucro_atual >= _stop_win:
        if _show_message:
            print(f'Stop Win atingido!')
        return True

    if _lucro_atual < 0:
        if abs(_lucro_atual) + _valor_entrada_atual >= _stop_loss:
            if _show_message:
                print(f'Stop Loss atingido, ou valor muito próximo!')
            return True

    return False


def aguardar_horario_entrada(_iq: IQ_Option, _pariedade: str) -> list:
    print('>>>>>>>>>>>>>>> Aguardando horário de entrada', end='\r')
    print()
    while True:
        minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
        if (6.59 <= minutos <= 7) or minutos == 1.59:
            return _iq.get_candles(_pariedade, 60, 3, time.time() - 120)


def validar_estrategia(_candles: list) -> [bool, str]:
    print('>>>>>>>>>>>>>>> Validando estratégia', end='\r')
    print()
    cores = get_color_candle(_candles[0]) + get_color_candle(_candles[1]) + get_color_candle(_candles[2])
    if cores.count('D'):
        return False, "None"
    elif cores.count('G') > cores.count('R'):
        return True, 'CALL'
    else:
        return True, 'PUT'


def executar_entrada(_iq: IQ_Option, _pariedade: str, _tipo_pariedade: str, _direcao: str, _valor_entrada_atual: float,
                     _quantidade_martigale_executado: int) -> [str, float]:
    status, order_id = _iq.buy_digital_spot(_pariedade, _valor_entrada_atual, _direcao.upper(), 1) \
        if _tipo_pariedade.upper() == 'DIGITAL' else _iq.buy(_valor_entrada_atual, _pariedade, _direcao.upper(), 1)

    if quantidade_martigale_executado == -1:
        print(f">>>>>>>>>>>>>>> Executando {'compra' if _direcao.upper() == 'CALL' else 'venda'} "
              f"{'em digital,' if _tipo_pariedade.upper() == 'DIGITAL' else 'em binaria,'} "
              f"moeda {_pariedade} no valor de {format_currency_value(currency_account, _valor_entrada_atual)}, em {datetime.now().strftime('%d/%m/%Y as %H:%M:%S')}")
    else:
        print(f">>>>>>>>>>>>>>> Executando {'compra' if _direcao.upper() == 'CALL' else 'venda'} "
              f"{'em digital,' if _tipo_pariedade.upper() == 'DIGITAL' else 'em binaria,'} "
              f"moeda {_pariedade} no valor de {format_currency_value(currency_account, _valor_entrada_atual)}, Martingale nível: {_quantidade_martigale_executado + 1}, "
              f"em {datetime.now().strftime('%d/%m/%Y as %H:%M:%S')}")

    if status:
        print(f">>>>>>>>>>>>>>> Aguardando resultado da operação")
        while True:
            status, reusltado = _iq.check_win_digital_v2(
                order_id) if _tipo_pariedade.upper() == 'DIGITAL' else _iq.check_win_v4(order_id)
            if status:
                if reusltado > 0:
                    return 'WIN', float(reusltado)
                else:
                    return 'LOSS', float(_valor_entrada_atual)

    return 'ERROR', float(0)


print('>>>>>>>>>>>>>>> Iniciando operações')
while not verificar_stops(stop_loss, stop_win, lucro_atual, valor_entrada_atual):
    candles = aguardar_horario_entrada(iq, pariedade)
    estrategia_valida, direcao = validar_estrategia(candles)

    if estrategia_valida:

        while True:

            if quantidade_martigale > quantidade_martigale_executado:
                resultado, valor = executar_entrada(iq, pariedade, tipo_pariedade, direcao, valor_entrada_atual,
                                                    quantidade_martigale_executado)

                if resultado == 'LOSS':
                    lucro_atual -= valor
                    print(
                        f">>>>>>>>>>>>>>> Resulatdo da operação foi LOSS, lucro até o momento {format_currency_value(currency_account, lucro_atual)}")
                    quantidade_martigale_executado += 1
                    valor_entrada_atual = valor_entrada_atual * 2
                else:
                    lucro_atual += valor
                    print(
                        f">>>>>>>>>>>>>>> Resulatdo da operação foi WIN, lucro até o momento {format_currency_value(currency_account, lucro_atual)}")
                    valor_entrada_atual = valor_entrada_incial
                    quantidade_martigale_executado = -1
                    break
            else:
                quantidade_martigale_executado = -1
                valor_entrada_atual = valor_entrada_incial
                break

            if verificar_stops(stop_loss, stop_win, lucro_atual, valor_entrada_atual, False):
                break
    else:
        print(">>>>>>>>>>>>>>> Pulando entrada atual, alto risco de LOSS")
        time.sleep(5)
