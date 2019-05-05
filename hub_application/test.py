import requests
import os


response = requests.post("http://localhost:8080/login", json={"username": os.environ["JWT_USER"], "password": os.environ["JWT_PASSWORD"]})
token = response.json()["token"]
headers = {"Authorization": "Bearer {0}".format(token)}

base_url = "http://localhost:8080/devices"
# delete any left-over resources
requests.delete("{0}/sensors".format(base_url, headers=headers))
requests.delete("{0}/ringers".format(base_url), headers=headers)


def test_sensors():

    api_url = "{0}/sensors".format(base_url)
    
    templatetest_devices(api_url)


def test_ringers():

    api_url = "{0}/ringers".format(base_url)

    templatetest_devices(api_url)


def templatetest_devices(api_url):
    
    assert requests.get(api_url, headers=headers).json() == []

    assert requests.post(api_url, json={"alias": "test1", "mac": "mac1"}, headers=headers).json() == {"status": "disconnected", "alias": "test1", "mac": "mac1"}
    assert requests.post(api_url, json={"alias": "test2", "mac": "mac2"}, headers=headers).json() == {"status": "disconnected", "alias": "test2", "mac": "mac2"}

    assert requests.get(api_url, headers=headers).json() == [{"status": "disconnected", "alias": "test1", "mac": "mac1"}, {"status": "disconnected", "alias": "test2", "mac": "mac2"}]
    assert requests.delete(api_url, headers=headers).json() == []
    assert requests.get(api_url, headers=headers).json() == []


def test_sensors_instance():

    identifier = "test"
    assert requests.post("{0}/sensors".format(base_url), json={"alias": identifier, "mac": "mac"}, headers=headers).json() == {"status": "disconnected", "alias": identifier, "mac": "mac"}
    templatetest_instance("{0}/sensors/{1}".format(base_url, identifier))


def test_ringers_instance():

    identifier = "test"
    assert requests.post("{0}/ringers".format(base_url), json={"alias": identifier, "mac": "mac"}, headers=headers).json() == {"status": "disconnected", "alias": identifier, "mac": "mac"}
    templatetest_instance("{0}/ringers/{1}".format(base_url, identifier))


def templatetest_instance(api_url):

    assert requests.get(api_url, headers=headers).json() == {"status": "disconnected", "alias": "test", "mac": "mac"}

    assert requests.post(api_url, json={"status": "connected"}, headers=headers).json() == {"status": "connected", "alias": "test", "mac": "mac"}
    assert requests.get(api_url, headers=headers).json() == {"status": "connected", "alias": "test", "mac": "mac"}

    assert requests.post(api_url, json={"status": "disconnected"}, headers=headers).json() == {"status": "disconnected", "alias": "test", "mac": "mac"}
    assert requests.get(api_url, headers=headers).json() == {"status": "disconnected", "alias": "test", "mac": "mac"}

    assert requests.delete(api_url, headers=headers).json() == {"status": "disconnected", "alias": "test", "mac": "mac"}
    assert requests.get(api_url, headers=headers).status_code == 404
