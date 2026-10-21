"""Loopback-only portfolio preview with HTTP byte-range support for media."""
import argparse
from pathlib import Path
import os
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class MediaHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.range_remaining = None
        value = self.headers.get('Range')
        path = self.translate_path(self.path)
        if not value or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', value.strip())
        if not match or not any(match.groups()):
            return super().send_head()
        start_text, end_text = match.groups()
        if start_text:
            start = int(start_text)
            end = min(int(end_text), size - 1) if end_text else size - 1
        else:
            count = int(end_text)
            start, end = max(0, size - count), size - 1
            if count == 0:
                start = size
        if start >= size or start > end:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        file = open(path, 'rb')
        file.seek(start)
        self.range_remaining = end - start + 1
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Length', str(self.range_remaining))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Last-Modified', self.date_time_string(os.fstat(file.fileno()).st_mtime))
        self.end_headers()
        return file

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def copyfile(self, source, outputfile):
        if self.range_remaining is None:
            return super().copyfile(source, outputfile)
        remaining = self.range_remaining
        while remaining:
            data = source.read(min(65536, remaining))
            if not data:
                break
            outputfile.write(data)
            remaining -= len(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--directory', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1', args.port), partial(MediaHandler, directory=args.directory)).serve_forever()
