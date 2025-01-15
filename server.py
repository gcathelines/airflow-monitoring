from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl


def start_tls11_server():
    httpd = HTTPServer(('localhost', 4443), SimpleHTTPRequestHandler)
    # Create an SSL context for TLS 1.1
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_1)
    # Use a self-signed or dummy certificate (can be generated with OpenSSL)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print("Serving on https://localhost:4443 with TLS 1.1 (unverified)")
    httpd.serve_forever()


start_tls11_server()
