#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 16:42:00 2021

@author: ahemmendinger
"""


from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for, session, make_response, abort
import model_builder
import joblib
import requests
import base64
file = open('files/username').read().split('\n')[1:]
locs = ['California','HongKong','Paris']

USERNAMES = [x.split(',') for x in file if x != '']
port = 8500
app = Flask(__name__)
app.config['SECRET_KEY'] = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'



### Clefs possibles d'utilisateur
all_credentials = {base64.b64encode(bytes(user + ":" + pwd, encoding='utf8')):1  for (user,pwd) in USERNAMES}
'''
{b'YWxpY2U6d29uZGVybGFuZA==': 1,
 b'Ym9iOmJ1aWxkZXI=': 1,
 b'Y2zDqW1lbnRpbmU6bWFuZGFyaW5l': 1}
'''

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET' :
        return '''
<form action="" method="post" role="form" enctype="multipart/form-data">
<h1>Projet Data Scientest</h1>

<div style="padding-top:50px"></div>

Veuillez renseigner pseudo et mot de passe
<div style="padding-top:10px"></div>
<input type="text" class="form-control" aria-label="Small" aria-describedby="inputGroup-sizing-sm"
  value="alice" name="name" id="name">
<input type="text" class="form-control" aria-label="Small" aria-describedby="inputGroup-sizing-sm"
  value="" name="password" id="password">
  
<div style="padding-top:50px"></div>

<button type="submit" name='connexion' id='button_test'
            >Connexion</button>
            

</form>
'''
    if request.method == 'POST' : 
        session['auth'] = 'not ok'
        session['credentials'] =  ''
        name,password=request.form['name'],request.form['password']
        credentials = base64.b64encode(bytes(name + ":" + password, encoding='utf8'))
        check_credentials(credentials)
        session['auth'] = 'ok'
        session['credentials'] = credentials
        return redirect('application')



@app.route('/application',methods=['GET','POST'])
def application():
    if 'auth' not in session or session['auth']=='not ok' : 
        abort(402,'Veuillez dabord vous connecter')
    result = '''
<form action="" method="post" role="form" enctype="multipart/form-data">
<h1>Projet Data Scientest - Résultats</h1>

<div style="padding-top:50px"></div>

Veuillez renseigner une phrase
<div style="padding-top:10px"></div>
<input type="text" class="form-control" aria-label="Small" aria-describedby="inputGroup-sizing-sm"
  value="Hello World" name="phrase" id="phrase">
<div style="padding-top:10px"></div>
Veuillez renseigner un lieu de Disney
<div style="padding-top:10px"></div>
<select class="select_rounded" name="select_option" id="select_option"
                onchange="select_option_function()">
                <option selected="selected">California</option>
                <option>HongKong</option>
                <option>Paris</option>
              </select>

  
<div style="padding-top:50px"></div>

<button type="submit" name='Analyse' id='button'
            >Analyse</button>
            

</form>
'''
    if request.method == 'POST' : 
        text = request.form['phrase']
        location = request.form['select_option']
        preprocessed_text = model_builder.preprocess_text(text)
        onemodel = requests.get(
        url=f'http://127.0.0.1:{port}/onemodel',
        json= {
            'text' : text
        },
        headers={'Authorization': session['credentials']}
        )
        
        locmodel = requests.get(
        url=f'http://127.0.0.1:{port}/locmodel',
        json= {
            'text' : text,
            'location' : location
        },
        headers={'Authorization': session['credentials']}
        )


        
        result += f'''
<div style="padding-top:30px"></div>
Texte : {text} <br>
Texte tokénisé : {preprocessed_text} <br>
Location : {location} <br>
Analyse tous modèles : {onemodel.json()['result']}  <br>
Analyse modèle {location} : {locmodel.json()['result']}

'''

    return result



@app.route('/permissions',methods=['GET'])
def permissions():
    #curl -X GET http://0.0.0.0:8500/permissions  --user alice:wonderland
    #curl -X GET http://0.0.0.0:8500/permissions --user alice:dgkh
    check_credentials(request.headers.get('Authorization'))
    code = request.headers.get('Authorization').split()[-1]
    session['auth']='ok'
    session['credentials'] = code
    return jsonify("Vous pouvez désormais utiliser l'application")


@app.route('/onemodel',methods=['GET'])
def onemodel():
    #curl -X GET http://0.0.0.0:8500/onemodel -i -H "Content-Type: application/json" -d '{"text" : "Wonderful"}' --user alice:wonderland
    check_credentials(request.headers.get('Authorization'))
    if 'text' not in request.json or len(request.json['text']) == 0 : 
        abort(403,'No text given')
    text = request.json['text']
    test = [model_builder.preprocess_text(text)]
    res = str(pipeline_one_model.predict(test)[0])
    print('##################',res)
    return jsonify({'result':res})

@app.route('/locmodel',methods=['GET'])
def locmodel():
    #curl -X GET http://0.0.0.0:8500/locmodel -i -H "Content-Type: application/json" -d '{"text" : "Wonderful", "location": "Paris"}'  --user alice:wonderland
    check_credentials(request.headers.get('Authorization'))
    if 'text' not in request.json or len(request.json['text']) == 0: 
        abort(403,'No text given')
    if 'location' not in request.json : 
        abort(403,'No location given')
    if  request.json['location'] not in locs : 
        abort(403,'Location is not good')
    text = request.json['text']
    location = request.json['location']
    test = [model_builder.preprocess_text(text)]
    res = str(pipelines_location[location].predict(test)[0])
    return jsonify({'result':res})




@app.route('/status',methods=['GET'])
def status():
    #curl -X GET http://0.0.0.0:8500/status
    """
    Verifie que l'application fonctionne
    """
    return jsonify([1,"l'application fonctionne"])
    
def encode_to_bytes(s) : 
    if type(s)==str : 
        return bytes(s,encoding='utf-8')
    if type(s)==bytes : 
        return s 


def check_credentials(credentials):
    """
    Check acces, et bon format de la requete
    """
    if credentials is None :
            abort(403,description = "Information non valide : veuillez renseigner name et password")
    credentials = credentials.split()[-1]
    if encode_to_bytes(credentials) not in all_credentials : 
        abort(403,description = "Pseudo ou mot de passe mauvais")
    return jsonify(["Mot de passe bien renseigné"])

if __name__ == '__main__':
    
    pipeline_one_model = joblib.load('models/pipeline_one_model')
    pipelines_location = {loc : joblib.load(f'models/pipeline_Disneyland_{loc}') for loc in locs}
    app.run(host="0.0.0.0",port=port,debug=True)

