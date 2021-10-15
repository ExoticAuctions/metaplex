from enum import IntEnum
from construct import Switch
from construct import Int8ul, Int32ul, Int64ul, Pass, Bytes
from construct import Struct as cStruct
from typing import Any, List, NamedTuple, Optional, Union
from solana._layouts.shared import PUBLIC_KEY_LAYOUT

class InstructionType(IntEnum):
	CANCEL_BID=0
	CREATE_AUCTION=1
	CLAIM_BID=2
	END_AUCTION=3
	START_AUCTION=4
	SET_AUTHORITY=5
	PLACE_BID=6
	CREATE_AUCTION_V2=7
	PLACE_BID_V2=8

class PriceFloorType(IntEnum):
	EMPTY=0
	MinimumPrice=1

class AuctionState(IntEnum):
	Created=0
	Started=1
	Ended=2

class BidStateType(IntEnum):
	EnglishAuction=0
	OpenEdition=1

class WinnerLimitType(IntEnum):
	Unlimited = 0
	Capped =1

_PRICEFLOOR_LAYOUT = cStruct(
	"pricefloor_type" / Int8ul,
	"args"
	/ Switch(
		lambda this : this.pricefloor_type,
		{
			PriceFloorType.EMPTY : Int8ul[32],
			PriceFloorType.MinimumPrice : Int64ul[4],
		},
	),
)

_BID_LAYOUT = cStruct(
	"bidder" / PUBLIC_KEY_LAYOUT,
	"amount" / Int64ul,
	"bidder_token" / PUBLIC_KEY_LAYOUT,
	"bidder_pot_token" / PUBLIC_KEY_LAYOUT,
)

_BID_STATE_LAYOUT = cStruct(
	"bid_state_type" / Int8ul,
	"bid_num" / Int32ul,
	"bidders" / _BID_LAYOUT[lambda this : this.bid_num],
	"max" / Int64ul #usize
)

_WINNER_LIMIT_LAYOUT = cStruct(
	"winner_type" / Int8ul,
	"args" / Int64ul, #usize
)

_CREATE_AUCTION_LAYOUT = cStruct(
	"winners"	/ _WINNER_LIMIT_LAYOUT,
	"exist_end_auction_at" / Int8ul,
	"end_auction_at" / Switch( lambda this: this.exist_end_auction_at,{ 0 : Pass, 1: Int64ul}) , 
	"exist_end_auction_gap" / Int8ul,
	"end_auction_gap"	/  Switch( lambda this: this.exist_end_auction_gap,{ 0 : Pass, 1: Int64ul}),
	"token_mint"	/ PUBLIC_KEY_LAYOUT,
	"authority"	/ PUBLIC_KEY_LAYOUT,
	"resource"	/ PUBLIC_KEY_LAYOUT,
	"price_floor"	/ _PRICEFLOOR_LAYOUT,
	"exist_tick_size" / Int8ul,
	"tick_size"	/ Switch( lambda this: this.exist_tick_size, { 0 : Pass, 1: Int64ul}),
	"exist_gap_tick_size_percentage" / Int8ul,
	"gap_tick_size_percentage"	/ Switch( lambda this: this.exist_gap_tick_size_percentage, { 0 : Pass, 1: Int8ul}),
)

_CLAIM_BID_LAYOUT = cStruct(
	"resource" / PUBLIC_KEY_LAYOUT,
)

_END_AUCTION_LAYOUT = cStruct(
	"resource" / PUBLIC_KEY_LAYOUT,
	"exist_reveal" / Int8ul,
	"reveal" / Switch(lambda this: this.exist_reveal,{ 0 : Pass, 1 : Int64ul[2] })
)

_START_AUCTION_LAYOUT = cStruct(
	"resource" / PUBLIC_KEY_LAYOUT,
)

_PLACE_BID_LAYOUT = cStruct(
	"amount" /	Int64ul,
	"resource" / PUBLIC_KEY_LAYOUT,
)

_CANCEL_BID_LAYOUT = cStruct(
	"resource" / PUBLIC_KEY_LAYOUT
)

_CREATE_AUCTION_V2_LAYOUT = cStruct(
	"winners"	/ _WINNER_LIMIT_LAYOUT,
	"exist_end_auction_at" / Int8ul,
	"end_auction_at" / Switch( lambda this: this.exist_end_auction_at,{ 0 : Pass, 1: Int64ul}) , 
	"exist_end_auction_gap" / Int8ul,
	"end_auction_gap"	/  Switch( lambda this: this.exist_end_auction_gap,{ 0 : Pass, 1: Int64ul}),
	"token_mint"	/ PUBLIC_KEY_LAYOUT,
	"authority"	/ PUBLIC_KEY_LAYOUT,
	"resource"	/ PUBLIC_KEY_LAYOUT,
	"price_floor"	/ _PRICEFLOOR_LAYOUT,
	"exist_tick_size" / Int8ul,
	"tick_size"	/ Switch( lambda this: this.exist_tick_size, { 0 : Pass, 1: Int64ul}),
	"exist_gap_tick_size_percentage" / Int8ul,
	"gap_tick_size_percentage"	/ Switch( lambda this: this.exist_gap_tick_size_percentage, { 0 : Pass, 1: Int8ul}),
	"exist_reward_size" / Int8ul,
	"reward_size"	/ Switch( lambda this: this.exist_reward_size, { 0 : Pass, 1: Int64ul}),
)

INSTRUCTION_LAYOUT = cStruct(
	"instruction_type" / Int8ul,
	"args"
	/ Switch(
		lambda this:this.instruction_type,
		{
			InstructionType.CANCEL_BID : _CANCEL_BID_LAYOUT,
			InstructionType.CREATE_AUCTION : _CREATE_AUCTION_LAYOUT,
			InstructionType.CLAIM_BID : _CLAIM_BID_LAYOUT,
			InstructionType.END_AUCTION : _END_AUCTION_LAYOUT,
			InstructionType.START_AUCTION : _START_AUCTION_LAYOUT,
			InstructionType.SET_AUTHORITY : Pass,
			InstructionType.PLACE_BID : _PLACE_BID_LAYOUT,
			InstructionType.CREATE_AUCTION_V2 : _CREATE_AUCTION_V2_LAYOUT,
			InstructionType.PLACE_BID_V2 : _PLACE_BID_LAYOUT,
		},
	),
)

AUCTION_LAYOUT = cStruct(
	"authority" / PUBLIC_KEY_LAYOUT,
	"token_mint" / PUBLIC_KEY_LAYOUT,
	"exist_last_bid" / Int8ul,
	"last_bid" / Switch( lambda this:this.exist_last_bid, {0 : Pass, 1 : Int64ul}),
	"exist_ended_at" / Int8ul,
	"ended_at" / Switch( lambda this:this.exist_ended_at, {0 : Pass, 1 : Int64ul}),
	"exist_end_auction_at" / Int8ul,
	"end_auction_at" / Switch( lambda this:this.exist_end_auction_at, {0 : Pass, 1 : Int64ul}),
	"exist_end_auction_gap" / Int8ul,
	"end_auction_gap" / Switch( lambda this:this.exist_end_auction_gap, {0 : Pass, 1 : Int64ul}),
	"price_floor" / _PRICEFLOOR_LAYOUT,
	"state" / Int8ul,
	"bid_state" / _BID_STATE_LAYOUT,
)

AUCTION_EXTENDED_LAYOUT = cStruct(
	"total_uncancelled_bids" / Int64ul,
	"exist_tick_size" / Int8ul,
	"tick_size" / Switch( lambda this:this.exist_tick_size, {0 : Pass, 1 : Int64ul}),
	"exist_gap_tick_size_percentage" / Int8ul,
	"gap_tick_size_percentage"	/ Switch( lambda this: this.exist_gap_tick_size_percentage, { 0 : Pass, 1: Int8ul}),
)

AUCTION_V2_EXTENDED_LAYOUT = cStruct(
	"total_uncancelled_bids" / Int64ul,
	"exist_tick_size" / Int8ul,
	"tick_size" / Switch( lambda this:this.exist_tick_size, {0 : Pass, 1 : Int64ul}),
	"exist_gap_tick_size_percentage" / Int8ul,
	"gap_tick_size_percentage"	/ Switch( lambda this: this.exist_gap_tick_size_percentage, { 0 : Pass, 1: Int8ul}),
	"exist_reward_size" / Int8ul,
	"reward_size"	/ Switch( lambda this: this.exist_reward_size, { 0 : Pass, 1: Int64ul}),
	"exist_prev_bidder_token" / Int8ul,
	"prev_bidder_token" / Switch( lambda this : this.exist_prev_bidder_token, {0 : Pass, 1 : PUBLIC_KEY_LAYOUT})
)