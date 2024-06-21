
#!/usr/bin/env python3
"""
License: MIT License
Copyright (c) 2023 Miel Donkers
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
#import logging
import json
import predictor_service

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        #logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        if self.path == "/leaderboard":
            self._set_response()
            self.wfile.write(json.dumps(predictor_service.leaderboard_entries).encode('utf-8'))
        elif self.path == "/compute_leaderboard":
            self._set_response()
            predictor_service.compute_leaderboard()
            self.wfile.write(json.dumps(predictor_service.leaderboard_entries).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write("404 - Not Found".encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Gets the size of data
        post_data = self.rfile.read(content_length)  # Gets the data itself
        #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n", str(self.path), str(self.headers), post_data.decode('utf-8'))

        # Check if the path is "/add_invocation"
        if self.path == "/add_invocation":
            try:
                # Parse the JSON data from the POST request
                data = json.loads(post_data.decode('utf-8'))
                timestamp = data['timestamp']
                trace_id = data['trace_id']
                call_count = int(data['call_count'])

                # Call the add_trace_entry function with the extracted data
                predictor_service.add_trace_entry(timestamp, trace_id, call_count)

                # Send a success response
                self._set_response()
                self.wfile.write("POST request for {} succeeded".format(self.path).encode('utf-8'))
            except (KeyError, json.JSONDecodeError) as e:
                # Send an error response if there is a problem with the JSON data
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_message = "Error processing POST data: {}".format(str(e))
                self.wfile.write(error_message.encode('utf-8'))
        else:
            # Handle other POST paths if necessary
            self._set_response()
            self.wfile.write("POST request for {} not handled".format(self.path).encode('utf-8'))

    # this avoids constant prints
    def log_message(self, format, *args):
        return
    

#I use this  to have some level of multithreading, but the multithreading is only when precesing the requests, the sockert that receives the request is stil single thread and sequencial.
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def run(server_class=HTTPServer, handler_class=S, port=8085):
    #logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    #httpd = server_class(server_address, handler_class)
    httpd = ThreadedHTTPServer(server_address, handler_class)
    print('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    predictor_service.init()

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

