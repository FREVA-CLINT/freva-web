import React from 'react';
import ReactDOM from 'react-dom';
import {Modal, Button, FormControl, Alert} from 'react-bootstrap';
import CircularProgress from 'material-ui/CircularProgress';


class NcdumpDialog extends React.Component {

    constructor(props) {
        super(props);
        this.state = {pw: ''};

        this.handleChange = this.handleChange.bind(this);
    }

    submitNcdump() {
        const {pw} = this.state;
        this.props.submitNcdump(this.props.file, pw);
    }

    handleChange(e) {
        const val = ReactDOM.findDOMNode(this.refs.ncdumpPW).value;
        this.setState({pw: val});
    }

    render() {
        const {show, onClose, status, output, file} = this.props;
        return (
            <Modal show={show} bsSize="large" dialogClassName="ncdump-modal"
                   onShow={() => {if (this.state.pw !== '') this.submitNcdump()}}
                   onHide={() => onClose()}>
                <Modal.Header closeButton>
                    <Modal.Title>{status === 'ready' ? `ncdump -h ${file}` : 'Enter your password'}</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                    <span style={status === 'pw' || status === 'pw_fail' ? {} : {display: 'none'}}>
                        {status === 'pw_fail' ? <Alert bsStyle="danger"><strong>Wrong password!</strong> Please try again.</Alert> : null}
                        <p>To start Ncdump you have to re-enter your password</p>
                        <form method="post" id="passForm" name="passForm">
                            <FormControl id={`username`} type="text" ref={`username`} name="password" style={{display: 'none'}}/>
                            <FormControl id={`search`} type="password" ref={`ncdumpPW`} name="password"
                                         onChange={this.handleChange} value={this.state.pw}/>
                        </form>
                    </span>
                    {status === 'loading' ?
                    <div style={{textAlign: 'center'}}>
                        <CircularProgress />
                    </div> : null}

                    {output ?
                        <div>
                            {output.error_msg ? <pre>{output.error_msg}</pre> : <pre>{output.ncdump}</pre>}
                        </div>  :  null}

                </Modal.Body>

                <Modal.Footer>
                    <Button bsStyle="primary" onClick={() => this.submitNcdump()}>Start Ncdump</Button>
                </Modal.Footer>

            </Modal>
        )
    }
}

export default NcdumpDialog;