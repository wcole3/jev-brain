from scripts.check_bind import exposure_error


def port(host_ip: str | None, target: int) -> dict:
    return {"target": target, "published": str(target)} | ({"host_ip": host_ip} if host_ip else {})


def config(host_ip: str | None, key: str = "", vllm_ip: str | None = "127.0.0.1") -> dict:
    gateway = {"ports": [port(host_ip, 9000)], "environment": {"GATEWAY_API_KEY": key}}
    return {"services": {"gateway": gateway, "vllm": {"ports": [port(vllm_ip, 8000)]}}}


def test_loopback_needs_no_key():
    assert exposure_error(config("127.0.0.1")) is None


def test_lan_bind_without_key_is_refused():
    assert "192.168.1.5" in exposure_error(config("192.168.1.5"))
    assert "0.0.0.0" in exposure_error(config(None))


def test_lan_bind_with_key_is_allowed():
    assert exposure_error(config("0.0.0.0", key="secret")) is None


def test_vllm_beyond_loopback_is_refused_even_with_a_key():
    assert "vllm binds 0.0.0.0" in exposure_error(config("127.0.0.1", key="secret", vllm_ip=None))
    assert "vllm binds 192.168.1.5" in exposure_error(config("127.0.0.1", vllm_ip="192.168.1.5"))

