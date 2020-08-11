import React from 'react';
import Button from 'react-bootstrap/Button';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faArrowLeft, faArrowRight} from '@fortawesome/free-solid-svg-icons';
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
        cocktailLimit: 3,
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
                    <div style={{...styles.buttonStyle, marginRight: '10px'}}>
                        <FontAwesomeIcon icon={faArrowLeft} size='4x' onClick={() => {
                            //TODO: Add mechanism to change pages
                            if(this.state.cocktailLimit > 3){
                                this.setState({
                                    cocktailLimit: this.state.cocktailLimit - 3,
                                });
                            }
                        }}/>
                    </div>
                    {this.state.cocktailList.length > 0 && this.state.cocktailList.map((name, index) => (index >= this.state.cocktailLimit-3 && index < this.state.cocktailLimit) ? (
                        <MenuItem name={name} key={name}/>
                    ) : (<></>))}
                    <div style={{...styles.buttonStyle, marginLeft: '10px'}}>
                        <FontAwesomeIcon icon={faArrowRight} size='4x' onClick={() => {
                            //TODO: Add ability to go to next page
                            if(this.state.cocktailLimit < this.state.cocktailList.length){
                                this.setState({
                                    cocktailLimit: this.state.cocktailLimit + 3,
                                });
                            }
                        }}/>
                    </div>
                </div>
            </div>
        );
    }
}

export default HomePage;

const styles = {
    buttonStyle: {
        maxHeight: '60px',
        justifyContent: 'center',
        alignSelf: 'center',
    },
};