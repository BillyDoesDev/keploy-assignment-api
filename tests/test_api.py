def test_api_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "yep, here it goes again [Server's online!]"}


def test_weather(client):
    res = client.get("/weather/London")
    assert res.status_code == 200
    assert "temperature_c" in res.json()


def test_apod(client):
    res = client.get("/apod")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_xkcd(client):
    res = client.get("/xkcd")
    assert res.status_code == 200
    assert "title" in res.json()
