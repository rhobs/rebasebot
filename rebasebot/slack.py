def send_message(webhook_url, msg):
    if webhook_url is None:
        return
    requests.post(webhook_url, json={"text": msg})
