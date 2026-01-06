def get_created_id(response):
    try:
        data = response.json()
        return data["id"] if isinstance(data, dict) else int(data)
    except Exception:
        return int(response.text.strip())
