import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import {
  Container,
  Row,
  Col,
  FormControl,
  InputGroup,
  Button,
  Form,
  Alert,
  Tooltip,
  OverlayTrigger,
} from "react-bootstrap";

import { browserHistory } from "react-router";
import { isEmpty } from "lodash";

import { FaStop, FaPlay } from "react-icons/fa";

import queryString from 'query-string';

import Spinner from "../../Components/Spinner";

import ChatBlock from "./components/ChatBlock";
import SidePanel from "./components/SidePanel";
import PendingAnswerComponent from "./components/PendingAnswerComponent";

import { truncate } from "./utils";

import { setThread, setConversation, addElement } from "./actions";

import { botSuggestions } from "./exampleRequests";

class FrevaGPT extends React.Component {
  // const abortController = useRef();
  // abortController.current = new AbortController();
  // const signal = abortController.signal;

  constructor(props) {
    super(props);
    this.handleUserInput = this.handleUserInput.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.createNewChat = this.createNewChat.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.toggleBotSelect = this.toggleBotSelect.bind(this);
    this.handleStop = this.handleStop.bind(this);
    this.submitUserInput = this.submitUserInput.bind(this);

    this.state = {
      loading: false,
      userInput: "",
      botModelList: [],
      botModel: "",
      hideBotModelList: true,
      botOkay: undefined,
      showSuggestions: true,
      dynamicAnswer: "",
      dynamicVariant: "",
    };
  }

  async componentDidMount() {
    // if thread giving on mounting the component, set thread within store
    const givenQueryParams = browserHistory.getCurrentLocation().query;
    if (
      Object.hasOwn(givenQueryParams, "thread_id") &&
      !isEmpty(givenQueryParams.thread_id)
    ) {
      this.props.dispatch(setThread(givenQueryParams.thread_id));

      // request content of old thread if threa_id is given
      this.setState({ loading: true });
      await this.getOldThread(givenQueryParams.thread_id);
      this.setState({ loading: false, showSuggestions: false });
    }

    const successfulPing = async () => {
      let pingSuccessful = false;

      try {
        const response = await fetch("/api/chatbot/ping");
        if (response.status === 200) {
          pingSuccessful = true;
        }
      } catch (err) {
        pingSuccessful = false;
      }

      return pingSuccessful;
    };

    const getBotModels = async () => {
      const response = await fetch(
        `/api/chatbot/availablechatbots?`
      );
      this.setState({ botModelList: await response.json() });
    };

    if (await successfulPing()) {
      this.setState({ botOkay: true });
      await getBotModels();
    } else {
      this.setState({ botOkay: false });
    }
  }

  createNewChat() {
    this.props.dispatch(setConversation([]));
    this.props.dispatch(setThread(""));
    browserHistory.push({
      pathname: "/chatbot/",
      search: "",
    });
    this.setState({ showSuggestions: true });
    window.scrollTo(0, 0);
  }

  handleUserInput(e) {
    this.setState({ userInput: e.target.value });
  }

  async handleKeyDown(e) {
    if (e.key === "Enter" && !isEmpty(e.target.value)) {
      this.handleSubmit(e.target.value);
    }
  }

  async submitUserInput() {
    const userInput = this.state.userInput;

    if (!isEmpty(userInput)) {
      await this.handleSubmit(userInput);
    }

    this.setState({ userInput: "" });
  }

  async handleSubmit(input) {
    this.props.dispatch(addElement({ variant: "User", content: input }));
    this.setState({ showSuggestions: false, userInput: "", loading: true });

    try {
      await this.fetchData(input);
    } catch (err) {
      this.props.dispatch(
        addElement({
          variant: "FrontendError",
          content: "An error occured during rendering!",
        })
      );
      // eslint-disable-next-line no-console
      console.error(err);
    }
    this.setState({ loading: false });
  }

  async fetchData(input) {
    const queryObject = {
      input,
      thread_id: this.props.frevaGPT.thread,
      chatbot: this.state.botModel,
    };

    // response of a new bot request is streamed
    const response = await fetch(
      `/api/chatbot/streamresponse?` + queryString.stringify(queryObject)
    ); //, signal);

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let buffer = "";
    let varObj = {};

    // eslint-disable-next-line no-constant-condition
    while (true) {
      // eslint-disable-next-line no-await-in-loop
      const { done, value } = await reader.read();
      if (done) {
        break;
      }

      const decodedValues = decoder.decode(value);
      buffer = buffer + decodedValues;

      let foundSomething = true;

      while (foundSomething) {
        foundSomething = false;

        for (let bufferIndex = 0; bufferIndex < buffer.length; bufferIndex++) {
          if (buffer[bufferIndex] !== "}") {
            continue;
          }
          const subBuffer = buffer.slice(0, bufferIndex + 1);

          try {
            const jsonBuffer = JSON.parse(subBuffer);
            buffer = buffer.slice(bufferIndex + 1); // shorten string by already evaluated string

            // object is not empty so compare variants
            if (Object.keys(varObj).length !== 0) {
              // if object has not same variant, add answer to conversation and override object
              if (varObj.variant !== jsonBuffer.variant) {
                this.props.dispatch(addElement(varObj));
                this.setState({ dynamicAnswer: "", dynamicVariant: "" });
                varObj = jsonBuffer;
              } else {
                // if object has same variant, add content
                // eslint-disable-next-line no-lonely-if
                if (
                  varObj.variant === "Code" ||
                  varObj.variant === "CodeOutput"
                ) {
                  varObj.content[0] = varObj.content[0] + jsonBuffer.content[0];
                  this.setState({
                    dynamicAnswer: varObj.content[0],
                    dynamicVariant: varObj.variant,
                  });
                } else {
                  varObj.content = varObj.content + jsonBuffer.content;
                  this.setState({
                    dynamicAnswer: varObj.content,
                    dynamicVariant: varObj.variant,
                  });
                }
              }
            } else {
              // object is empty so add content
              varObj = jsonBuffer;

              // set thread id
              if (
                this.props.frevaGPT.thread === "" &&
                varObj.variant === "ServerHint"
              ) {
                try {
                  this.props.dispatch(
                    setThread(JSON.parse(varObj.content).thread_id)
                  );
                  browserHistory.push({
                    pathname: "/chatbot/",
                    search: `?thread_id=${this.props.frevaGPT.thread}`,
                  });
                } catch (err) {
                  // handle warning
                }
              }
            }

            foundSomething = true;
            break;
          } catch (err) {
            // ServerHints and CodeBlocks include nested JSON Objects
            // eslint-disable-next-line no-console
            if (
              !subBuffer.includes("ServerHint") &&
              !subBuffer.includes("Code")
            ) {
              this.props.dispatch(
                addElement({
                  variant: "FrontendError",
                  content: "Incomplete message received.",
                })
              );
            }
          }
        }
      }
    }
  }

  async getOldThread(thread) {

    const queryObject = { "thread_id": thread };
    const response = await fetch(
      `/api/chatbot/getthread?` + queryString.stringify(queryObject)
    );

    const variantArray = await response.json();
    this.props.dispatch(setConversation(variantArray));
  }

  async handleStop() {
    // stop of thread only possible if a thread id is given

    const queryObject = { thread_id: this.props.frevaGPT.thread }
    if (this.props.frevaGPT.thread) {
      await fetch(
        `/api/chatbot/stop?` + queryString.stringify(queryObject)
      );
    }

    // abort fetch request anyway (especially if no thread is given)
    // if (abortController.current) abortController.current.abort();

    this.setState({ loading: false });
    this.props.dispatch(
      addElement({ variant: "UserStop", content: "Request stopped manually" })
    );
  }

  toggleBotSelect() {
    this.setState({ hideBotModelList: !this.state.hideBotModelList });
  }

  renderAlert() {
    return (
      <Alert key="botError" variant="danger">
        The bot is currently not available. Please retry later.
      </Alert>
    );
  }

  renderBotContent() {
    return (
      <>
        <Col md={4}>
          <SidePanel />
        </Col>

        <Col md={8}>
          {this.state.showSuggestions ? (
            <Row className="mb-2 g-2">
              {botSuggestions.map((element) => {
                return (
                  <div key={element} className="col-md-3">
                    <OverlayTrigger
                      key={element}
                      overlay={<Tooltip>{element}</Tooltip>}
                    >
                      <Button
                        className="h-100 w-100"
                        variant="outline-secondary"
                        onClick={() => this.handleSubmit(element)}
                      >
                        {truncate(element)}
                      </Button>
                    </OverlayTrigger>
                  </div>
                );
              })}
            </Row>
          ) : null}

          <ChatBlock />

          <PendingAnswerComponent
            content={this.state.dynamicAnswer}
            variant={this.state.dynamicVariant}
          />

          {this.state.loading && !this.state.dynamicAnswer ? (
            <Row className="mb-3">
              <Col md={1}>
                <Spinner />
              </Col>
            </Row>
          ) : null}

          <Row>
            <Col md={12}>
              <InputGroup className="mb-2 pb-2">
                <FormControl
                  type="text"
                  value={this.state.userInput}
                  onChange={this.handleUserInput}
                  onKeyDown={this.handleKeyDown}
                  placeholder="Ask a question"
                />
                {this.state.loading ? (
                  <Button variant="outline-danger" onClick={this.handleStop}>
                    <FaStop />
                  </Button>
                ) : (
                  <Button
                    variant="outline-success"
                    onClick={this.submitUserInput}
                  >
                    <FaPlay />
                  </Button>
                )}
              </InputGroup>
            </Col>
          </Row>
        </Col>
      </>
    );
  }

  renderBotHeader() {
    return (
      <div className="d-flex justify-content-between mb-2">
        <Form.Select
          value={this.botModel}
          onChange={(e) => {
            this.setState({ botModel: e.target.value });
          }}
          className="me-1"
          placeholder="Model"
          hidden={this.state.hideBotModelList}
        >
          {this.state.botModelList.map((x) => {
            return <option key={x}>{x}</option>;
          })}
        </Form.Select>
        <Button onClick={this.createNewChat} variant="info">
          NewChat
        </Button>
      </div>
    );
  }

  render() {
    return (
      <Container>
        <Row>
          <div className="d-flex justify-content-between">
            <h2 onClick={this.toggleBotSelect}>FrevaGPT</h2>

            {this.state.botOkay ? this.renderBotHeader() : null}
          </div>

          {this.state.botOkay === undefined ? (
            <Spinner />
          ) : this.state.botOkay ? (
            this.renderBotContent()
          ) : (
            this.renderAlert()
          )}
        </Row>
      </Container>
    );
  }
}

FrevaGPT.propTypes = {
  frevaGPT: PropTypes.shape({
    thread: PropTypes.string,
    conversation: PropTypes.array,
  }),
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  frevaGPT: state.frevaGPTReducer,
});

export default connect(mapStateToProps)(FrevaGPT);
