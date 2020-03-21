import requests

def fetch_satellite_location(id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    url = 'https://fanqiang.network'

    r = requests.get(url=url, headers=headers)
    html = r.content.decode('utf-8')

    return 'location'

