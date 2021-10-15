from enum import IntEnum
from typing import Any, List, NamedTuple, Optional, Union
from solana.publickey import PublicKey
from solana.transaction import AccountMeta, TransactionInstruction
from solana.sysvar import SYSVAR_RENT_PUBKEY,SYSVAR_CLOCK_PUBKEY
from solana.rpc.api import Client
from solana.system_program import SYS_PROGRAM_ID
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
from construct import Int8ul, Int32ul, Int64ul, Pass, Bytes
from _layout import *
import time
import base58
import base64

PREFIX = "auction"
EXTENDED = "extended"

def get_auction_data(
	conn : Client,
	program_id : PublicKey,
	resource : PublicKey,
	):
	print("Auction Data")
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	auction_raw_data=conn.get_account_info(auction_pubkey)["result"]["value"]["data"][0]
	auction_data=AUCTION_LAYOUT.parse(base64.b64decode(auction_raw_data))
	# print(auction_data)
	return auction_data

def get_auction_extended_data(
	conn : Client,
	program_id : PublicKey,
	resource : PublicKey,
	):
	seeds=[b'auction',bytes(program_id),bytes(resource),b'extended']
	auction_extended_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	auction_extended_raw_data=conn.get_account_info(auction_extended_pubkey)["result"]["value"]["data"][0]
	auctioin_extended_data=AUCTION_EXTENDED_LAYOUT.parse(base64.b64decode(auction_extended_raw_data))
	return auctioin_extended_data

def get_auction_v2_extended_data(
	conn : Client,
	program_id : PublicKey,
	resource : PublicKey,
	):
	seeds=[b'auction',bytes(program_id),bytes(resource),b'extended']
	auction_extended_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	auction_extended_raw_data=conn.get_account_info(auction_extended_pubkey)["result"]["value"]["data"][0]
	auctioin_extended_data=AUCTION_V2_EXTENDED_LAYOUT.parse(base64.b64decode(auction_extended_raw_data))
	return auctioin_extended_data

def create_auction_instruction(
	program_id : PublicKey,
	payer : PublicKey,
	authority : PublicKey,
	end_auction_at : Int64ul = 0,
	end_auction_gap : Int64ul = 0,
	resource : PublicKey = PublicKey(1),
	token_mint : PublicKey = PublicKey(2),
	winners : int = 1,
	price_floor : int = 0,
	gap_tick_size_percentage : Int8ul = 0,
	tick_size : Int64ul = 0,
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(resource),b'extended']
	auction_extended_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	data = INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.CREATE_AUCTION,args=dict(
			winners=dict(winner_type=WinnerLimitType.Capped,args=winners),
			exist_end_auction_at = 0,
			end_auction_at = None,
			exist_end_auction_gap = 0,
			end_auction_gap = None,
			token_mint = bytes(token_mint),
			authority=bytes(authority),
			resource=bytes(resource),
			price_floor=dict(pricefloor_type=PriceFloorType.MinimumPrice,args=[price_floor,0,0,0]),
			exist_tick_size=1,
			tick_size=tick_size,
			exist_gap_tick_size_percentage=1,
			gap_tick_size_percentage=gap_tick_size_percentage
		)))
	parse_data = INSTRUCTION_LAYOUT.parse(data)
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=payer,is_signer=True,is_writable=True),
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=auction_extended_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=SYSVAR_RENT_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYS_PROGRAM_ID,is_signer=False,is_writable=False),
		],
		program_id=program_id,
		data=data
	)

def create_auction_v2_instruction(
	program_id : PublicKey,
	payer : PublicKey,
	authority : PublicKey,
	end_auction_at : Int64ul = 0,
	end_auction_gap : Int64ul = 0,
	resource : PublicKey = PublicKey(1),
	token_mint : PublicKey = PublicKey(2),
	winners : int = 1,
	price_floor : int = 0,
	gap_tick_size_percentage : Int8ul = 0,
	tick_size : Int64ul = 0,
	reward_size : Int64ul = 0,
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(resource),b'extended']
	auction_extended_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	data = INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.CREATE_AUCTION_V2,args=dict(
			winners=dict(winner_type=WinnerLimitType.Capped,args=winners),
			exist_end_auction_at = 0,
			end_auction_at = None,
			exist_end_auction_gap = 0,
			end_auction_gap = None,
			token_mint = bytes(token_mint),
			authority=bytes(authority),
			resource=bytes(resource),
			price_floor=dict(pricefloor_type=PriceFloorType.MinimumPrice,args=[price_floor,0,0,0]),
			exist_tick_size=1,
			tick_size=tick_size,
			exist_gap_tick_size_percentage=1,
			gap_tick_size_percentage=gap_tick_size_percentage,
			exist_reward_size=1,
			reward_size=reward_size,
		)))
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=payer,is_signer=True,is_writable=True),
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=auction_extended_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=SYSVAR_RENT_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYS_PROGRAM_ID,is_signer=False,is_writable=False),
		],
		program_id=program_id,
		data=data
	)

def start_auction_instruction(
	program_id : PublicKey,
	authority : PublicKey,
	resource : PublicKey
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	data = INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.START_AUCTION,args=dict(
			resource=bytes(resource)
		)))
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=authority,is_signer=True,is_writable=True),
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=SYSVAR_CLOCK_PUBKEY,is_signer=False,is_writable=False)
		],
		program_id=program_id,
		data=data
	)

def end_auction_instruction(
	program_id : PublicKey,
	authority : PublicKey,
	resource : PublicKey,
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	data = INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.END_AUCTION,args=dict(
			resource=bytes(resource),
			exist_reveal=0,
			reveal=None
		)))
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=authority,is_signer=True,is_writable=True),
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=SYSVAR_CLOCK_PUBKEY,is_signer=False,is_writable=False)
		],
		program_id=program_id,
		data=data
	)

def place_bid_instruction(
	program_id : PublicKey,
	bidder : PublicKey,
	bidder_token : PublicKey,
	bidder_pot_token : PublicKey,
	token_mint : PublicKey,
	transfer_authority : PublicKey,
	payer : PublicKey,
	resource : PublicKey,
	amount : Int64ul
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(resource),b'extended']
	auction_extended_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(auction_pubkey),bytes(bidder)]
	bidder_pot_pubkey=PublicKey.find_program_address(seeds,program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(auction_pubkey),bytes(bidder),b'metadata']
	bidder_meta_pubkey=PublicKey.find_program_address(seeds,program_id)[0]
	data = INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.PLACE_BID,args=dict(
			amount=amount,
			resource=bytes(resource)
		)))
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=bidder,is_signer=True,is_writable=True),
			AccountMeta(pubkey=bidder_token,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_pot_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_pot_token,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_meta_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=auction_extended_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=token_mint,is_signer=False,is_writable=True),
			AccountMeta(pubkey=transfer_authority,is_signer=True,is_writable=False),
			AccountMeta(pubkey=payer,is_signer=True,is_writable=False),
			AccountMeta(pubkey=SYSVAR_CLOCK_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYSVAR_RENT_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYS_PROGRAM_ID,is_signer=False,is_writable=False),
			AccountMeta(pubkey=TOKEN_PROGRAM_ID,is_signer=False,is_writable=False)
		],
		program_id=program_id,
		data=data
	)

def place_bid_instruction_v2(
	program_id : PublicKey,
	bidder : PublicKey,
	bidder_token : PublicKey,
	bidder_pot_token : PublicKey,
	token_mint : PublicKey,
	transfer_authority : PublicKey,
	payer : PublicKey,
	resource : PublicKey,
	amount : Int64ul,
	prev_bidder : PublicKey,
	prev_bidder_token : PublicKey,
	prev_bidder_pot_token : PublicKey,
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(resource),b'extended']
	auction_extended_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(auction_pubkey),bytes(bidder)]
	bidder_pot_pubkey=PublicKey.find_program_address(seeds,program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(auction_pubkey),bytes(bidder),b'metadata']
	bidder_meta_pubkey=PublicKey.find_program_address(seeds,program_id)[0]
	data = INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.PLACE_BID_V2,args=dict(
			amount=amount,
			resource=bytes(resource)
		)))
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=bidder,is_signer=True,is_writable=True),
			AccountMeta(pubkey=bidder_token,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_pot_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_pot_token,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_meta_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=auction_extended_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=token_mint,is_signer=False,is_writable=True),
			AccountMeta(pubkey=transfer_authority,is_signer=True,is_writable=False),
			AccountMeta(pubkey=payer,is_signer=True,is_writable=False),
			AccountMeta(pubkey=SYSVAR_CLOCK_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYSVAR_RENT_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYS_PROGRAM_ID,is_signer=False,is_writable=False),
			AccountMeta(pubkey=TOKEN_PROGRAM_ID,is_signer=False,is_writable=False),
			AccountMeta(pubkey=prev_bidder,is_signer=False,is_writable=True),
			AccountMeta(pubkey=prev_bidder_token,is_signer=False,is_writable=True),
			AccountMeta(pubkey=prev_bidder_pot_token,is_signer=False,is_writable=True),
		],
		program_id=program_id,
		data=data
	)

def cancel_bid_instruction(
	program_id : PublicKey,
	bidder : PublicKey,
	bidder_token : PublicKey,
	bidder_pot_token : PublicKey,
	token_mint : PublicKey,
	resource : PublicKey
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(resource),b'extended']
	auction_extended_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(auction_pubkey),bytes(bidder)]
	bidder_pot_pubkey=PublicKey.find_program_address(seeds,program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(auction_pubkey),bytes(bidder),b'metadata']
	bidder_meta_pubkey=PublicKey.find_program_address(seeds,program_id)[0]
	data = INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.CANCEL_BID,args=dict(
			resource=bytes(resource)
		)))
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=bidder,is_signer=True,is_writable=True),
			AccountMeta(pubkey=bidder_token,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_pot_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_pot_token,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_meta_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=auction_extended_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=token_mint,is_signer=False,is_writable=True),
			AccountMeta(pubkey=SYSVAR_CLOCK_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYSVAR_RENT_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYS_PROGRAM_ID,is_signer=False,is_writable=False),
			AccountMeta(pubkey=TOKEN_PROGRAM_ID,is_signer=False,is_writable=False)
		],
		program_id=program_id,
		data=data
	)

def set_authority_instruction(
	program_id : PublicKey,
	resource : PublicKey,
	authority : PublicKey,
	new_authority : PublicKey
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	data=INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.SET_AUTHORITY,args=None))
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=authority,is_signer=True,is_writable=False),
			AccountMeta(pubkey=new_authority,is_signer=False,is_writable=False)
		],
		program_id=program_id,
		data=data
	)

def claim_bid_instruction(
	program_id : PublicKey,
	destination : PublicKey,
	authority : PublicKey,
	bidder : PublicKey,
	bidder_pot_token : PublicKey,
	token_mint : PublicKey,
	resource : PublicKey
	) -> TransactionInstruction:
	seeds=[b'auction',bytes(program_id),bytes(resource)]
	auction_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(resource),b'extended']
	auction_extended_pubkey = PublicKey.find_program_address(seeds, program_id)[0]
	seeds=[b'auction',bytes(program_id),bytes(auction_pubkey),bytes(bidder)]
	bidder_pot_pubkey=PublicKey.find_program_address(seeds,program_id)[0]
	data = INSTRUCTION_LAYOUT.build(dict(instruction_type=InstructionType.CLAIM_BID,args=dict(
			resource=bytes(resource)
		)))
	return TransactionInstruction(
		keys=[
			AccountMeta(pubkey=destination,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_pot_token,is_signer=False,is_writable=True),
			AccountMeta(pubkey=bidder_pot_pubkey,is_signer=False,is_writable=True),
			AccountMeta(pubkey=authority,is_signer=True,is_writable=False),
			AccountMeta(pubkey=auction_pubkey,is_signer=False,is_writable=False),
			AccountMeta(pubkey=bidder,is_signer=False,is_writable=False),
			AccountMeta(pubkey=token_mint,is_signer=False,is_writable=False),
			AccountMeta(pubkey=SYSVAR_CLOCK_PUBKEY,is_signer=False,is_writable=False),
			AccountMeta(pubkey=TOKEN_PROGRAM_ID,is_signer=False,is_writable=False),
			# AccountMeta(pubkey=auction_extended_pubkey,is_signer=False,is_writable=False)
		],
		program_id=program_id,
		data=data
	)