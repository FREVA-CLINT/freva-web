import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import { Col, Card } from "react-bootstrap";

import { isEmpty } from "lodash";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { replaceLinebreaks } from "../utils";

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
  }

  renderImage(element) {
    return (
      <Col key={element.content} md={constants.BOT_COLUMN_STYLE}>
        <img
          className="w-100"
          src={`data:image/jpeg;base64,${element.content}`}
        />
      </Col>
    );
  }

  renderCode(element) {
    if (isEmpty(element.content[0])) return null;
    else
      return (
        <Col md={constants.BOT_COLUMN_STYLE} key={element.content}>
          <CodeBlock title={element.variant} code={element.content} />
        </Col>
      );
  }

  renderUser(element) {
    return (
      <Col md={{ span: 10, offset: 2 }} key={element.content}>
        <Card
          className="shadow-sm card-body border-0 border-bottom mb-3"
          style={{ backgroundColor: "#eee" }}
        >
          {element.content}
        </Card>
      </Col>
    );
  }

  renderError(element) {
    return (
      <Col md={constants.BOT_COLUMN_STYLE} key={element.content}>
        <Card className="shadow-sm card-body border-0 border-bottom mb-3 bg-danger">
          <span className="fw-bold">{element.variant}</span>
          <ReactMarkdown>{replaceLinebreaks(element.content)}</ReactMarkdown>
        </Card>
      </Col>
    );
  }

  renderDefault(element) {
    return (
      <Col md={constants.BOT_COLUMN_STYLE} key={element.content}>
        <Card className="shadow-sm card-body border-0 border-bottom mb-3 bg-light">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {replaceLinebreaks(element.content)}
          </ReactMarkdown>
        </Card>
      </Col>
    );
  }

  renderChatComponents(element) {
    switch (element.variant) {
      case "ServerHint":
      case "StreamEnd":
        return null;
      case "Image":
        return this.renderImage(element);

      case "Code":
      case "CodeOutput":
        return this.renderCode(element);

      case "User":
        return this.renderUser(element);

      case "ServerError":
      case "OpenAIError":
      case "CodeError":
      case "FrontendError":
      case "UserStop":
        return this.renderError(element);

      default:
        return this.renderDefault(element);
    }
  }

  render() {
    const { conversation } = this.props.chatBlock;

    return (
      <Col>
        {conversation.map((element) => {
          return this.renderChatComponents(element);
        })}
      </Col>
    );
  }
}

ChatBlock.propTypes = {
  chatBlock: PropTypes.shape({
    thread: PropTypes.string,
    conversation: PropTypes.array,
  }),
};

const mapStateToProps = (state) => ({
  chatBlock: state.frevaGPTReducer,
});

export default connect(mapStateToProps)(ChatBlock);
