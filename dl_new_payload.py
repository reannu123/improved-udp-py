import requests

uniqueID = "c3563823"

url = f'http://3.0.248.41:5000/get_data?student_id={uniqueID}'
response = requests.get(url)
open(f"{uniqueID}.txt", "wb").write(response.content)