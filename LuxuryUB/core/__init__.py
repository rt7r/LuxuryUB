from aiohttp import web
from .decorators import check_owner
from .route import routes

# LuxuryUB Metadata Storage
CMD_INFO = {}
PLG_INFO = {}
GRP_INFO = {}
BOT_INFO = []
LOADED_CMDS = {}

LUXURY_DEV = 1165225957

async def web_server():
    web_app = web.Application(client_max_size=30000000) 
    web_app.add_routes(routes)
    return web_app