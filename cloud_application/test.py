import requests
import os


response = requests.post("http://localhost:8080/login", json={"username": os.environ["JWT_USER"], "password": os.environ["JWT_PASSWORD"]})
token = response.json()["token"]
headers = {"Authorization": "Bearer {0}".format(token)}

base_url = "http://localhost:8080/receivers"
# delete any left-over resources
requests.delete(base_url, headers=headers)


def test_receivers():

    assert requests.get(base_url, headers=headers).json() == []

    response1 = requests.post(base_url, json={"email": "email1@email.com"}, headers=headers).json()
    assert response1["email"] == "email1@email.com"
    assert "id" in response1

    assert requests.post(base_url, json={"email": "email1@email.com"}, headers=headers).status_code == 409
    assert requests.post(base_url, json={}, headers=headers).status_code == 400

    response2 = requests.post(base_url, json={"email": "email2@email.com"}, headers=headers).json()
    assert response2["email"] == "email2@email.com"
    assert "id" in response2

    assert requests.get(base_url, headers=headers).json() == [response1, response2]
    assert requests.delete(base_url, headers=headers).json() == []
    assert requests.get(base_url, headers=headers).json() == []


def test_receiver():

    assert requests.get(base_url, headers=headers).json() == []

    response1 = requests.post(base_url, json={"email": "email1@email.com"}, headers=headers).json()
    assert response1["email"] == "email1@email.com"
    assert "id" in response1

    response2 = requests.post(base_url, json={"email": "email2@email.com"}, headers=headers).json()
    assert response2["email"] == "email2@email.com"
    assert "id" in response2

    assert requests.get("{0}/{1}".format(base_url, response1["id"]), headers=headers).json() == response1
    assert requests.get("{0}/{1}".format(base_url, response2["id"]), headers=headers).json() == response2

    assert requests.get(base_url, headers=headers).json() == [response1, response2]

    assert requests.delete("{0}/{1}".format(base_url, response1["id"]), headers=headers).json() == response1
    assert requests.delete("{0}/{1}".format(base_url, response2["id"]), headers=headers).json() == response2

    assert requests.get(base_url, headers=headers).json() == []
