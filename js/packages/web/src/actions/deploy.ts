import {getPayer} from './utils'
import {
	Connection,
	PublicKey,
	Keypair,
	BpfLoader,
	BPF_LOADER_PROGRAM_ID,
	clusterApiUrl
} from '@solana/web3.js'
import fs from 'mz/fs'

export async function getLamport(){
	const payer = await getPayer()
	const devnet = clusterApiUrl('devnet')
	const conn=new Connection(devnet,'confirmed')
	await conn.requestAirdrop(payer.publicKey, 3000000000)
	console.log(await conn.getBalance(payer.publicKey))
}

export async function deploy(filepath : string){
	console.log("Let's go!")
	const payer = await getPayer()
	console.log({payer:{publicKey:payer.publicKey.toBase58()}})
	const devnet = clusterApiUrl('devnet')
	const conn=new Connection(devnet,'confirmed')

	if(await conn.getBalance(payer.publicKey) < 9000000000){
		console.log("Low lamports. You first get sols.")
		return
	}

	console.log("Create Program Account")
	const programAccount = new Keypair()
	const programId=programAccount.publicKey
	console.log({program:{programId:programId.toBase58()}})

	const program = await fs.readFile(filepath)
	console.log({program})
	await BpfLoader.load(conn,payer,programAccount,program,BPF_LOADER_PROGRAM_ID)
}

export class deployEngine {
	conn : Connection;
	payer : Keypair;
	constructor(){
		const devnet = clusterApiUrl('devnet')
		this.conn=new Connection(devnet,'confirmed')
		this.payer=new Keypair()
		console.log(this.payer)
	}

	async getLamports(){
		await this.conn.requestAirdrop(this.payer.publicKey, 3000000000)
		console.log(await this.conn.getBalance(this.payer.publicKey))
	}

	async deploy(filepath:string){
		if(await this.conn.getBalance(this.payer.publicKey) < 9000000000){
			console.log("Low lamports. You first get sols.")
			return
		}

		console.log("Create Program Account")
		const programAccount = new Keypair()
		const programId=programAccount.publicKey
		console.log({program:{programId:programId.toBase58()}})

		const program = await fs.readFile(filepath)
		console.log({program})
		await BpfLoader.load(this.conn,this.payer,programAccount,program,BPF_LOADER_PROGRAM_ID)
	}
}