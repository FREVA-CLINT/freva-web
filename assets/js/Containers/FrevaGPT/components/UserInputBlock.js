import React from "react";

import { Col, Card, Button, FormControl } from "react-bootstrap";

import { FaEdit } from "react-icons/fa";

import PropTypes from "prop-types";

class UserInputBlock extends React.Component {
  constructor(props) {
    super(props);

    this.showEditBar = this.showEditBar.bind(this);
    this.hideEditBar = this.hideEditBar.bind(this);
    this.renderUserInputCard = this.renderUserInputCard.bind(this);
    this.renderUserInputField = this.renderUserInputField.bind(this);
    this.resizeInputField = this.resizeInputField.bind(this);

    this.state = {
      showEditBar: false,
      renderInput: false,
    };
  }

  showEditBar() {
    this.setState({ showEditBar: true });
  }

  hideEditBar() {
    setTimeout(() => {
      this.setState({ showEditBar: false });
    }, 500);
  }

  resizeInputField(id) {
    const inputField = document.getElementById(id);
    const style = inputField.style;

    style.height = inputField.style.minHeight = "auto";
    style.minHeight = `${Math.min(inputField.scrollHeight, parseInt(inputField.style.maxHeight))}px`;
    style.height = `${inputField.scrollHeight}px`;
  }

  renderUserInputCard() {
    return (
      <Col
        md={{ span: 10, offset: 2 }}
        key={`${this.props.index}-user`}
        onMouseEnter={this.showEditBar}
        onMouseLeave={this.hideEditBar}
      >
        <Card
          className="shadow-sm card-body border-0 border-bottom"
          style={{ backgroundColor: "#eee" }}
        >
          {this.props.content.content}
        </Card>
        <div className="w-100 d-flex justify-content-end p-0 h-5">
          <Button
            variant="link"
            className="d-flex align-items-center"
            onClick={() => this.setState({ renderInput: true })}
          >
            {this.state.showEditBar ? (
              <FaEdit />
            ) : (
              <FaEdit className="opacity-0" />
            )}
          </Button>
        </div>
      </Col>
    );
  }

  renderUserInputField() {
    return (
      <Col
        md={{ span: 10, offset: 2 }}
        key={`${this.props.index}-user`}
        onMouseEnter={this.showEditBar}
        onMouseLeave={this.hideEditBar}
      >
        <Card
          className="shadow-sm card-body border-0 border-bottom"
          style={{ backgroundColor: "#eee" }}
        >
          <FormControl
            as="textarea"
            id={`UserInputField-${this.props.index}`}
            className="mb-2"
            defaultValue={this.props.content.content}
            onChange={() => {
              this.resizeInputField(`UserInputField-${this.props.index}`);
            }}
          />
          <div className="w-100 d-flex justify-content-end">
            <Button
              variant="secondary"
              onClick={() =>
                this.setState({ renderInput: false, showEditBar: false })
              }
            >
              Cancel
            </Button>
            <Button variant="info">Send</Button>
          </div>
        </Card>
        <div className="w-100 d-flex justify-content-end p-0">
          <Button
            variant="link"
            className="d-flex align-items-center"
            onClick={() => this.setState({ renderInput: true })}
          >
            <FaEdit className="opacity-0" />
          </Button>
        </div>
      </Col>
    );
  }

  render() {
    return (
      <>
        {this.state.renderInput
          ? this.renderUserInputField()
          : this.renderUserInputCard()}
      </>
    );
  }
}

UserInputBlock.propTypes = {
  content: PropTypes.object,
  index: PropTypes.number,
};

export default UserInputBlock;
