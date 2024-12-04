import React from "react";
import { Accordion } from "react-bootstrap";

import PropTypes from "prop-types";

import Highlight from "react-highlight";
import "highlight.js/styles/atom-one-light.css";

import { formatCode } from "../utils";

function CodeBlock(props) {
  return (
    <div className="mb-3">
      <Accordion defaultActiveKey="0">
        <Accordion.Item eventKey="0">
          <Accordion.Header>{props.title}</Accordion.Header>
          <Accordion.Body>
            <Highlight>{formatCode(props.title, props.code[0])}</Highlight>
          </Accordion.Body>
        </Accordion.Item>
      </Accordion>
    </div>
  );
}

CodeBlock.propTypes = {
  code: PropTypes.array,
  title: PropTypes.string,
};

export default CodeBlock;
