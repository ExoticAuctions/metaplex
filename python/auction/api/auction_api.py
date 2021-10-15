import solana.system_program as sp
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.transaction import Transaction,TransactionInstruction,AccountMeta
from typing import Any,List,NamedTuple,Optional,Union
from construct import Int8ul, Int32ul, Int64ul, Pass, Bytes
import instruction as ax
from solana.blockhash import Blockhash
import time

def create_auction(
	conn : Client,
	program_id : PublicKey,
	payer : Keypair,
	resource : PublicKey,
	mint : PublicKey,
	max_winners : int =1,
	price_floor : int =0,
	gap_tick_size_percentage : Int8ul =0,
	tick_size : Int64ul =0
	):
	print("Creating auction...")
	transaction=Transaction()
	transaction.add(
		ax.create_auction_instruction(
			program_id=program_id,
			payer=payer.public_key,
			authority=payer.public_key,
			end_auction_at=None,
			end_auction_gap=None,
			resource=resource,
			token_mint=mint,
			winners=max_winners,
			price_floor=price_floor,
			gap_tick_size_percentage=gap_tick_size_percentage,
			tick_size=tick_size,
			)
		)
	resp=conn.send_transaction(transaction,payer)
	time.sleep(60)
	print("Completed.")

def create_auction_v2(
	conn : Client,
	program_id : PublicKey,
	payer : Keypair,
	resource : PublicKey,
	mint : PublicKey,
	max_winners : int =1,
	price_floor : int =0,
	gap_tick_size_percentage : Int8ul =0,
	tick_size : Int8ul =0,
	reward_size : Int64ul =0,
	):
	print("Creating auction v2...")
	transaction=Transaction()
	transaction.add(
		ax.create_auction_v2_instruction(
			program_id=program_id,
			payer=payer.public_key,
			authority=payer.public_key,
			end_auction_at=None,
			end_auction_gap=None,
			resource=resource,
			token_mint=mint,
			winners=max_winners,
			price_floor=price_floor,
			gap_tick_size_percentage=gap_tick_size_percentage,
			tick_size=tick_size,
			reward_size=reward_size,
			)
		)
	resp=conn.send_transaction(transaction,payer)
	time.sleep(40)
	print("Completed.")
	
def start_auction(
	conn : Client,
	program_id : PublicKey,
	authority : Keypair,
	resource : PublicKey,
	):
	print("Starting auction...")
	transaction=Transaction()
	transaction.add(
		ax.start_auction_instruction(
			program_id=program_id,
			authority=authority.public_key,
			resource=resource
			)
		)
	resp=conn.send_transaction(transaction,authority)
	time.sleep(30)
	print("Completed.")

def end_auction(
	conn : Client,
	program_id : PublicKey,
	authority : Keypair,
	resource : PublicKey,
	):
	print("Ending auction...")
	transaction=Transaction()
	transaction.add(
		ax.end_auction_instruction(
			program_id=program_id,
			authority=authority.public_key,
			resource=resource
			)
		)
	resp=conn.send_transaction(transaction,authority)
	time.sleep(40)
	print("Auction ended.")

def place_bid(
	conn : Client,
	program_id : PublicKey,
	payer : Keypair,
	bidder : Keypair,
	bidder_token : PublicKey,
	bidder_pot_token : PublicKey,
	transfer_authority : Keypair,
	resource : PublicKey,
	mint : PublicKey,
	amount : Int64ul,
	):
	print("Placing bid")
	transaction = Transaction()
	transaction.add(
		ax.place_bid_instruction(
			program_id=program_id,
			bidder=bidder.public_key,
			bidder_token=bidder_token,
			bidder_pot_token=bidder_pot_token,
			token_mint=mint,
			transfer_authority=transfer_authority.public_key,
			payer=payer.public_key,
			resource=resource,
			amount=amount,
			)
		)
	conn.send_transaction(transaction,bidder,transfer_authority,payer)
	time.sleep(30)
	print("Completed.")

def place_bid_v2(
	conn : Client,
	program_id : PublicKey,
	payer : Keypair,
	bidder : Keypair,
	bidder_token : PublicKey,
	bidder_pot_token : PublicKey,
	transfer_authority : Keypair,
	resource : PublicKey,
	mint : PublicKey,
	amount : Int64ul,
	prev_bidder : PublicKey,
	prev_bidder_token : PublicKey,
	prev_bidder_pot_token : PublicKey
	):
	print("Placing bid")
	transaction = Transaction()
	transaction.add(
		ax.place_bid_instruction_v2(
			program_id=program_id,
			bidder=bidder.public_key,
			bidder_token=bidder_token,
			bidder_pot_token=bidder_pot_token,
			token_mint=mint,
			transfer_authority=transfer_authority.public_key,
			payer=payer.public_key,
			resource=resource,
			amount=amount,
			prev_bidder=prev_bidder,
			prev_bidder_token=prev_bidder_token,
			prev_bidder_pot_token=prev_bidder_pot_token,
			)
		)
	conn.send_transaction(transaction,bidder,transfer_authority,payer)
	time.sleep(30)
	print("Completed.")

def cancel_bid(
	conn : Client,
	program_id : PublicKey,
	payer : Keypair,
	bidder : Keypair,
	bidder_token : PublicKey,
	bidder_pot_token : PublicKey,
	resource : PublicKey,
	mint : PublicKey
	):
	print("Ending bid.")
	transaction=Transaction()
	transaction.add(
		ax.cancel_bid_instruction(
			program_id=program_id,
			bidder=bidder.public_key,
			bidder_token=bidder_token,
			bidder_pot_token=bidder_pot_token,
			token_mint=mint,
			resource=resource
			)
		)
	conn.send_transaction(transaction,bidder,payer)
	print("Completed.")

def claim_bid(
	conn : Client,
	program_id : PublicKey,
	payer : Keypair,
	authority : Keypair,
	bidder : PublicKey,
	bidder_pot_token : PublicKey,
	seller : PublicKey,
	resource : PublicKey,
	mint : PublicKey
	):
	print("Claiming bid")
	transaction=Transaction()
	transaction.add(
		ax.claim_bid_instruction(
			program_id=program_id,
			destination=seller,
			authority=authority.public_key,
			bidder=bidder,
			bidder_pot_token=bidder_pot_token,
			token_mint=mint,
			resource=resource
			)
		)
	resp=conn.send_transaction(transaction,authority)
	time.sleep(20)
	print("Completed.")