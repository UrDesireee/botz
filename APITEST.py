import requests

url = "https://open.tiktokapis.com/v2/oauth/token/"
data = {
    "client_key": "",
    "client_secret": "",
    "grant_type": "client_credentials"
}

response = requests.post(url, data=data)
print(response.status_code)
print(response.text)