import React,{Component} from 'react'
import {deployEngine} from '../actions/deploy'

const d = new deployEngine()

export default class DeployPage extends Component<any,any> {
	constructor(props : any) {
		super(props);
		this.state={
			filepath : ""
		}
	}
	changeInputValue = (e:any)=>{
		this.setState({filepath:e.target.value})
	}
	deploy = async () => {
		await d.deploy(this.state.filepath)
	}
	getLamports = async () =>{
		await d.getLamports()
	}
	render = () => {
		return <div className="container-fluid mt-4">
			<input type="file" className="form-control-file border" value={this.state.filepath}
				onChange={this.changeInputValue} />
			<button type="button" className="btn btn-success" onClick={this.deploy}>Deploy</button>
			<button type="button" className="btn btn-danger" onClick={this.getLamports}>Lamports</button>
		</div>
	}
}