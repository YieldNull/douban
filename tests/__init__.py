def fake_response_from_file(file_name, url=None, meta=None):
    import os
    import codecs
    from scrapy.http import HtmlResponse, Request

    if not url:
        url = 'http://www.example.com'

    if meta:
        meta.update({'mid': 1291844})
    else:
        meta = {'mid': 1291844}

    request = Request(url=url, meta=meta)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    file_content = codecs.open(file_path, 'r', 'utf-8').read()

    response = HtmlResponse(url=url,
                            encoding='utf-8',
                            request=request,
                            body=file_content)

    return response


def fake_response_from_url(url, headers=None, meta=None):
    import requests
    from scrapy.http import HtmlResponse, Request

    resp = requests.get(url, headers=headers)

    if meta:
        meta.update({'mid': 1291844})
    else:
        meta = {'mid': 1291844}

    return HtmlResponse(url=url, status=resp.status_code, body=resp.text,
                        encoding='utf-8', request=Request(url=url, meta=meta))
