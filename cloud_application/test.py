import requests


base_url = "http://localhost:8080/receivers"
# delete any left-over resources
requests.delete(base_url)


def test_receivers():

    assert requests.get(base_url).json() == []

    response1 = requests.post(base_url, json={"email": "email1@email.com"}).json()
    assert response1["email"] == "email1@email.com"
    assert "id" in response1

    assert requests.post(base_url, json={"email": "email1@email.com"}).status_code == 409
    assert requests.post(base_url, json={}).status_code == 400

    response2 = requests.post(base_url, json={"email": "email2@email.com"}).json()
    assert response2["email"] == "email2@email.com"
    assert "id" in response2

    assert requests.get(base_url).json() == [response1, response2]
    assert requests.delete(base_url).json() == []
    assert requests.get(base_url).json() == []


def test_receiver():

    assert requests.get(base_url).json() == []

    response1 = requests.post(base_url, json={"email": "email1@email.com"}).json()
    assert response1["email"] == "email1@email.com"
    assert "id" in response1

    response2 = requests.post(base_url, json={"email": "email2@email.com"}).json()
    assert response2["email"] == "email2@email.com"
    assert "id" in response2

    assert requests.get("{0}/{1}".format(base_url, response1["id"])).json() == response1
    assert requests.get("{0}/{1}".format(base_url, response2["id"])).json() == response2

    assert requests.get(base_url).json() == [response1, response2]

    assert requests.delete("{0}/{1}".format(base_url, response1["id"])).json() == response1
    assert requests.delete("{0}/{1}".format(base_url, response2["id"])).json() == response2

    assert requests.get(base_url).json() == []
