import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Spinner from 'react-bootstrap/Spinner';

class LoadingComponent extends React.Component{
    
    render(){
        return(
            <Modal size='md' 
                aria-labelledby="contained-modal-title-vcenter"
                centered
                show={this.props.visible}
                >
                <Modal.Header style={{display: 'flex', justifyContent: 'center'}}>
                    <Modal.Title id="contained-modal-title-vcenter">{this.props.titleText}</Modal.Title>   
                </Modal.Header>
                <Modal.Body>
                    <div style={{display: 'flex', flexDirection: 'column', textAlign: 'center'}}>
                        <Spinner animation='border' style={{alignSelf: 'center', marginBottom: '10px'}}/>
                        <p>{this.props.bodyText}</p>
                    </div>
                </Modal.Body>
            </Modal>
        );
    }

}

export default LoadingComponent;