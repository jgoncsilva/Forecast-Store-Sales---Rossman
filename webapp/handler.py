import os
import pandas as pd 
from flask import Flask, request, Response
from rossmann.Rossmann import Rossmann
import pickle

#  carregando modelo 
model = pickle.load(open('model/model_rossmann.pkl', 'rb'))

app = Flask(__name__)

@app.route('/rossmann/predict', methods=['POST'])

def rossmann_predict():
    test_json = request.get_json()
    
    if test_json: #tem dados
	
        if isinstance(test_json, dict): # exemplo único 
            test_raw = pd.Dataframe(test_json, index=[0])
        
        else:
            test_raw = pd.DataFrame(test_json, columns=test_json[0].keys())
        # instanciando classe do rossmann 
        pipeline = Rossmann()
        
        # limpeza dos dados
        df1 = pipeline.data_cleaning(test_raw)
        
        # atributo dos dados 
        df2 = pipeline.feature_engineer(df1)
        
        # preparação dos dados
        df3 = pipeline.data_preparation(df2)
        
        # predição dos dados
        df_response = pipeline.get_prediction(model, test_raw, df3)
        
        return df_response
    
    
    else:
        return Response('{}', status=200, mimetype='application/json')
    
if __name__ == '__main__':
	port = os.environ.get('PORT', 5000)
	app.run(host='0.0.0.0', port=port)
