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
        # the coding format used 
        format = 'utf-8'
        # receives the request 
        self.data = self.request.recv(1024).strip()
        # printing the request received 
        print(f"Got a request of: {self.data}\n")
        
        # decoding the received request from bytes to string
        received_request = self.data.decode(format)

        # if the received request wasn't an empty request then continue with the code in the condition
        if received_request != '':
            request_info = received_request.splitlines()[0]
            method, path, http_version = request_info.split(" ")
            # print statements commented out below used for self testing please ignore 
            # print(request_info)
            # print(method)
            # print(path)
            # print(not_needed)

            # checks if there are errors 
            final_response = self.test_if_valid(request_info)

            # if there are no errors and received an empty byte string then execute the line in if condition and move in to valid_response method
            if final_response == b'':
                final_response = self.valid_response(path)
        
        # if the received request was an empty request then continue with the code in the condition
        if received_request == '':
            # send an empty path to valid response 
            final_response = self.valid_response('')

        # send the response to the client
        self.request.sendall(final_response)

    def test_if_valid(self, request_info):
        # collects the method path and http version 
        method, path, http_version = request_info.split(" ")
        # if the request was empty then display 400 bad request error message
        if request_info == "":
            return b'HTTP/1.1 400 Bad Request\r\n'
        # if anything else other than GET was used then 405 display method not allowed message
        if method != "GET":
            return b'HTTP/1.1 405 Method Not Allowed\r\n'
        # if the http version mentioned was anything other than http/1.1 then dislpay 400 bad request 
        if http_version != "HTTP/1.1":
            return b'HTTP/1.1 400 Bad Request\r\n'
        # if the path mentioned doesn't exist then display 404 not found message 
        if os.path.exists('www' + path) == False:
            return b'HTTP/1.1 404 Not Found \r\n'
        # if the path exists and there are no errors return a blank byte string which will be used later in code to proceed 
        if os.path.exists('www' + path):
            return b''
    
    def valid_response(self, path):
        # if path to the file is empty or NULL then return bad response
        if path == '':
            return b'HTTP/1.1 400 Bad Request\r\n'
        
        # prevents directory traversal attacks by removing all .. in the path to stop from traversing back and only allows traversal within the www folder
        if '..' in path:
            path = path.split('..')[-1]
        
        # directory of file starting from the www folder 
        main_path = 'www' + path

        # checks if the file or directory mentioned exists or not 
        if os.path.exists('www' + path):
            # checks if it is a folder 
            if os.path.isfile('www' + path) == False:
                # if the folder ends with a / then redirect to index.html in that folder
                if path[-1] == '/':
                    main_path += 'index.html'
                    # checks if index.html exists in the directory. If not present then give error
                    if os.path.exists(main_path) == False:
                        return b'HTTP/1.1 404 Not Found \r\n'

                # checks if the path mentioned was incorrect and shows the redirected location to the directory 
                if path[-1] != '/':
                    current_datetime = datetime.datetime.utcnow()
                    formatted_date = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
                    return b'HTTP/1.1 301 Moved Permanently \r\n' + b'Location: ' + path.encode('utf-8') + b'/\r\n' + b'Date: ' + formatted_date.encode('utf-8') + b' \r\n'

            # reads file contents.
            with open(main_path, 'rb') as fh:
                file_data = fh.read().decode('utf-8')
                file_data = file_data.encode()

                # print statements below were for testing purposes please ignore
                # print(file_data)
            # print(file_data)

            # calculates the length or size of the data in file 
            length_file_data = (str(len(file_data))).encode('utf-8')

            # shows the date and time of the execution
            current_datetime = datetime.datetime.utcnow()
            formatted_date = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # handles the mimes for the html and css files as instructed and returns normal content type if the files were anything except html and css
            file_format = main_path.split('.')[-1]
            if file_format == 'html':
                main_file_format = b'Content-type: text/html \r\n'
            elif file_format == 'css':
                main_file_format = b'Content-type: text/css \r\n'
            else: 
                main_file_format = b'Content-type: ' + file_format.encode('utf-8') + b' \r\n'

            # returns the response
            response_header = b'HTTP/1.1 200 OK \r\n' + b'Date: ' + formatted_date.encode('utf-8') + b' \r\n' + main_file_format + b'Content-length: ' + length_file_data + b'\r\n\r\n' + file_data
            print(response_header)
            return response_header
            # return b'HTTP/1.1 200 OK \r\n' + b'Date: ' + formatted_date.encode('utf-8') + b' \r\n' + main_file_format + b'Content-length: ' + length_file_data + b' \r\n' + file_data

        # if file mentioned doesn't exist then returns the error 
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
