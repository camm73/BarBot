import React from 'react';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import {toUpper} from '../utils/Tools';
import {getIngredients} from '../api/Cloud';

class MenuItem extends React.Component {

    state = {
        ingredients: {}
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
            <Card style={styles.containerStyle}>
                <Card.Img variant='top' src={require('../assets/defaultCocktail.jpg')} style={{width: '140px', height: '140px', alignSelf: 'center', borderRadius: '8px', marginTop: '10px'}}/>
                <Card.Body>
                    <Card.Title style={styles.titleStyle}>{toUpper(this.props.name)}</Card.Title>
                    {Object.keys(this.state.ingredients).length > 0 && Object.keys(this.state.ingredients).map((name, index) => (
                        <div key={name} style={{display: 'flex', flexDirection: 'row', justifyContent: 'center', marginBottom: '-10px'}}>
                            <p style={{marginRight: '8px'}}>{toUpper(name)}</p>
                            <p>{this.state.ingredients[name]*1.5 + ' fl oz'}</p>
                        </div>
                    ))}
                    <Button style={styles.buttonStyle}>Make Cocktail</Button>
                </Card.Body>
            </Card>
        );
    }
}

export default MenuItem;

const styles = {
    containerStyle: {
        minWidth: '15rem',
        margin: '15px',
        textAlign: 'center',
        borderRadius: '12px',
        background: '#3E525C',
        color: 'white'
    },

    titleStyle: {
        textDecorationLine: 'underline',
        marginBottom: '2px',
    },

    buttonStyle: {
        borderRadius: '20px',
        width: '175px',
        backgroundColor: '#7295A6',
        borderWidth: '0px'
    }
};