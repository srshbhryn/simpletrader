from enum import Enum


class Asset(Enum):
	USD = 1
	RLS = 2
	BTC = 10
	ETH = 11
	LTC = 12
	USDT = 13
	XRP = 14
	BCH = 15
	BNB = 16
	EOS = 17
	DOGE = 18
	XLM = 19
	TRX = 20
	ADA = 21
	XMR = 22
	XEM = 23
	IOTA = 24
	ETC = 25
	DASH = 26
	ZEC = 27
	NEO = 28
	QTUM = 29
	XTZ = 30
	PMN = 31
	LINK = 32
	DAI = 33
	DOT = 34
	UNI = 35
	AAVE = 36
	SOL = 37
	MATIC = 38
	FIL = 39
	GRT = 40
	THETA = 41
	SHIB = 42
	ONEINCH = 50
	ALICE = 51
	ALPHA = 52
	ANKR = 53
	ARPA = 54
	ATA = 55
	ATOM = 56
	AVAX = 57
	AXS = 58
	BAKE = 59
	BAL = 60
	BAND = 61
	BAT = 62
	BEL = 63
	BLZ = 64
	BTT = 65
	C98 = 66
	CELR = 67
	CHR = 68
	COMP = 69
	COTI = 70
	CTK = 71
	CTSI = 72
	DODO = 73
	EGLD = 74
	FTM = 75
	GALA = 76
	IOTX = 77
	KNC = 78
	KSM = 79
	LINA = 80
	LIT = 81
	MASK = 82
	MKR = 83
	NEAR = 84
	OCEAN = 85
	ONT = 86
	REEF = 87
	SFP = 88
	SNX = 89
	SUSHI = 90
	SXP = 91
	TLM = 92
	UNFI = 93
	YFI = 94
	YFII = 95
	ZIL = 96
	MANA = 97
	SAND = 98
	APE = 99
	ONE = 100
	WBTC = 101
	USDC = 102
	ALGO = 103
	LUNA = 104
	KLAY = 105
	GMT = 106
	CHZ = 107
	VET = 108
	QNT = 109
	BUSD = 110
	FLOW = 111
	HBAR = 112
	PGALA = 113
	EGALA = 114
	ENJ = 115
	OP = 116
	CRV = 117
	CAKE = 118
	LDO = 119
	DYDX = 120
	GNO = 121
	APT = 122
	FLR = 123
	LRC = 124
	ENS = 125
	LPT = 126
	GLM = 127
	API3 = 128
	ELF = 129
	DAO = 130
	CVC = 131
	NMR = 132
	STORJ = 133
	CVX = 134
	SNT = 135
	SLP = 136
	NFT = 137
	SRM = 138
	ANT = 139
	ILV = 140
	ICP = 142
	HNT = 143
	BABYDOGE = 144


class Exchange(Enum):
	Nobitex = 1


class PairType:
	def __init__(self, id, base_asset, quote_asset):
		self.id = id
		self.base_asset = base_asset
		self.quote_asset = quote_asset


class Pair(Enum):
	UsdtRls = PairType(1, Asset.USDT, Asset.RLS)
	BtcUsdt = PairType(1000, Asset.BTC, Asset.USDT)
	BtcRls = PairType(1001, Asset.BTC, Asset.RLS)
	WbtcUsdt = PairType(1010, Asset.WBTC, Asset.USDT)
	WbtcRls = PairType(1011, Asset.WBTC, Asset.RLS)
	EthUsdt = PairType(1020, Asset.ETH, Asset.USDT)
	EthRls = PairType(1021, Asset.ETH, Asset.RLS)
	DogeUsdt = PairType(1030, Asset.DOGE, Asset.USDT)
	DogeRls = PairType(1031, Asset.DOGE, Asset.RLS)
	ShibUsdt = PairType(1040, Asset.SHIB, Asset.USDT)
	ShibRls = PairType(1041, Asset.SHIB, Asset.RLS)


class MarketType:
	def __init__(self, id, exchange, pair):
		self.id = id
		self.exchange = exchange
		self.pair = pair


class Market(Enum):
	NobitexUsdtRls = MarketType(1, Exchange.Nobitex, Pair.UsdtRls)
	NobitexBtcUsdt = MarketType(2, Exchange.Nobitex, Pair.BtcUsdt)
	NobitexBtcRls = MarketType(3, Exchange.Nobitex, Pair.BtcRls)
	NobitexWbtcUsdt = MarketType(4, Exchange.Nobitex, Pair.WbtcUsdt)
	NobitexWbtcRls = MarketType(5, Exchange.Nobitex, Pair.WbtcRls)
	NobitexEthUsdt = MarketType(6, Exchange.Nobitex, Pair.EthUsdt)
	NobitexEthRls = MarketType(7, Exchange.Nobitex, Pair.EthRls)
	NobitexDogeUsdt = MarketType(8, Exchange.Nobitex, Pair.DogeUsdt)
	NobitexDogeRls = MarketType(9, Exchange.Nobitex, Pair.DogeRls)
	NobitexShibUsdt = MarketType(10, Exchange.Nobitex, Pair.ShibUsdt)
	NobitexShibRls = MarketType(11, Exchange.Nobitex, Pair.ShibRls)
