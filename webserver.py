#!/usr/bin/env python3

import sys
import logging
import os
import ssl
import json

from aiohttp import web
import asyncio

event_loop = asyncio.get_event_loop()

class webserver_t(object):

    PARTITION_DIR="partitions"
    TOKEN_PREAMBLE="token "

    def __init__(self, port, is_verbose, host, akeyfile, ssl_context=None, logger=None):
        self.port = port
        self.host = host
        self.ssl_context = ssl_context
        if logger is None:
            logger = logging.getLogger(__name__)
            self._logger = logger
            if is_verbose:
                logging.basicConfig(level=logging.DEBUG)
        self._logger.info(f"Running on {self.host} on port {self.port}")

        self.authorisation_tokens = json.load(akeyfile)

    def verify_token(self, token: str) -> bool:
        return bool(list(filter(lambda t: t["Token"] == token, self.authorisation_tokens)))

    def request_bin(self, version: str, filename: str) -> web.Response | web.HTTPException:
        self._logger.debug(f"VERSION: '{version}', FILENAME: '{filename}'")
        partition_path = os.path.join(self.PARTITION_DIR, version, filename)
        if not os.path.exists(partition_path):
            self._logger.error(f"Partition path does not exist: {partition_path}")
            raise web.HTTPNotFound
        return web.FileResponse(
                partition_path,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )

    @staticmethod
    def _get_query_val(request: web.Request, key: str) -> str | web.HTTPException:
        val = request.rel_url.query.get(key)
        if val is None:
            self._logger.error(f"Not given {key}")
            raise web.HTTPNotFound
        return val

    async def rom_handler(self, request: web.Request) -> web.Response | web.HTTPException:
        self._logger.debug(f"HEADERS: {request.headers}")
        authorisation_token = request.headers.get("Authorization")
        if authorisation_token is None:
            self._logger.error("Not given authorisation token in header")
            raise web.HTTPForbidden
        if not authorisation_token.startswith(self.TOKEN_PREAMBLE):
            self._logger.error("Failed to interpret authorisation token")
            raise web.HTTPForbidden
        authorisation_token = authorisation_token[len(self.TOKEN_PREAMBLE):]
        if not self.verify_token(authorisation_token):
            self._logger.error(f"Invalid token '{authorisation_token}'")
            raise web.HTTPForbidden

        self._logger.debug(f"REQUEST: {request}")
        action      = self._get_query_val(request, 'action')
        version     = self._get_query_val(request, 'version')
        filename    = self._get_query_val(request, 'filename')
        if action != 'download_rom':
            self._logger.error("Dont know any other actions")
            raise web.HTTPNotFound
        return self.request_bin(version, filename)

    def run_server(self):
        app = web.Application()
        # URL: /v1/device/rom/?action=download_rom&version=v1&filename=mfg_nvs.bin
        app.router.add_route('GET', '/{version}/device/rom/{query:.*}', self.rom_handler)
        runner = web.AppRunner(app)
        event_loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, port=self.port, ssl_context=self.ssl_context)
        event_loop.run_until_complete(site.start())
        event_loop.run_forever()

def main(args):
    ssl_context = None
    if args.ssl:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(args.cert, args.key)

    svr = webserver_t(args.port, args.verbose, args.host, args.akeyfile, ssl_context=ssl_context)
    svr.run_server()

    return 0

if __name__ == "__main__":
    import argparse

    def get_args():
        parser = argparse.ArgumentParser(description="OSM Config GUI Server")
        parser.add_argument("-p", "--port"      , help="Serial Port"                    , required=False, type=int                  , default=8000          )
        parser.add_argument("-v", "--verbose"   , help="Verbose messages"               , action="store_true"                                               )
        parser.add_argument("-H", "--host"      , help="Host url"                       , type=str                                  , default='127.0.0.1'   )
        parser.add_argument("-s", "--ssl"       , help="Enable SSL"                     , action="store_true"                                               )
        parser.add_argument("--key"             , help="SSL Key path"                   , type=str                                  , default="key.pem"     )
        parser.add_argument("--cert"            , help="SSL Cert path"                  , type=str                                  , default="cert.pem"    )
        parser.add_argument("akeyfile"          , help="Authorisation key file"         , type=argparse.FileType("r")                                       )
        return parser.parse_args()

    args = get_args()
    sys.exit(main(args))
