import requests

r = {
    "event": "ssdfsadf conference",
    "date": "2020-11-15"
}
requests.post('http://127.0.0.1:5000/event/', data=r)
print(requests.get('http://127.0.0.1:5000/event?start_time=2020-1-1&end_time=2021-5-20').text)