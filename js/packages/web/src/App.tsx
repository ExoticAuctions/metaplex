import React,{Component} from 'react';
import './bootstrap.min.css';
//import RoomSelect from './RoomSelect'
// import DeployPage from './pages/deploy'
import AuctionPage from './pages/auction'
export default class App extends Component{
  render = () => {
    return <div>
      <AuctionPage/>
    </div>
  }
}
