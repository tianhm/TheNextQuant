# -*- coding:utf-8 -*-

"""
常量

Author: HuangTao
Date:   2018/07/31
Update: None
"""


# 交易所名称
COINSUPER = "coinsuper"
BCOIN = "bcoin"
GBX = "gbx"
BITFINEX = "bitfinex"
BINANCE = "binance"
OKEX = "okex"  # OKEx现货
OKEX_FUTURE = "okex_future"  # OKEx交割合约
OKEX_SWAP = "okex_swap"  # OKEx永续合约
BITMEX = "bitmex"
HUOBI = "huobi"
HUOBI_FUTURE = "huobi_future"
OKCOIN = "okcoin"
COINBASE = "coinbase"
MXC = "mxc"
DERIBIT = "deribit"
KRAKEN = "kraken"
BITSTAMP = "bitstamp"
GEMINI = "gemini"
FOTA = "fota"
BIBOX = "bibox"

# 自定义
CUSTOM = "custom"


# 各个交易所对应的交易对名字不一样，需要有一个表来做统一转换
SYMBOL_MAP = {
    "BCHABC/BTC": {
        OKEX: "BCH/BTC",
    },
    "BCHSV/BTC": {
        OKEX: "BSV/BTC",
    },
    "BCHABC/XBT": {
        KRAKEN: "BCH/XBT",
    },
    "BCHSV/XBT": {
        KRAKEN: "BSV/XBT",
    }
}
