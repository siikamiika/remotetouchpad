import ctypes
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qsl

ME = dict(
    MOUSEEVENTF_ABSOLUTE=0x8000,
    MOUSEEVENTF_LEFTDOWN=0x0002,
    MOUSEEVENTF_LEFTUP=0x0004,
    MOUSEEVENTF_MIDDLEDOWN=0x0020,
    MOUSEEVENTF_MIDDLEUP=0x0040,
    MOUSEEVENTF_MOVE=0x0001,
    MOUSEEVENTF_RIGHTDOWN=0x0008,
    MOUSEEVENTF_RIGHTUP=0x0010,
    MOUSEEVENTF_WHEEL=0x0800,
    MOUSEEVENTF_XDOWN=0x0080,
    MOUSEEVENTF_XUP=0x0100,
    MOUSEEVENTF_HWHEEL=0x01000
    )

def move_mouse(x, y, absolute=False):
    dwFlags = ME['MOUSEEVENTF_MOVE']
    if absolute:
        dwFlags |= ME['MOUSEEVENTF_ABSOLUTE']
    ctypes.windll.user32.mouse_event(ctypes.c_ulong(dwFlags), ctypes.c_long(x), ctypes.c_long(y), 0, ctypes.c_ulong(0))


def mouse_button(event):
    ctypes.windll.user32.mouse_event(ME[event], 0, 0, 0, 0)

class InputHandler(BaseHTTPRequestHandler):

    protocol_version = 'HTTP/1.1'

    def move_mouse(self):
        x = int(self.qs_list['x'])
        y = int(self.qs_list['y'])
        move_mouse(x, y)

    def mouse_button(self):
        mouse_button(self.qs_list['event'])

    def do_GET(self):
        self.url_parsed = urlparse(self.path)
        self.qs_list = dict(parse_qsl(self.url_parsed.query))
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        data = b''
        if self.url_parsed.path == '/':
            with open('index.html', 'rb') as f:
                data = f.read()
        elif self.url_parsed.path == '/move_mouse':
            self.move_mouse()
        elif self.url_parsed.path == '/mouse_button':
            self.mouse_button()
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

class InputServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == "__main__":
    srv = InputServer(('', 9877), InputHandler)
    srv.serve_forever()
