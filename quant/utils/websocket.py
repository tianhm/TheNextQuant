# -*— coding:utf-8 -*-

"""
websocket接口封装

Author: HuangTao
Date:   2018/06/29
Update: 2018/10/30  1. 数据处理函数采用异步任务，避免处理异常导致程序退出；
"""

import json
import aiohttp
import asyncio

from quant.utils import tools
from quant.utils import logger
from quant.heartbeat import heartbeat


class Websocket:
    """ websocket接口封装
    """

    def __init__(self, url, proxy=None, check_conn_interval=10, send_hb_interval=10):
        """ 初始化
        @param url 建立websocket的地址
        @param proxy http代理
        @param check_conn_interval 检查websocket连接时间间隔
        @param send_hb_interval 发送心跳时间间隔
        """
        self._url = url
        self._proxy = proxy
        self._ws = None  # websocket连接对象
        self._check_conn_interval = check_conn_interval
        self._send_hb_interval = send_hb_interval
        self.heartbeat_msg = None  # 心跳消息

    def initialize(self):
        """ 初始化
        """
        # 注册服务 检查连接是否正常
        heartbeat.register(self._check_connection, self._check_conn_interval)
        # 注册服务 发送心跳
        heartbeat.register(self._send_heartbeat_msg, self._send_hb_interval)
        # 建立websocket连接
        asyncio.get_event_loop().run_until_complete(self._connect())

    async def _connect(self):
        logger.info('url:', self._url, 'proxy:', self._proxy, caller=self)
        session = aiohttp.ClientSession()
        self.ws = await session.ws_connect(self._url, proxy=self._proxy)
        asyncio.get_event_loop().create_task(self.receive())
        await self.connected_callback()

    async def _reconnect(self):
        """ 重新建立websocket连接
        """
        logger.warn('reconnecting websocket right now!', caller=self)
        await self._connect()

    async def connected_callback(self):
        """ 连接建立成功的回调函数
        * NOTE: 子类继承实现
        """
        pass

    async def receive(self):
        """ 接收消息
        """
        async for msg in self.ws:
            self._last_receive_ts = tools.get_cur_timestamp()
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except:
                    data = msg.data
                await asyncio.get_event_loop().create_task(self.process(data))
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await asyncio.get_event_loop().create_task(self.process_binary(msg.data))
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                logger.warn('receive event CLOSED:', msg, caller=self)
                await asyncio.get_event_loop().create_task(self._reconnect())
                return
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error('receive event ERROR:', msg, caller=self)
            else:
                logger.warn('unhandled msg:', msg, caller=self)

    async def process(self, msg):
        """ 处理websocket上接收到的消息 text 类型
        * NOTE: 子类继承实现
        """
        raise NotImplementedError

    async def process_binary(self, msg):
        """ 处理websocket上接收到的消息 binary类型
        * NOTE: 子类继承实现
        """
        raise NotImplementedError

    async def _check_connection(self, *args, **kwargs):
        """ 检查连接是否正常
        """
        # 检查websocket连接是否关闭，如果关闭，那么立即重连
        if not self.ws:
            logger.warn('websocket connection not connected yet!', caller=self)
            return
        if self.ws.closed:
            await asyncio.get_event_loop().create_task(self._reconnect())
            return

    async def _send_heartbeat_msg(self, *args, **kwargs):
        """ 发送心跳给服务器
        """
        if self.heartbeat_msg:
            if isinstance(self.heartbeat_msg, dict):
                await self.ws.send_json(self.heartbeat_msg)
            elif isinstance(self.heartbeat_msg, str):
                await self.ws.send_str(self.heartbeat_msg)
            else:
                logger.error('send heartbeat msg failed! heartbeat msg:', self.heartbeat_msg, caller=self)
                return
            logger.debug('send ping message:', self.heartbeat_msg, caller=self)
