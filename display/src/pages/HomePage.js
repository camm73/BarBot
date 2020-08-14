import React from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faArrowLeft, faArrowRight} from '@fortawesome/free-solid-svg-icons';
import { getCocktailMenu } from '../api/Control';
import MenuItem from '../components/MenuItem';
import './HomePage.css';

const cocktailsPerPage = 4;

class HomePage extends React.Component{
    constructor(props){
        super(props);

        this.loadMenuInterval = undefined;
    }

    state = {
        cocktailList: [],
        cocktailLimit: cocktailsPerPage,
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
                    {this.state.cocktailList.length > 0 && (<div style={{...styles.buttonStyle}}>
                        <FontAwesomeIcon icon={faArrowLeft} size='5x' onClick={() => {
                            //TODO: Add mechanism to change pages
                            if(this.state.cocktailLimit > cocktailsPerPage){
                                this.setState({
                                    cocktailLimit: this.state.cocktailLimit - cocktailsPerPage,
                                });
                            }
                        }}/>
                    </div>)}
                    {this.state.cocktailList.length > 0 && this.state.cocktailList.map((name, index) => (index >= (this.state.cocktailLimit - cocktailsPerPage) && index < this.state.cocktailLimit) ? (
                        <MenuItem name={name} key={name}/>
                    ) : (<></>))}
                    {this.state.cocktailList.length > 0 && (<div style={{...styles.buttonStyle}}>
                        <FontAwesomeIcon icon={faArrowRight} size='5x' onClick={() => {
                            //TODO: Add ability to go to next page
                            if(this.state.cocktailLimit < this.state.cocktailList.length){
                                this.setState({
                                    cocktailLimit: this.state.cocktailLimit + cocktailsPerPage,
                                });
                            }
                        }}/>
                    </div>)}
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