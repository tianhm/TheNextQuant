# -*- coding:utf-8 -*-

"""
外盘ticker行情实时数据 基类

Author: HuangTao
Date:   2018/07/31
Update: None
"""

import asyncio

from quant.event import EventTicker


class TickerBase:
    """ 外盘ticker实时行情 基类
    """

    def __init__(self, platform, symbol):
        self._platform = platform       # 平台
        self._symbol = symbol           # 交易对
        self._ask = None                # 买一价
        self._ask_quantity = None       # 卖一量
        self._bid = None                # 买一价
        self._bid_quantity = None       # 买一量
        self._timestamp = None          # 更新时间戳（秒）

        self._callback_handlers = []    # 外盘行情有更新的时候，执行的回调函数

        # 订阅事件回调
        EventTicker(self.platform, self._symbol).subscribe(self.on_event_ticker)

    @property
    def platform(self):
        return self._platform

    @property
    def symbol(self):
        return self._symbol

    @property
    def ask(self):
        return self._ask

    @property
    def ask_quantity(self):
        return self._ask_quantity

    @property
    def bid(self):
        return self._bid

    @property
    def bid_quantity(self):
        return self._bid_quantity

    @property
    def timestamp(self):
        return self._timestamp

    def register_callback(self, callback):
        """ 注册事件回调 当ticker行情有更新，执行回调函数
        @param callback 回调函数，必须是async异步函数
            async def callback_func(platform, ticker):
                pass
        """
        self._callback_handlers.append(callback)

    async def on_event_ticker(self, event):
        """ 事件回调 行情信息
        """
        event = EventTicker().duplicate(event)
        if event.platform != self._platform:
            return
        if event.symbol != self._symbol:
            return

        self._ask = event.ask
        self._ask_quantity = event.ask_quantity
        self._bid = event.bid
        self._bid_quantity = event.bid_quantity
        self._timestamp = event.timestamp

        for func in self._callback_handlers:
            asyncio.get_event_loop().create_task(func(event.platform, event.data))
