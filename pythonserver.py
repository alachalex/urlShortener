#import statements
from http.server import BaseHTTPRequestHandler, HTTPServer

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import urllib.parse
import random
import string


class S(BaseHTTPRequestHandler):
    #opens a new spreadsheet for a database using google api
    #takes credentials for google api from json file
    def make_gdrive_connection(self):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        spread = client.open('URLShortner')
        self.sheet = spread.sheet1

    #retrieve from spreadsheet
    def get(self):
        #print the path
        print("header", self.headers)
        print("path", self.path)
        #check spread
        self.make_gdrive_connection()
        values = self.sheet.col_values(2)
        print(values)
        ind = 0
        try:
            ind = values.index(self.path)
        except Exception:
            ind = 0
        print("index", ind)
        self.send_response(301)
        #get from spreadsheet
        self.send_header('Location', self.sheet.col_values(1)[ind])
        self.end_headers()

    #post to spreadsheet database
    def post(self):
        print(self.headers)
        # Gets the size of data
        content_length = int(self.headers['Content-Length'])
        # Gets the data itself
        post_data = self.rfile.read(content_length) 
        long_url = urllib.parse.unquote(post_data.decode()[4:])
        #creates a short url
        shortUrl = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        #updates the google drive database
        self.make_gdrive_connection()
        start = len(self.sheet.col_values(1))+1
        self.sheet.update_cell(start, 1, long_url)
        self.sheet.update_cell(start, 2, "/"+shortUrl)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        #writes the encoded file
        self.wfile.write(("http://"+self.headers['Host']+"/"+shortUrl).encode('utf-8'))
 
#initializes server 
def run(server_class=HTTPServer, handler_class=S, port=8083):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Start')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('End')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
