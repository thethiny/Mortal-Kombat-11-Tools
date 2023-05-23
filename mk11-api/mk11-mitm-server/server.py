import base64
import json
import re

import requests
from flask import Flask, Response, request
from ag_conv import json_to_ag

app = Flask("MK11_MITM_Server")

MK11_DOMAIN = "https://mk11-api.wbagora.com"
MK11_DOMAIN_PATTERN = re.compile(r"(?i)(?:^" + re.escape(MK11_DOMAIN) + r")(?:/)(.*)")


def get_resources(path: str):
    return "".join(MK11_DOMAIN_PATTERN.findall(path))


def detect_path_type(path: str):
    resource = get_resources(path)
    print("Resource", resource)
    if not resource:
        return "test"
    if resource == "auth":
        return "auth"
    if resource == "access":
        return "access"
    if resource == "ssc/invoke/premium_shop_products":
        return "shop"


def mk_redirect(url):
    print("Redirect Request", url)
    # request.headers.pop("Host", None)
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k:v for k, v in request.headers.items() if k != "Host"},
        data=request.get_data(),
        params=request.args,
        cookies=request.cookies,
        allow_redirects=False,
    )

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    print("Attempting Redirect")
    response = Response(resp.content, resp.status_code, headers)
    b64 = base64.b64encode(resp.content.strip())
    # b64 = base64.encodebytes(resp.content.strip()).decode("ascii") # Inserts line breaks so the length of each line is 76, useful for RSA
    print("Response", b64)
    return response


@app.route(
    "/mitm/<path:url>",
    methods=[
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
    ],
)
def mk11_test(url: str):
    print(request, url)
    # return mk_redirect(url)

    path_type = detect_path_type(url)
    print("type", path_type)
    if path_type == "auth":
        return mk_redirect(url)
    if path_type == "access":
        return mk_redirect(url)
    if path_type == "shop":
        print("Assigning Shop")
        with open("premium_shop.json") as file:
            data = json.load(file)
        data = json_to_ag(data)
        print(base64.encodestring(data).decode())

        # Test
        r = requests.request(
            method=request.method,
            url=url,
            headers={k:v for k, v in request.headers.items() if k != "Host"},
            data=request.get_data(),
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False,
        )

        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]

        headers = [
            (k, v) for k,v in r.raw.headers.items() if k.lower() not in excluded_headers
        ]


        print(r.content)
        print(data)

        return Response(data, r.status_code, headers)

    return mk_redirect(url)

if __name__ == "__main__":
    app.run(port=12181)