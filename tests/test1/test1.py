import os
import requests
import sys
import base64

username,password = sys.argv[1],sys.argv[2]

code = base64.b64encode(bytes(username + ":" + password, encoding='utf8'))


# définition de l'adresse de l'API
# port de l'API
api_port = 8500


# requête
r = requests.get(
    url='http://project:{port}/permissions'.format(port=api_port),
    headers={'Authorization': code}
    
)

output = '''
============================
    Authentication test
============================

request done at "/permissions"
| username="{username}"
| password="{password}"

expected result = 200
actual restult = {status_code}

==>  {test_status}

'''


# statut de la requête
status_code = r.status_code

# affichage des résultats
if status_code == 200:
    test_status = 'SUCCESS'
else:
    test_status = 'FAILURE'
print(output.format(username=username,password=password,status_code=status_code, test_status=test_status))


