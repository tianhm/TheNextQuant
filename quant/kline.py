# -*- coding:utf-8 -*-

"""
外盘K线实时数据 基类

Author: HuangTao
Date:   2018/07/31
Update: 2018/21/16  1. 增加5分钟K线、15分钟K线；
"""

import asyncio

from quant.event import EventKline, EventKline5Min, EventKline15Min


KLINE_1MIN = 'kline.1min'  # 1分钟K线
KLINE_5MIN = 'kline.5min'  # 5分钟K线
KLINE_15MIN = 'kline.15min'  # 15分钟K线


class KLine:
    """ 外盘K线实时数据 基类
    """

    def __init__(self, platform, symbol, range_type=KLINE_1MIN):
        """ 初始化
        @param platform 交易平台
        @param symbol 交易对
        @param range_type K线类型 1min 5min 15min，默认为 1min
        """
        self._platform = platform  # 交易平台
        self._symbol = symbol  # 交易对
        self._open = None  # 开盘价
        self._high = None  # 最高价
        self._low = None  # 最低价
        self._close = None  # 收盘价
        self._volume = None  # 交易量
        self._timestamp = None  # 更新时间戳（秒）

        self._range_type = range_type
        self._callback_handlers = []    # 外盘K线数据有更新的时候，执行的回调函数

        # 订阅事件回调
        if range_type == KLINE_1MIN:
            EventKline(self.platform, self.symbol).subscribe(self.on_event_kline)
        elif range_type == KLINE_5MIN:
            EventKline5Min(self.platform, self.symbol).subscribe(self.on_event_kline)
        elif range_type == KLINE_15MIN:
            EventKline15Min(self.platform, self.symbol).subscribe(self.on_event_kline)

    @property
    def platform(self):
        return self._platform

    @property
    def symbol(self):
        return self._symbol

    @property
    def open(self):
        return self._open

    @property
    def high(self):
        return self._high

    @property
    def low(self):
        return self._low

    @property
    def close(self):
        return self._close

    @property
    def volume(self):
        return self._volume

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def range_type(self):
        return self._range_type

    def register_callback(self, callback):
        """ K线数据更新回调
        @param callback 回调函数
            async def callback_func(platform, kline):
                pass
        """
        self._callback_handlers.append(callback)

    async def on_event_kline(self, event):
        """ 事件回调 K线信息
        """
        event = EventKline().duplicate(event)
        if event.platform != self._platform:
            return
        if event.symbol != self._symbol:
            return
        self._open = event.open
        self._high = event.high
        self._low = event.low
        self._close = event.close
        self._volume = event.volume
        self._timestamp = event.timestamp
        for func in self._callback_handlers:
            asyncio.get_event_loop().create_task(func(event.platform, event.data))
