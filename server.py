#  coding: utf-8 
import socketserver
import os.path
import datetime

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
    
    def handle(self):
        format = 'utf-8'
        # receives the request 
        self.data = self.request.recv(1024).strip()
        # printing the request received 
        print(f"Got a request of: {self.data}\n")
        
        received_request = self.data.decode(format)
        request_info = received_request.splitlines()[0]
        # print statements commented out below used for self testing 
        # print(request_info)
        # print(method)
        # print(path)
        # print(not_needed)

        # checks if there are errors 
        final_response = self.test_if_valid(request_info)

        # if there are no errors execute then execute line in if condition
        if final_response == b'':
            final_response = self.valid_response(request_info)
        
        # send the response to the client
        self.request.sendall(final_response)

    def test_if_valid(self, request_info):
        method, path, http_version = request_info.split(" ")
        if request_info == "":
            return b'HTTP/1.1 400 Bad Request\r\n'
        if method != "GET":
            return b'HTTP/1.1 405 Method Not Allowed\r\n'
        if http_version != "HTTP/1.1":
            return b'HTTP/1.1 400 Bad Request\r\n'
        if os.path.exists('www' + path) == False:
            return b'HTTP/1.1 404 Not Found \r\n'
        if os.path.exists('www' + path):
            return b''
    
    def valid_response(self, request_info):
        method, path, http_version = request_info.split(" ")
        main_path = 'www' + path
        if os.path.exists('www' + path):
            if os.path.isfile('www' + path) == False:
                if path[-1] == '/':
                    main_path += 'index.html'

                    if os.path.exists(main_path) == False:
                        return b'HTTP/1.1 404 Not Found \r\n'
            
                if path[-1] != '/':
                    current_datetime = datetime.datetime.utcnow()
                    formatted_date = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
                    return b'HTTP/1.1 301 Moved Permanently \r\n' + b'Location: ' + path.encode('utf-8') + b'/\r\n' + b'Date: ' + formatted_date.encode('utf-8') + b' \r\n'
            
            with open(main_path, 'rb') as fh:
                file_data = fh.read()

            length_file_data = (str(len(file_data))).encode('utf-8')

            current_datetime = datetime.datetime.utcnow()
            formatted_date = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')

            file_format = main_path.split('.')[-1]
            if file_format == 'html':
                main_file_format = b'Content-type: text/html \r\n'
            elif file_format == 'css':
                main_file_format = b'Content-type: text/css \r\n'
            else: 
                main_file_format = b'Content-type: ' + file_format.encode('utf-8') + b' \r\n'

            return b'HTTP/1.1 200 OK \r\n' + b'Date: ' + formatted_date.encode('utf-8') + b' \r\n' + main_file_format + b'Content-length: ' + length_file_data + b' \r\n' + file_data + b' \r\n'

        else:
            return b'HTTP/1.1 404 Not Found \r\n'

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    # displays that the server is on 
    print("SERVER HAS STARTED ........... \n")
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
