import socket
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs


def run_server(host='127.0.0.1', port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server running on http://{host}:{port}")
        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                request = client_socket.recv(1024).decode("utf-8")
                if not request:
                    continue
                response, status_code = handle_request(request, client_address)
                status_line = f"HTTP/1.1 {status_code} {HTTPStatus(status_code).phrase}\r\n"
                headers = "Content-Type: text/plain\r\n\r\n"
                client_socket.sendall(status_line.encode('utf-8'))
                client_socket.sendall(headers.encode('utf-8'))
                client_socket.sendall(response.encode('utf-8'))


def handle_request(request, client_address):
    request_line = request.splitlines()[0]
    method, url, _ = request_line.split(' ')

    status_code = 200

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if 'status' in query_params:
        try:
            status_code = int(query_params['status'][0])
            if status_code not in {status.value for status in HTTPStatus}:
                status_code = 400
        except ValueError:
            status_code = 200

    status_message = HTTPStatus(status_code).phrase

    headers = [
        f"Request Method: {method}",
        f"Request Source: {client_address}",
        f"Response Status: {status_code} {status_message}"
    ]

    for line in request.splitlines():
        if ':' in line:
            headers.append(line)

    body = "\r\n".join(headers) + "\r\n"

    response = body
    return response, status_code


if __name__ == '__main__':
    run_server()