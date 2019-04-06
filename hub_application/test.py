import requests


base_url = "http://localhost:8080/devices"
# delete any left-over resources
requests.delete("{0}/sensors".format(base_url))
requests.delete("{0}/ringers".format(base_url))


def test_sensors():

    api_url = "{0}/sensors".format(base_url)
    
    templatetest_devices(api_url)


def test_ringers():

    api_url = "{0}/ringers".format(base_url)
    templatetest_devices(api_url)


def templatetest_devices(api_url):
    
    assert requests.get(api_url).json() == {}

    assert requests.post(api_url, json={"alias": "test1", "mac": "mac1"}).json() == {"status": "disconnected", "alias": "test1", "mac": "mac1"}
    assert requests.post(api_url, json={"alias": "test2", "mac": "mac2"}).json() == {"status": "disconnected", "alias": "test2", "mac": "mac2"}

    assert requests.get(api_url).json() == {"test1": {"status": "disconnected", "alias": "test1", "mac": "mac1"}, "test2": {"status": "disconnected", "alias": "test2", "mac": "mac2"}}
    assert requests.delete(api_url).json() == {}
    assert requests.get(api_url).json() == {}


def test_sensors_instance():

    identifier = "test"
    assert requests.post("{0}/sensors".format(base_url), json={"alias": identifier, "mac": "mac"}).json() == {"status": "disconnected", "alias": identifier, "mac": "mac"}
    templatetest_instance("{0}/sensors/{1}".format(base_url, identifier))


def test_ringers_instance():

    identifier = "test"
    assert requests.post("{0}/ringers".format(base_url), json={"alias": identifier, "mac": "mac"}).json() == {"status": "disconnected", "alias": identifier, "mac": "mac"}
    templatetest_instance("{0}/ringers/{1}".format(base_url, identifier))


def templatetest_instance(api_url):

    assert requests.get(api_url).json() == {"status": "disconnected", "alias": "test", "mac": "mac"}

    assert requests.post(api_url, json={"status": "connected"}).json() == {"status": "connected", "alias": "test", "mac": "mac"}
    assert requests.get(api_url).json() == {"status": "connected", "alias": "test", "mac": "mac"}

    assert requests.post(api_url, json={"status": "disconnected"}).json() == {"status": "disconnected", "alias": "test", "mac": "mac"}
    assert requests.get(api_url).json() == {"status": "disconnected", "alias": "test", "mac": "mac"}

    assert requests.delete(api_url).json() == {"status": "disconnected", "alias": "test", "mac": "mac"}
    assert requests.get(api_url).status_code == 404
