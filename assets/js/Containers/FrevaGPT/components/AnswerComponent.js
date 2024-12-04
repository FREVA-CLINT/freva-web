import React from "react";
import PropTypes from "prop-types";

import { Col, Card, Spinner } from "react-bootstrap";

import Markdown from "react-markdown";

function AnswerComponent(props) {
  function renderAnswer(props) {
    switch (props.variant) {
      case "Assistant":
        return (
          <Col md={{ span: 10, offset: 0 }}>
            <Card className="shadow-sm card-body border-0 border-bottom mb-3 bg-light">
              <Markdown>{props.content}</Markdown>
            </Card>
          </Col>
        );
      case "Code":
      case "CodeBlock":
        return (
          <Col md={{ offset: 0 }}>
            <Card className="shadow-sm card-body border-0 border-bottom mb-3 bg-light">
              <span>
                <Spinner size="sm" />
                Analyzing code...
              </span>
            </Card>
          </Col>
        );
      default:
        return null;
    }
  }

  return <Col>{renderAnswer(props)}</Col>;
}

AnswerComponent.propTypes = {
  content: PropTypes.string,
  variant: PropTypes.string,
};

export default AnswerComponent;
