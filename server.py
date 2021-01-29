#  coding: utf-8 
import socketserver
import os

# Copyright 2021 Abram Hindle, Eddie Antonio Santos, Hugh Bagan
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

    # Constant headers
    HTTP_200 = b'HTTP/1.1 200 OK'
    HTTP_301 = b'HTTP/1.1 301 Moved Permanently'
    HTTP_404 = b'HTTP/1.1 404 Not Found'
    HTTP_405 = b'HTTP/1.1 405 Method Not Allowed'
    CT_HTML = b'Content-Type: text/html'
    CT_CSS = b'Content-Type: text/css'
    
    def handle(self):
        # "self.request is a TCP socket object connected to the client" -docs
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s" % self.data)
        self.data = self.data.decode("utf-8")
        # Parse data for request type and respond accordingly
        parts = self.data.splitlines() # edge cases? probably should use regex
        print(parts)
        method = None
        for req_method in ["GET","POST","DELETE","PUT"]:
            if req_method in self.data: # probably bad, oh well
                method = req_method
        # In lieu of a switch statement or state machine...
        if method == "GET":
            (m, url, http) = parts[0].split()
            # Format the url for open()
            if url[0]=='/':
                url = url[1:]
            if "www/" not in url:
                url = "www/" + url
            # Get the requested file to be the payload, or handle edge cases
            try:
                payload = open(url, mode='r+b').read() # bytes object
            except (FileNotFoundError, PermissionError):
                payload = "NotFound"
            except IsADirectoryError:
                if url[len(url)-1] != '/': 
                    # Missing end slash / => redirect to correct path ending
                    url += '/'
                    payload = "Redirect"
                elif os.path.isfile(url+'index.html'):
                    # Serve this dir's index.html at /
                    # eg. /deep/ will display /deep/index.html
                    url += 'index.html'
                    payload = open(url, mode='r+b').read()
                else:
                    # This dir has no index.html, just do whatever
                    payload = bytes(url,'utf-8')+b'\n'
            # Assemble the response as bytes
            if payload == "NotFound":
                response = self.HTTP_404+b'\n' \
                         + self.CT_HTML+b'\n\n' \
                         + b'<p>404 Not Found</p>\n'
            elif payload =="Redirect":
                # Undo the formatting done above...
                url = url.replace("www/", "")
                url = '/' + url
                html_str = "<p>Moved to {}</p>".format(url)
                response = self.HTTP_301+b'\n' \
                         + b'Location: '+bytes(url,'utf-8')+b'\n' \
                         + self.CT_HTML+b'\n\n' \
                         + bytes(html_str,'utf-8')+b'\n'
                print(response)
            elif ".html" in url:
                response = self.HTTP_200+b'\n' \
                         + self.CT_HTML+b'\n\n' \
                         + payload
            elif ".css" in url:
                response = self.HTTP_200+b'\n' \
                         + self.CT_CSS+b'\n\n' \
                         + payload
            else:
                response = self.HTTP_200+b'\n' \
                         + self.CT_HTML+b'\n\n' \
                         + payload
        else: 
            # This method isn't handled; respond with 405
            response = self.HTTP_405+b'\n' \
                     + self.CT_HTML+b'\n\n' \
                     + b'<p>405 Method Not Allowed\n'
        self.request.sendall(response)
        print()


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
