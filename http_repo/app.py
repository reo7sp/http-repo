import os
from aiohttp import web
from werkzeug.utils import secure_filename
from binascii import crc32

routes = web.RouteTableDef()


def make_abs_path(rel_path, files_root):
    rel_path = secure_filename(rel_path)
    rel_path_hash = hex(crc32(rel_path.encode()))[2:]
    abs_path = os.path.join(files_root, rel_path_hash[0:2], rel_path_hash[2:4], rel_path)
    return abs_path


@routes.get('/{path:.*}')
async def handle_get(req):
    if 'path' not in req.match_info:
        raise web.HTTPBadRequest(text='path is required')
    abs_path = make_abs_path(req.match_info['path'], req.app['files_root'])

    if not os.path.isfile(abs_path):
        raise web.HTTPNotFound()

    return web.FileResponse(abs_path)


@routes.post('/{path:.*}')
async def handle_post(req):
    if 'path' not in req.match_info:
        raise web.HTTPBadRequest(text='path is required')
    abs_path = make_abs_path(req.match_info['path'], req.app['files_root'])

    try:
        reader = await req.multipart()
    except:
        return web.HTTPBadRequest(text='multipart request is required')
    file_is_written = False

    async for part in reader:
        if part.name == 'file':
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            size = 0
            with open(abs_path, 'wb') as f:
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)
            file_is_written = True

    if file_is_written:
        return web.Response(text='ok')
    else:
        return web.HTTPBadRequest(text='file is required')


if __name__ == '__main__':
    files_path = os.getenv('FILES_ROOT')
    if files_path is None:
        print('USAGE: python3 ./http_repo/app.py')
        print('Required envs: FILES_ROOT')
        exit(1)

    app = web.Application()
    app['files_root'] = files_path
    app.add_routes(routes)
    web.run_app(app)
