import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import { Col, Card, Modal, Button, Alert } from "react-bootstrap";

import { isEmpty } from "lodash";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { FaExpand } from "react-icons/fa";

import { replaceLinebreaks, chatExceedsWindow } from "../utils";

import * as constants from "../constants";

import CodeBlock from "./CodeBlock";

class ChatBlock extends React.Component {
  constructor(props) {
    super(props);

    this.renderImage = this.renderImage.bind(this);
    this.renderCode = this.renderCode.bind(this);
    this.renderUser = this.renderUser.bind(this);
    this.renderError = this.renderError.bind(this);
    this.renderDefault = this.renderDefault.bind(this);
    this.enlargeImage = this.enlargeImage.bind(this);
    this.rearrangeCodeElement = this.rearrangeCodeElements.bind(this);

    this.state = {
      showModal: false,
    };
  }

  componentDidUpdate() {
    // only scroll when user input is added to conversation which is long (exceedswindowheight)
    // all other scrolling is done by the pendinganswercomponent
    if (chatExceedsWindow()) {
      if (
        this.props.chatBlock.conversation[
          this.props.chatBlock.conversation.length - 1
        ].variant === "User"
      ) {
        this.props.onScrollDown();
      }
    }
  }

  enlargeImage(imageString) {
    this.setState({
      showModal: true,
      image: `data:image/jpeg;base64,${imageString}`,
    });
  }

  rearrangeCodeElements(conversation) {
    const newConv = [];

    for (const element of conversation) {
      if (element.variant !== "Code" && element.variant !== "CodeOutput") {
        if (
          element.variant !== "ServerHint" &&
          element.variant !== "StreamEnd"
        ) {
          newConv.push([element]);
        }
      } else {
        const existingIndex = newConv.findIndex(
          (x) =>
            x[0].content.length > 1 && x[0].content[1] === element.content[1]
        );
        if (existingIndex === -1) {
          newConv.push([element]);
        } else {
          newConv[existingIndex].push(element);
        }
      }
    }

    return newConv;
  }

  renderImage(element, index) {
    return (
      // <Col
      //   key={`${index}-image`}
      //   md={constants.BOT_COLUMN_STYLE}
      //   className="border-0 border-bottom mb-3 shadow-sm card-body"
      // >
      <div className="w-75 mb-5" key={index}>
        <img
          onClick={() => this.enlargeImage(element.content)}
          src={`data:image/jpeg;base64,${element.content}`}
          className="mw-100"
        />
        <div className="d-flex justify-content-end">
          <Button
            variant="link"
            onClick={() => this.enlargeImage(element.content)}
            className="d-flex align-items-center"
          >
            <FaExpand />
          </Button>
        </div>
      </div>

      // </Col>
    );
  }

  renderCode(element, index) {
    if (isEmpty(element[0].content[0])) {
      return null;
    } else {
      return (
        <Col md={constants.BOT_COLUMN_STYLE} key={`${index}-code`}>
          <CodeBlock content={element} />
        </Col>
      );
    }
  }

  renderUser(element, index) {
    return (
      <Col md={{ span: 10, offset: 2 }} key={`${index}-user`}>
        <Card
          className="shadow-sm card-body border-0 border-bottom mb-3"
          style={{ backgroundColor: "#eee" }}
        >
          {element.content}
        </Card>
      </Col>
    );
  }

  renderError(element, index) {
    return (
      <Col md={12} key={`${index}-error`}>
        <Alert variant="danger" className="shadow-sm mb-3">
          <span className="fw-bold">{element.variant}</span>
          <ReactMarkdown>{replaceLinebreaks(element.content)}</ReactMarkdown>
        </Alert>
      </Col>
    );
  }

  renderDefault(element, index) {
    return (
      <Col md={constants.BOT_COLUMN_STYLE} key={`${index}-default`}>
        <Card className="shadow-sm card-body border-0 border-bottom mb-3 bg-light">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {replaceLinebreaks(element.content)}
          </ReactMarkdown>
        </Card>
      </Col>
    );
  }

  renderChatComponents(element, index) {
    switch (element[0].variant) {
      case "ServerHint":
      case "StreamEnd":
        return null;
      case "Image":
        return this.renderImage(element[0], index);

      case "Code":
      case "CodeOutput":
        return this.renderCode(element, index);

      case "User":
        return this.renderUser(element[0], index);

      case "ServerError":
      case "OpenAIError":
      case "CodeError":
      case "FrontendError":
      case "InvalidThread":
      case "UserStop":
        return this.renderError(element[0], index);

      default:
        return this.renderDefault(element[0], index);
    }
  }

  render() {
    const { conversation } = this.props.chatBlock;
    const rearrangedConversation = this.rearrangeCodeElements(conversation);

    return (
      <>
        <Col>
          {rearrangedConversation.map((element, index) => {
            return this.renderChatComponents(element, index);
          })}
        </Col>

        <Modal
          size="lg"
          aria-labelledby="contained-modal-title-vcenter"
          centered
          show={this.state.showModal}
          onHide={() => this.setState({ showModal: false, image: "" })}
        >
          <Modal.Header closeButton></Modal.Header>
          <Modal.Body>
            <img className="w-100" src={this.state.image} />
          </Modal.Body>
        </Modal>
      </>
    );
  }
}

ChatBlock.propTypes = {
  chatBlock: PropTypes.shape({
    thread: PropTypes.string,
    conversation: PropTypes.array,
  }),
  onScrollDown: PropTypes.func,
};

const mapStateToProps = (state) => ({
  chatBlock: state.frevaGPTReducer,
});

export default connect(mapStateToProps)(ChatBlock);
