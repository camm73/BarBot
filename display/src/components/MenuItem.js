import React from 'react';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import {toUpper} from '../utils/Tools';
import {getIngredients} from '../api/Cloud';
import {makeCocktail} from '../api/Control';
import LoadingComponent from '../components/LoadingComponent';

class MenuItem extends React.Component {

    state = {
        ingredients: {},
        loading: false,
    };

    componentDidMount(){
        this.loadIngredients();
    }

    loadIngredients(){
        if(this.props.name !== undefined && this.props.name !== ''){
            getIngredients(this.props.name).then(res => {
                this.setState({
                    ingredients: res,
                });
            });
        }
    }

    render(){
        return(
            <div>
                <LoadingComponent titleText='Making Cocktail' bodyText='Please wait while BarBot makes your cocktail...' visible={this.state.loading}/>
                <Card style={styles.containerStyle}>
                    <Card.Img variant='top' src={require('../assets/defaultCocktail.jpg')} style={{width: '140px', height: '140px', alignSelf: 'center', borderRadius: '8px', marginTop: '10px'}}/>
                    <Card.Body>
                        <Card.Title style={styles.titleStyle}>{toUpper(this.props.name)}</Card.Title>
                        <div>
                            {Object.keys(this.state.ingredients).length > 0 && Object.keys(this.state.ingredients).map((name, index) => (
                                <div key={name} style={{display: 'flex', flexDirection: 'row', justifyContent: 'center', marginBottom: '-10px'}}>
                                    <p style={{marginRight: '8px'}}>{toUpper(name)}</p>
                                    <p>{this.state.ingredients[name]*1.5 + ' fl oz'}</p>
                                </div>
                            ))}
                        </div>
                        <Button style={styles.buttonStyle} onClick={() => {
                            this.setState({
                                loading: true,
                            });
                            makeCocktail(this.props.name).then((res) => {
                                this.setState({
                                    loading: false,
                                }, () => {
                                    if(res === false){
                                        alert('There was an error making your cocktail!');
                                    }
                                });
                            });
                        }}>Make Cocktail</Button>
                    </Card.Body>
                </Card>
            </div>
        );
    }
}

export default MenuItem;

const styles = {
    containerStyle: {
        display: 'table',
        minWidth: '15.5rem',
        margin: '15px',
        textAlign: 'center',
        borderRadius: '12px',
        background: '#3E525C',
        color: 'white',
        maxHeight: '25rem',
        minHeight: '25rem',
    },

    titleStyle: {
        textDecorationLine: 'underline',
        marginBottom: '2px',
    },

    buttonStyle: {
        borderRadius: '20px',
        width: '175px',
        backgroundColor: '#7295A6',
        borderWidth: '0px',
        position: 'absolute',
        bottom: '12px',
        left: '15%',
    },
};