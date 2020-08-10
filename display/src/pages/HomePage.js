import React from 'react';
import './HomePage.css';

class HomePage extends React.Component{
    constructor(props){
        super(props);
    }

    state = {
        cocktailList: [],
    };

    render(){
        return(
            <div className='HomePage'>
                <h1 className='HeaderText'>BarBot</h1>
                {this.state.cocktailList.length === 0 && (
                    <div>
                        <h3 className='NotAvailable'>No cocktails are available right now.</h3>
                    </div>
                )}
            </div>
        );
    }
}

export default HomePage;