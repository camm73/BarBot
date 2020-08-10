import React from 'react';
import { getCocktailMenu } from '../api/Control';
import MenuItem from '../components/MenuItem';
import './HomePage.css';

class HomePage extends React.Component{
    constructor(props){
        super(props);

        this.loadMenuInterval = undefined;
    }

    state = {
        cocktailList: [],

    };

    componentDidMount(){
        this.loadCocktailMenu();
        
        this.loadMenuInterval = setInterval(this.loadCocktailMenu.bind(this), 30000);
    }

    componentWillUnmount(){
        if(this.loadMenuInterval !== undefined){
            clearInterval(this.loadMenuInterval);
        }
    }

    loadCocktailMenu(){
        getCocktailMenu().then(res => {
            this.setState({
                cocktailList: res,
            });
        }).catch((err) => {
            console.log(err);
        });
    }

    render(){
        return(
            <div className='HomePage'>
                <h1 className='HeaderText' onClick={() => {this.loadCocktailMenu()}}>BarBot</h1>
                {this.state.cocktailList.length === 0 && (
                    <div className='NotAvailableContainer'>
                        <h3 className='NotAvailable'>No cocktails are available right now.</h3>
                        <h3 className='NotAvailable'>Please check back later.</h3>
                    </div>
                )}
                <div className='CardContainer'>
                    {this.state.cocktailList.length > 0 && this.state.cocktailList.map((name, index) => (
                        <MenuItem name={name} key={name}/>
                    ))}
                </div>
            </div>
        );
    }
}

export default HomePage;