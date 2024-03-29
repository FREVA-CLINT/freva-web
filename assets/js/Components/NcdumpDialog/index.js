import React from "react";
import PropTypes from "prop-types";
import { Modal, Button, FormControl, Alert } from "react-bootstrap";

import Spinner from "../Spinner";

export const NcDumpDialogState = {
  ENTER_PASSWORD: "pw",
  ERROR: "error",
  READY: "ready",
  LOADING: "loading",
};

class NcdumpDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = { pw: "" };

    this.handleChange = this.handleChange.bind(this);
    this.submitNcdump = this.submitNcdump.bind(this);
  }

  submitForm(e) {
    e.preventDefault();
    this.submitNcdump();
  }

  submitNcdump() {
    const { pw } = this.state;
    this.props.submitNcdump(this.props.file, pw);
  }

  handleChange(e) {
    const val = e.target.value;
    this.setState({ pw: val });
  }

  render() {
    const { show, onClose, status, output, file, error } = this.props;
    return (
      <Modal
        show={show}
        size="lg"
        dialogClassName="ncdump-modal"
        onHide={() => onClose()}
      >
        <Modal.Header closeButton>
          <Modal.Title className="fs-5">Metadata for {file}</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          {(status === NcDumpDialogState.ENTER_PASSWORD ||
            status === NcDumpDialogState.ERROR) && (
            <span>
              {status === NcDumpDialogState.ERROR && (
                <Alert variant="danger">{error}</Alert>
              )}
              <p>To inspect metadata you have to re-enter your password</p>
              <form onSubmit={this.submitNcdump} id="passForm" name="passForm">
                <FormControl
                  id="search"
                  type="password"
                  name="password"
                  onChange={this.handleChange}
                  value={this.state.pw}
                />
              </form>
            </span>
          )}
          {status === NcDumpDialogState.LOADING ? <Spinner /> : null}
          {output && (
            <div>
              <pre
                className="d-flex justify-content-center"
                dangerouslySetInnerHTML={{ __html: output }}
              />
            </div>
          )}
        </Modal.Body>

        <Modal.Footer>
          <Button variant="primary" onClick={() => this.submitNcdump()}>
            Inspect metadata
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }
}

NcdumpDialog.propTypes = {
  show: PropTypes.bool,
  submitNcdump: PropTypes.func.isRequired,
  onClose: PropTypes.func,
  status: PropTypes.string,
  output: PropTypes.string,
  error: PropTypes.string,
  file: PropTypes.string,
};

export default NcdumpDialog;
