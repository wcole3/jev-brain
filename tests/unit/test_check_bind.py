from scripts.check_bind import exposure_error


def config(host_ip: str | None, key: str = "") -> dict:
    port = {"target": 9000, "published": "9000"} | ({"host_ip": host_ip} if host_ip else {})
    return {"services": {"gateway": {"ports": [port], "environment": {"GATEWAY_API_KEY": key}}}}


def test_loopback_needs_no_key():
    assert exposure_error(config("127.0.0.1")) is None


def test_lan_bind_without_key_is_refused():
    assert "192.168.1.5" in exposure_error(config("192.168.1.5"))
    assert "0.0.0.0" in exposure_error(config(None))


def test_lan_bind_with_key_is_allowed():
    assert exposure_error(config("0.0.0.0", key="secret")) is None
