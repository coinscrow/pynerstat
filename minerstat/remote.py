from zope.interface import implementer
from twisted.internet.interfaces import IProtocol
from minerstat.utils import Config
from urllib import parse
import treq
from typing import Dict, Optional
import json
import asyncio
from twisted.logger import Logger


@implementer(IProtocol)
class MinerStatRemoteProtocol:
    log = Logger()

    def __init__(self, config: Config, treq=treq) -> None:
        self.config = config
        self.treq = treq

    def make_full_url(self, component: str) -> str:
        return parse.urljoin(
            self.config.api_base, component + ".php?"
        ) + parse.urlencode(self.make_url_params())

    def make_url_params(
            self,
            params: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        new_params = {
            "token": self.config.accesskey,
            "worker": self.config.worker
        }
        if params:
            new_params.update(params)
        return new_params

    async def make_request(
            self,
            method: str,
            resource: str,
            params: Optional[Dict[str, str]] = None,
            body: Optional[str] = None
    ) -> str:
        url = self.make_full_url(resource)
        params = self.make_url_params()
        response = await self.treq.request(
            method=method,
            url=url,
            params=params,
            body=body)
        content = await response.content()
        return content

    async def get_request(
            self,
            resource,
            params: Optional[Dict[str, str]] = None,
    ) -> str:
        content = await self.make_request("GET", resource, params)
        return content

    async def algoinfo(self) -> str:
        content = await self.get_request("bestquery")
        return content

    def dlconf(self):
        pass

    async def send_log(self, res_data):
        await self.make_request(
            "POST", "getstat",
            body=json.dumps({"mes": res_data}))
        self.log.info("Package sent.")
        self.log.debug("Package sent: {data}", data=res_data)

    async def algo_check(self):
        futs = [
            self.get_request("bestquerytext"),
            self.get_request("bestquery"),
            self.get_request("dualresponse")
        ]
        bq, b, dr = await asyncio.gather(*futs)

    def dispatch_remote_command(self):
        pass

    def poll_remote(self):
        pass