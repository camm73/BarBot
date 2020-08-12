import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

class ConfirmationComponent extends React.Component {

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
                        <p>{this.props.bodyText}</p>
                    </div>
                </Modal.Body>
                <Modal.Footer style={{justifyContent: 'space-between'}}>
                    <Button variant='secondary' onClick={() => {
                        this.props.confirmCallback(false);
                    }}>Go Back</Button>
                    <Button variant='primary' onClick={() => {
                        this.props.confirmCallback(true);
                    }}>Continue</Button>
                </Modal.Footer>
            </Modal>
        );
    }
}

export default ConfirmationComponent;