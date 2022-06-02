import requests

ID = "c3563823"
payload = requests.get(f'http://3.0.248.41:5000/get_data?student_id={ID}')
open(f"{ID}.txt", "wb").write(payload.content)