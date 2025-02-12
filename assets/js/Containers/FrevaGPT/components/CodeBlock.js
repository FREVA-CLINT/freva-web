import React from "react";
import { Card, Collapse } from "react-bootstrap";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";

import PropTypes from "prop-types";

import Highlight from "react-highlight";

import { formatCode } from "../utils";

class CodeBlock extends React.Component {

  constructor(props) {
    super(props);
    this.toggleShowCode = this.toggleShowCode.bind(this);
    this.extractElements = this.extractElements.bind(this);

    this.state = {
      showCode: false,
    }
  }

  toggleShowCode(status) {
    this.setState({showCode: !status});
  }

  extractElements(content, variant) {
    return content.filter(elem => elem.variant === variant)
  }

  render() {
    return (
      <Card className="shadow-sm card-body border-0 border-bottom mb-3 bg-light">
        <a href="#" className="m-0" onClick={() => {this.toggleShowCode(this.state.showCode)}}>
          Analyzed 
          <span>
            {this.state.showCode ? <FaAngleUp/> : <FaAngleDown/>}
          </span>
        </a>

        <Collapse in={this.state.showCode} className="mt-2">
          <Card className="shadow-sm">
            <Card.Header>python</Card.Header>

            {this.extractElements(this.props.content, "Code").map((codeElement) => {
              return(
                <Card.Body className="p-0 m-0" key={`${codeElement.content[1]}-code`}>
                  <Highlight className="python">
                    {formatCode("Code", codeElement.content[0])}
                  </Highlight>
                </Card.Body>
              )}
            )}

            {this.extractElements(this.props.content, "CodeOutput").map((codeElement, index) => {
              return(
                <Card.Footer className="p-0 m-0" key={`${codeElement.content[1]}-codeoutput-${index}`}>
                  <Highlight className="python">
                    {formatCode("CodeOutput", codeElement.content[0])}
                  </Highlight>
                </Card.Footer>
              )}
            )}
            
          </Card>
        </Collapse>
      </Card>
    );
  }
}

CodeBlock.propTypes = {
  content: PropTypes.array,
};

export default CodeBlock;
