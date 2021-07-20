import os
import requests
import sys
import base64
from bs4 import BeautifulSoup
username,password,text = sys.argv[1],sys.argv[2],sys.argv[3]

code = base64.b64encode(bytes(username + ":" + password, encoding='utf8'))

# définition de l'adresse de l'API
# port de l'API
api_port = 8500


# requête
r = requests.get(
    url='http://project:{port}/onemodel'.format(port=api_port),
    headers={'Authorization': code},
    json= {'text':text}   
)

output = '''
============================
    Authentication test
============================

request done at "/permissions"
| username="{username}"
| password="{password}"

| text="{text}"
| score="{score}"

expected result = 200
actual result = {status_code}
error = {error}

==>  {test_status}

'''

error = 'no error'
score = ''

# statut de la requête
status_code = r.status_code

# affichage des résultats
if status_code == 200:
    score = float(r.json()['result'])
    test_status = 'SUCCESS'
else:
    test_status = 'FAILURE'
    error = BeautifulSoup(r.text).p.text
print(output.format(username=username,password=password,status_code=status_code, test_status=test_status, score=score, text=text, error=error))


