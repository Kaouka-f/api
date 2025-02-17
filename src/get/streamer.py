from flask import Flask, Response, request, abort
import mimetypes
import os
from flask import Response
from werkzeug.utils import secure_filename
BASE_DIRECTORY = "/opt/files"

def secure_path(subpath):
    # Secure each segment of the path
    safe_segments = [secure_filename(segment) for segment in subpath.split('/')]
    return os.path.join(*safe_segments)


def stream_file(subpath):
    safe_subpath = secure_path(subpath)
    file_path = os.path.join(BASE_DIRECTORY, safe_subpath)

    if not file_path.startswith(os.path.abspath(BASE_DIRECTORY)):
        abort(403, "Access denied")

    if not os.path.isfile(file_path):
        abort(404, "File not found or access denied")

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('Range', None)
    length = file_size
    if range_header:
        byte_range = range_header.strip().split('=')[1]
        start, end = byte_range.split('-')
        start = int(start)
        end = int(end) if end else file_size - 1
        length = end - start + 1

        def generate(length):
            with open(file_path, 'rb') as f:
                f.seek(start)
                while length > 0:
                    chunk_size = min(4096, length)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    length -= len(chunk)
                    yield chunk

        response = Response(generate(length), content_type=mime_type, status=206)
        response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Length'] = length
        return response
    else:
        def generate():
            with open(file_path, 'rb') as f:
                while chunk := f.read(4096):
                    yield chunk

        response = Response(generate(), content_type=mime_type)
        response.headers['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        response.headers['Content-Length'] = file_size
        return response