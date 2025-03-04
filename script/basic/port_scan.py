#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: orleven

from lib.util.aiohttputil import open_connection
from lib.core.enums import ServicePortMap
from script import BaseScript

class Script(BaseScript):

    def __init__(self):
        BaseScript.__init__(self)
        self.name = 'PortScan'
        self.service_type = ServicePortMap.UNKNOWN

    async def prove(self):
        if self.url is None:
            msg = "stats\r\n"
            try:
                reader, writer = await open_connection(host=self.host, port=self.port)
                writer.write(bytes(msg, 'utf-8'))
                await writer.drain()
            except:
                pass
            else:
                self.ping = True
                try:
                    message = await reader.read(1024)
                    self.service_type = await self.service_match(message)
                except:
                    self.service_type = self.service_type[0]
                finally:
                    writer.close()

        else:
            await self.get_url()
            self.service_type = ServicePortMap.WEB[0]

        if self.url:
            if self.protocol is None:
                self.protocol = self.url[:self.url.index("://")]
            if self.base_url is None:
                self.base_url = f"{self.protocol}://{self.host}:{self.port}/"

        if self.ping:
            yield self.service_type

    async def exec(self):
        yield self.prove()

    async def upload(self):
        yield self.prove()

    async def rebound(self):
        yield self.prove()

    async def service_match(self, message=None):

        await self.get_url()

        if self.url:
            return ServicePortMap.WEB[0]

        elif message is not None:
            message = str(message).lower()
            if b"AMQP" in message:
                return ServicePortMap.RABBITMQ[0]
            elif b'smtp' in message or b'spam' in message or b'Esmtp' in message:
                return ServicePortMap.SMTP[0]
            elif b'SSH' in message:
                return ServicePortMap.SSH[0]
            elif b'mysql' in message or b'caching_sha2_password' in message:
                return ServicePortMap.MYSQL[0]
            elif b'redis' in message or b'Err wrong number of arguments for' in message or b'ERR unknown command' in message:
                return ServicePortMap.REDIS[0]
            elif b'FTP' in message:
                return ServicePortMap.FTP[0]
            elif b'rsync' in message:
                return ServicePortMap.RSYNC[0]
            elif b'http' in message:
                return ServicePortMap.WEB[0]
            else:
                print(self.host, self.port, message)
        return ServicePortMap.UNKNOWN[0]


