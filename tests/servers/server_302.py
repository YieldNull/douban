from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.log_message(' '.join(['{:s}:{:s}'.format(key, value) for (key, value) in self.headers.items()]))

        self.send_response(302)
        if self.path.find('sorry') > 0:
            self.send_header('Location', 'https://movie.douban.com/sorry?')
        else:
            self.send_header('Location', 'https://movie.douban.com/')
        self.end_headers()


if __name__ == '__main__':
    httpd = HTTPServer(('', 5000), Handler)
    print('Starting httpd...')
    httpd.serve_forever()
