import requests

API_URL = 'http://localhost:8000'

res = requests.post(f"{API_URL}/auth/signup", json={
    "username": "tester1234",
    "email": "test4@test.com",
    "password": "password123"
})
print("Signup:", res.status_code)
token = res.json().get("access_token")

res = requests.get(f"{API_URL}/daily-sales/", headers={"Authorization": f"Bearer {token}"})
print("GET Daily Sales:", res.status_code, res.text)

