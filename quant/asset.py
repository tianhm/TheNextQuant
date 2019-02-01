# -*- coding:utf-8 -*-

"""
交易所的账户资金

Author: HuangTao
Date:   2018/05/17
Update: None
"""

import copy
import asyncio

from quant.utils import logger
from quant.event import EventAsset
from quant.data import AssetData


class Asset:
    """ 账户资金
    """
    """ self._assets
    {
        "BTC": {
            "free": 11.11,
            "locked": 22.22,
            "total": 33.33
        },
        ...
    }
    """

    def __init__(self, platform, account, symbol):
        """ 初始化
        @param platform 交易平台
        @param account 交易账户
        @param symbol 交易对
        """
        self._platform = platform   # 交易平台
        self._account = account     # 交易账户
        self._timestamp = 0         # 资产更新时间戳
        self._symbol = symbol       # 交易对
        self._assets = {}           # 所有资金详情
        self._key_x = self._symbol.split('/')[0]
        self._key_y = self._symbol.split('/')[1]
        self._asset_x = None        # 交易对的资金详情 {"free": 11.11, "locked": 22.22, "total": 33.33}
        self._asset_y = None        # 交易对的资金详情 {"free": 11.11, "locked": 22.22, "total": 33.33}
        self._callback_handlers = []    # 资产有更新的时候，执行的回调函数

        # 初始化资产数据库对象
        self._asset_db = AssetData()

        # 订阅事件 资产更新
        EventAsset(platform, account).subscribe(self._on_event_asset)
        # 从数据库加载初始化资产
        asyncio.get_event_loop().create_task(self._load_asset())

    @property
    def assets(self):
        """ 返回账户里所有余额不为0的资产
        """
        return copy.copy(self._assets)

    @property
    def timestamp(self):
        """ 返回资产更新时间戳(秒)
        """
        return self._timestamp

    @property
    def asset_x(self):
        """ 返回交易对左边的资产，如BTC/USD交易对，此时返回BTC的资产
        """
        return copy.copy(self._asset_x)

    @property
    def asset_y(self):
        """ 返回交易对左边的资产，如BTC/USD交易对，此时返回USD的资产
        """
        return copy.copy(self._asset_y)

    def register_callback(self, callback):
        """ 注册回调函数，当账户资产有更新，执行回调函数
        @param callback 回调函数
            async def callback_func(assets):
                pass
        """
        self._callback_handlers.append(callback)

    async def _on_event_asset(self, event):
        """ 资产更新事件
        @param event 事件对象
        """
        asset = EventAsset().duplicate(event)
        if asset.platform != self._platform:
            return
        if asset.account != self._account:
            return
        self._assets = asset.assets
        self._timestamp = asset.timestamp
        self._asset_x = self._assets.get(self._key_x)
        self._asset_y = self._assets.get(self._key_y)
        for func in self._callback_handlers:
            asyncio.get_event_loop().create_task(func(self.assets))
        logger.debug('assets updated. assets:', self._assets, caller=self)

    async def _load_asset(self):
        """ 启动程序的时候，加载最新的资产数据
        """
        asset = await self._asset_db.get_latest_asset(self._platform, self._account)
        if not asset:
            logger.warn('no find any asset data in db, platform:', self._platform, 'account:', self._account,
                        caller=self)
            return
        for key, value in asset.items():
            self._assets[key] = value
        self._asset_x = self._assets.get(self._key_x)
        self._asset_y = self._assets.get(self._key_y)
        logger.info('assets loads success. assets:', self._assets, caller=self)
