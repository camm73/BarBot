import React from 'react';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import {toUpper} from '../utils/Tools';
import {getIngredients} from '../api/Cloud';
import {makeCocktail} from '../api/Control';
import LoadingComponent from '../components/LoadingComponent';
import ConfirmationComponent from '../components/ConfirmationComponent';

class MenuItem extends React.Component {

    state = {
        ingredients: {},
        loading: false,
        confirmVisible: false,
        confirmText: '',
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

    processCocktail(){
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
        }).catch(err => {
            console.log(err);
            this.setState({
                loading: false,
            }, () => {
                alert('There was an error making your cocktail!');
            });
        })
    }

    confirmCallback(confirm) {
        if(confirm){
            this.setState({
                confirmVisible: false,
            });
            this.processCocktail();
        }else{
            this.setState({
                confirmVisible: false,
            });
        }
    }

    render(){
        return(
            <div>
                <LoadingComponent titleText='Making Cocktail' bodyText='Please wait while BarBot makes your cocktail...' visible={this.state.loading}/>
                <ConfirmationComponent titleText='Make Cocktail?' bodyText={this.state.confirmText} visible={this.state.confirmVisible} confirmCallback={this.confirmCallback.bind(this)}/>
                <Card style={styles.containerStyle}>
                    <Card.Img variant='top' src={require('../assets/defaultCocktail.jpg')} style={{width: '140px', height: '140px', alignSelf: 'center', borderRadius: '8px', marginTop: '10px'}}/>
                    <Card.Body>
                        <Card.Title style={styles.titleStyle}>{toUpper(this.props.name)}</Card.Title>
                        <div>
                            {Object.keys(this.state.ingredients).length > 0 && Object.keys(this.state.ingredients).map((name, index) => (
                                <div key={name} style={{display: 'flex', flexDirection: 'row', justifyContent: 'center', marginBottom: '-10px'}}>
                                    <p style={{marginRight: '8px', fontSize: '19px'}}>{toUpper(name)}</p>
                                    <p style={{fontSize: '19px'}}>{this.state.ingredients[name]*1.5 + ' fl oz'}</p>
                                </div>
                            ))}
                        </div>
                        <Button style={styles.buttonStyle} onClick={() => {
                            this.setState({
                                confirmText: 'Place your cup underneath BarBot. Press "Continue" when you\'re ready to make your ' + toUpper(this.props.name) + '.',
                                confirmVisible: true,
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
        minWidth: '17rem',
        margin: '15px',
        textAlign: 'center',
        borderRadius: '12px',
        background: '#3E525C',
        color: 'white',
        maxHeight: '32rem',
        minHeight: '32rem',
    },

    titleStyle: {
        textDecorationLine: 'underline',
        marginBottom: '2px',
        fontSize: '22px'
    },

    buttonStyle: {
        borderRadius: '25px',
        width: '200px',
        height: '50px',
        backgroundColor: '#7295A6',
        borderWidth: '0px',
        position: 'absolute',
        bottom: '12px',
        fontSize: '20px',
        left: '14%',
    },
};