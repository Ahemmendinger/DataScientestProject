#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 16:42:00 2021

@author: ahemmendinger
"""


from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for, session, make_response, abort
import pandas as pd
import model_builder
import joblib
import requests
USERNAMES = pd.read_table('files/username',sep=',')
USERNAMES = {user.lower():pwd for (user,pwd) in zip(USERNAMES.USER,USERNAMES.PASSWORD)}

port = 8500
app = Flask(__name__)
app.config['SECRET_KEY'] = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'





@app.route('/',methods=['GET','POST'])
def index():
    print(session)
    if request.method == 'GET' :
        print('argh')
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
        if 'name' in session : 
            session.pop('name')  
        if 'password' in session : 
            session.pop('password')
        name,password=request.form['name'],request.form['password']
        credentials = {'name':name,'password':password}
        check_credentials(credentials)
        session['name']=name
        session['password']=password
        return redirect('application')



@app.route('/application',methods=['GET','POST'])
def application():
    if 'name' not in session : 
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
            'name': session['name'],
            'password': session['password'],
            'text' : text
        }
        )
        
        locmodel = requests.get(
        url=f'http://127.0.0.1:{port}/locmodel',
        json= {
            'name': session['name'],
            'password': session['password'],
            'text' : text,
            'location' : location
        }
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
    #curl -X GET http://0.0.0.0:8000/permissions -i -H "Content-Type: application/json" -d '{"name": "daniel", "password" : "youpi"}' 
    #curl -X GET http://0.0.0.0:8000/permissions -i -H "Content-Type: application/json" -d '{"name": "alice", "password" : "wonderland"}' 
    check_credentials(request.json)
    name = request.json['name']
    password = request.json['password']
    session['name']=name
    session['password']=password
    return jsonify("Vous pouvez désormais utiliser l'application")


@app.route('/onemodel',methods=['GET'])
def onemodel():
    #curl -X GET http://0.0.0.0:8000/onemodel -i -H "Content-Type: application/json" -d '{"name": "alice", "password" : "wonderland", "text" : "Wonderful"}' 
    check_credentials(request.json)
    if 'text' not in request.json : 
        abort(403,'No text given')
    text = request.json['text']
    test = [model_builder.preprocess_text(text)]
    res = str(pipeline_one_model.predict(test)[0])
    print('##################',res)
    return jsonify({'result':res})

@app.route('/locmodel',methods=['GET'])
def locmodel():
    #curl -X GET http://0.0.0.0:8000/onemodel -i -H "Content-Type: application/json" -d '{"name": "alice", "password" : "wonderland", "text" : "Wonderful", "location": "Paris"}' 
    check_credentials(request.json)
    if 'text' not in request.json : 
        abort(403,'No text given')
    if 'location' not in request.json : 
        abort(403,'No location given')
    text = request.json['text']
    location = request.json['location']
    test = [model_builder.preprocess_text(text)]
    res = str(pipelines_location[location].predict(test)[0])
    return jsonify({'result':res})




@app.route('/status',methods=['GET'])
def status():
    """
    Verifie que l'application fonctionne
    """
    return jsonify([1,"l'application fonctionne"])
    


def check_credentials(credentials):
    """
    Check acces, et bon format de la requete
    """
    if "name" not in credentials or "password" not in credentials  :
            abort(403,description = "Information non valide : veuillez renseigner name et password")
    name = credentials['name'].lower()
    password = credentials['password']
    if name not in USERNAMES : 
        abort(403,description = f"Utilisateur {name} non connu")
    if str(USERNAMES[name]) != str(password) : 
        abort(403,description = "Mot de passe mauvais")
    return jsonify(["Mot de passe bien renseigné"])

if __name__ == '__main__':
    locs = ['California','HongKong','Paris']
    pipeline_one_model = joblib.load('models/pipeline_one_model')
    pipelines_location = {loc : joblib.load(f'models/pipeline_Disneyland_{loc}') for loc in locs}
    app.run(host="0.0.0.0",port=port,debug=True)

