import requests
API_URL = 'http://localhost:8000'

res = requests.post(f"{API_URL}/auth/signup", json={"username":"newuser2", "email":"x@x.com", "password":"123"})
tok = res.json().get("access_token")

res = requests.get(f"{API_URL}/summary/", headers={"Authorization": f"Bearer {tok}"})
print("Summary:", res.status_code, res.text)
