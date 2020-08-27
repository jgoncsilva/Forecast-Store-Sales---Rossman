import os
import json 
import pandas as pd 
import requests

from flask import Flask, request, Response

TOKEN= '1363696729:AAEw0LqK4xA8-nINohUe8BCM1Eu2xJAn7xE'

'''
#informações sobre o bot


#Get Updates 


#set webhook



#mandando mensagem

'''
def send_message(chat_id, text):
    url = 'https://api.telegram.org/bot{}/'.format(TOKEN)
    url = url + 'sendMessage?chat_id={}'.format(chat_id)

    r = requests.post(url, json={'text':text})
    
    print('Status code(send_message):{}'.format(r.status_code))

    return None

def load_dataset(store_id):

    # carregando o dataset de teste
    df10 = pd.read_csv('test.csv')

    df_store_raw = pd.read_csv('store.csv')

    # unindo os datasets
    df_test = pd.merge(df10, df_store_raw, how='left', on='Store')

    # escolhendo uma loja específica
    df_test = df_test[df_test['Store'] == store_id]

    if not df_test.empty:
        # excluindo os dias em que as lojas estão fechadas
        df_test = df_test[df_test['Open'] != 0]
        df_test = df_test[~df_test['Open'].isnull()]

        # excluindo a coluna 'ID'
        df_test = df_test.drop('Id', axis=1)

        # convertendo o Datafram em Json
        data = json.dumps(df_test.to_dict(orient='records'))

    else:
        data = 'error'
    
    return data


def predict(data):
    # chamando a API 
    url = 'https://rossmann-model-prediction.herokuapp.com/rossmann/predict'
    header = {'Content-type': 'application/json'}
    data = data

    r = requests.post(url, data= data, headers= header)
    print('Status code: {}'.format(r.status_code))

    # transformando os dados JSON em um DataFrame novamente
    d1 = pd.DataFrame(r.json(), columns=r.json()[0].keys())
    
    return d1


def parse_message(message):
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']

    store_id = store_id.replace('/', '')

    try:
        store_id = int(store_id)

    except ValueError:
        store_id = 'error'

    return chat_id, store_id



#inicialização da API
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def index():
    emoji_money_bag = u'\U0001F4B0'
    emoji_cold_sweat = u'\U0001F630'
    emoji_confused = u'\U0001F615'

    if request.method == 'POST':
        message = request.get_json()

        # parses message comming from json
        chat_id, store_id = parse_message(message)

        if (store_id != 'error' and store_id != 'start'):
            # loads data
            data = load_dataset(store_id)

            if data != 'error':
                # makes the prediction
                d1 = predict(data)

                # calculates
                # gets total sales by store
                d2 = d1[['store', 'prediction']].groupby('store').sum().reset_index()
                
                # sends message
                msg = 'The estimated total amount of sales, by the end of the next 6 weeks, for the store number {} is US${:,.2f}'.format(
                        d2['store'].values[0], 
                        d2['prediction'].values[0])
                
                send_message(chat_id, msg)
                return Response('OK', status=200)

            else:
                send_message(chat_id, 'This store number does not exist ' + emoji_confused + '\nPlease, enter another store number. \nExample: /42')
                return Response('OK', status=200)

        elif(store_id == 'start'):
            send_message(chat_id, 'Hello! It is a great day to do business! ' + emoji_money_bag)
            return Response('OK', status=200)

        else:
            send_message(chat_id, 'Hmmm... This does not seem to be a store number ' + emoji_cold_sweat + '\nPlease enter a store number. \nExample: /42')
            return Response('OK', status=200)

    else:
        return '<h1>Rossmann Telegram BOT</h1>'

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
