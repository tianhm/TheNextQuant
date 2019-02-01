# -*- coding:utf-8 -*-

"""
外盘订单薄实时数据 基类

Author: HuangTao
Date:   2018/08/17
Update: None
"""

import copy
import asyncio

from quant.event import EventOrderbook


class Orderbook:
    """ 外盘订单薄实时数据 基类
    """

    def __init__(self, platform, symbol):
        self._platform = platform       # 平台
        self._symbol = symbol           # 交易对
        self._asks = []                 # 买单
        self._bids = []                 # 卖单
        self._ask1 = None               # 买一
        self._bid1 = None               # 卖一
        self._timestamp = None          # 更新时间戳（秒）
        self._callback_handlers = []    # 外盘行情有更新的时候，执行的回调函数

        # 订阅事件回调
        EventOrderbook(self._platform, self._symbol).subscribe(self.on_event_orderbook)

    @property
    def platform(self):
        return self._platform

    @property
    def symbol(self):
        return self._symbol

    @property
    def asks(self):
        return copy.copy(self._asks)

    @property
    def bids(self):
        return copy.copy(self._bids)

    @property
    def ask1(self):
        return copy.copy(self._ask1)

    @property
    def bid1(self):
        return copy.copy(self._bid1)

    @property
    def timestamp(self):
        return self._timestamp

    def register_callback(self, callback):
        """ 注册事件回调 当订单薄有更新，执行回调函数
        @param callback 回调函数，必须是async异步函数
            async def callback_func(platform, symbol, asks, bids, timestamp):
                pass
        """
        self._callback_handlers.append(callback)

    async def on_event_orderbook(self, event):
        """ 事件回调 行情信息
        """
        orderbook = EventOrderbook().duplicate(event)
        if orderbook.platform != self._platform or orderbook.symbol != self._symbol:
            return

        self._asks = orderbook.asks
        self._bids = orderbook.bids
        self._bid1 = self._bids[0] if self._bids else None
        self._ask1 = self._asks[0] if self._asks else None
        self._timestamp = orderbook.timestamp

        for func in self._callback_handlers:
            asyncio.get_event_loop().create_task(func(self.platform, self.symbol, self.asks, self.bids, self.timestamp))
