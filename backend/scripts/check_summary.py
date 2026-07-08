"""Simple integration script to create a user and hit the /summary endpoint.

Usage:
    python scripts/check_summary.py

Requires `requests` package.
"""

import requests
from pprint import pprint

API_URL = 'http://localhost:8000'

def signup(username='intuser1'):
    res = requests.post(f"{API_URL}/auth/signup", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "password123"
    })
    res.raise_for_status()
    return res.json().get('access_token')


def get_summary(token, period='daily'):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{API_URL}/summary/?period={period}", headers=headers)
    res.raise_for_status()
    return res.json()


if __name__ == '__main__':
    try:
        token = signup('intuser_test')
        print('Token obtained:', bool(token))
        for p in ['daily', 'monthly', 'yearly', 'lifetime']:
            print('\nPeriod:', p)
            data = get_summary(token, p)
            pprint(data)
    except Exception as e:
        print('Error:', e)
