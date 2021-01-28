#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    HTTP_200 = b'HTTP/1.1 200 OK'
    HTTP_404 = b'HTTP/1.1 404 Not Found'
    CT_HTML = b'Content-Type: text/html'
    CT_CSS = b'Content-Type: text/css'
    
    def handle(self):
        # "For stream services, self.request is a TCP socket object connected 
        # to the client" -py docs
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s" % self.data)
        self.data = self.data.decode("utf-8")
        print(self.data)
        # Parse data for request type and respond accordingly
        # eg. serve /www/index.html
        parts = self.data.splitlines() # edge cases? probably should use regex.
        print(parts)
        method = None
        for req_method in ["GET","POST","DELETE","PUT"]:
            if req_method in parts[0]:
                method = req_method
        # In lieu of a switch statement...
        if method=="GET":
            # What exactly do they want?
            (m, url, http) = parts[0].split()
            print(m, url, http)
            #if url != '/': # as long as we're not getting root...
            if url[0]=='/':
                url = url[1:]
            if "www" not in url:
                url = "www/" + url
            print(url)
            try:
                target = open(url, mode='r+b').read() # bytes object
            except FileNotFoundError:
                target = "NotFound"
            except IsADirectoryError:
                # Maybe they are trying to get root?
                target = bytes(url,'utf-8') 
            
            if target == "NotFound":
                to_send = self.HTTP_404+b'\n\n' \
                        + self.CT_HTML+b'\n\n' \
                        + b'<p>404 Not Found</p>'
            elif ".html" in url:
                to_send = self.HTTP_200+b'\n' \
                        + self.CT_HTML+b'\n\n' \
                        + target
            elif ".css" in url:
                to_send = self.HTTP_200+b'\n' \
                        + self.CT_CSS+b'\n\n' \
                        + target
            else:
                to_send = self.HTTP_200+b'\n' \
                        + self.CT_HTML+b'\n\n' \
                        + target
            self.request.sendall(to_send)
        else: # Some other method I don't know...
            self.request.sendall(bytearray("OK",'utf-8'))
        print()
        


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
