import os
from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/{path:.*}')
async def handle_get(req):
    if 'path' not in req.match_info:
        raise web.HTTPBadRequest(text='path is required')
    if '..' in req.match_info['path']:
        raise web.HTTPBadRequest(text='path is invalid')

    file_path = os.path.join(req.app['files_root'], req.match_info['path'])

    if not os.path.isfile(file_path):
        raise web.HTTPNotFound()

    return web.FileResponse(file_path)


@routes.post('/{path:.*}')
async def handle_post(req):
    if 'path' not in req.match_info:
        raise web.HTTPBadRequest(text='path is required')
    if '..' in req.match_info['path']:
        raise web.HTTPBadRequest(text='path is invalid')

    file_path = os.path.join(req.app['files_root'], req.match_info['path'])

    reader = await req.multipart()

    async for part in reader:
        if part.name == 'file':
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            size = 0
            with open(file_path, 'wb+') as f:
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)

    return web.Response(text='ok')


if __name__ == '__main__':
    try:
        files_path = os.getenv('FILES_ROOT')
        assert files_path is not None
    except AssertionError:
        print('USAGE: python3 ./http_repo/app.py')
        print('Required envs: FILES_ROOT')
        exit(1)

    app = web.Application()
    app['files_root'] = files_path
    app.add_routes(routes)
    web.run_app(app)
