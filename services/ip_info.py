def get_ip_info(force_refresh=False):
    return {
        "ip": "192.168.1.100",
        "tor": False,
        "geo": {
            "city": "Paris",
            "region": "Île-de-France",
            "country": "FR",
            "loc": "48.8566,2.3522",
            "org": "Fake ISP"
        },
        "alert": ""
    }