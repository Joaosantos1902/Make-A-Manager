import requests
import json

printer_host = "192.168.50.179"
path = "/api/v1/status"
#path = "/api/v1/info"

API_key = "fmR_VorvHS6nxg"


r = requests.get('http://' + printer_host + path, headers = {'X-Api-Key': API_key})
r.raise_for_status()
return_json = r.json()


print(return_json
      )




