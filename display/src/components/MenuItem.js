import React from 'react';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import {toUpper} from '../utils/Tools';
import {getIngredients, verifyImageExists, getThumbnail} from '../api/Cloud';
import {makeCocktail} from '../api/Control';
import LoadingComponent from '../components/LoadingComponent';
import ConfirmationComponent from '../components/ConfirmationComponent';

class MenuItem extends React.Component {

    state = {
        ingredients: {},
        loading: false,
        confirmVisible: false,
        confirmText: '',
        thumbnailLink: undefined,
        imageExists: false,
    };

    componentDidMount(){
        this.loadIngredients();
        verifyImageExists(this.props.name, this.setImageExists.bind(this));
    }

    setImageExists(status){
        //Load thumbnail
        if (status === true) {
            console.log('Found image for: ' + this.props.name);
            var link = getThumbnail(this.props.name);
            this.setState({
                thumbnailLink: link,
                imageExists: true,
            });
        } else {
            this.setState({
                imageExists: status,
            });
        }
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
            });
        }).catch(err => {
            console.log(err);
            this.setState({
                loading: false,
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
                    <Card.Img variant='top' src={this.state.imageExists ? this.state.thumbnailLink : require('../assets/defaultCocktail.jpg')} style={{width: '170px', height: '170px', alignSelf: 'center', borderRadius: '10px', marginTop: '10px'}}/>
                    <Card.Body>
                        <Card.Title style={styles.titleStyle}>{toUpper(this.props.name)}</Card.Title>
                        <div>
                            {Object.keys(this.state.ingredients).length > 0 && Object.keys(this.state.ingredients).map((name, index) => (
                                <div key={name} style={{display: 'flex', flexDirection: 'row', justifyContent: 'center', marginBottom: '-10px'}}>
                                    <p style={{marginRight: '8px', fontSize: '22px'}}>{toUpper(name)}</p>
                                    <p style={{fontSize: '22px'}}>{this.state.ingredients[name]*1.5 + ' fl oz'}</p>
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
        minWidth: '21rem',
        margin: '15px',
        textAlign: 'center',
        borderRadius: '12px',
        background: '#3E525C',
        color: 'white',
        maxHeight: '38rem',
        minHeight: '38rem',
    },

    titleStyle: {
        textDecorationLine: 'underline',
        marginBottom: '2px',
        fontSize: '26px'
    },

    buttonStyle: {
        borderRadius: '30px',
        width: '250px',
        height: '60px',
        backgroundColor: '#7295A6',
        borderWidth: '0px',
        position: 'absolute',
        bottom: '15px',
        fontSize: '24px',
        left: '13%',
    },
};