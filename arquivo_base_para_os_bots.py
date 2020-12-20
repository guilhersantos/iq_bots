import ast
import getpass
import os
import sys
import time

from iqoptionapi.stable_api import IQ_Option


def verificar_se_fez_a_conexao(_iq, _account_type='PRACTICE'):
    check, reason = _iq.connect()
    error_password = """{"code":"invalid_credentials","message":"You entered the wrong credentials. Please check that the login/password is correct."}"""
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

    print("Finishing application, check your data and try again.")
    return False


def get_login():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        _login = str(input('Digite seu email: ')).strip()
        if len(_login) > 0 and _login.count('@') > 0:
            return _login
        else:
            print('Email inválido')
            time.sleep(1)


def get_password():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        _password = str(getpass.getpass('Digite sua senha: ')).strip()
        if len(_password) > 0:
            return _password
        else:
            print('Dados inválidos')
            time.sleep(1)


def get_account_type():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        option = str(input('Tipo de conta\n[1] : Demo\n[2] : Real\nOpção: '))
        if option == '1':
            return "PRACTICE"
        elif option == '2':
            return "REAL"
        else:
            print('Opção inválida')
            time.sleep(1)


login = get_login()
password = get_password()
account_type = get_account_type()

iq = IQ_Option(login, password)
if not verificar_se_fez_a_conexao(iq, account_type):
    sys.exit(0)

print('#:===============================================================:#')
print(f"This is your API version {IQ_Option.__version__}")
print('#:===============================================================:#')
print(f"Welcome: {iq.email}")
account_balance = '$ {:,.2f}'.format(iq.get_balance()) if iq.get_currency() == 'USD' else 'R$ {:,.2f}'.format(iq.get_balance())
print(f"{'Practice account balance' if iq.get_balance_mode() == 'PRACTICE' else 'Real account balance'}: {account_balance}")
print('#:===============================================================:#')

# #:===============================================================:#
# Daqui pra baixo começa seu bot
# #:===============================================================:#
