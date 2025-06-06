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
  Spinner,
  Card,
} from "react-bootstrap";

import { browserHistory } from "react-router";
import { isEmpty, debounce } from "lodash";

import { FaStop, FaPlay, FaArrowDown, FaArrowUp } from "react-icons/fa";

import queryString from "query-string";

import ChatBlock from "./components/ChatBlock";
import SidePanel from "./components/SidePanel";
import PendingAnswerComponent from "./components/PendingAnswerComponent";

import {
  truncate,
  chatExceedsWindow,
  getPosition,
  scrollToChatBottom,
} from "./utils";

import { setThread, setConversation, addElement } from "./actions";

import { botSuggestions } from "./exampleRequests";

class FrevaGPT extends React.Component {
  constructor(props) {
    super(props);
    this.handleUserInput = this.handleUserInput.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.createNewChat = this.createNewChat.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.toggleBotSelect = this.toggleBotSelect.bind(this);
    this.handleStop = this.handleStop.bind(this);
    this.submitUserInput = this.submitUserInput.bind(this);
    this.setPosition = this.setPosition.bind(this);
    this.resizeInputField = this.resizeInputField.bind(this);
    this.scrollDown = this.scrollDown.bind(this);

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
      atBottom: false,
      atTop: true,
      reader: undefined,
    };

    this.lastVariant = React.createRef("User");
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
      const response = await fetch(`/api/chatbot/availablechatbots?`);
      if (response.ok) {
        this.setState({ botModelList: await response.json() });
      } else {
        this.setState({ botModelList: ["No model information available."] });
      }
    };

    if (await successfulPing()) {
      this.setState({ botOkay: true });
      await getBotModels();
    } else {
      this.setState({ botOkay: false });
    }

    this.setPosition();
  }

  createNewChat() {
    this.handleStop(false)
      .then(() => {
        this.props.dispatch(setConversation([]));
        this.props.dispatch(setThread(""));
        browserHistory.push({
          pathname: "/chatbot/",
          search: "",
        });
        this.setState({
          showSuggestions: true,
          atBottom: true,
          atTop: true,
          dynamicAnswer: "",
          dynamicVariant: "",
          reader: undefined,
        });
        window.scrollTo(0, 0);
        return;
      })
      .catch((err) => {
        // eslint-disable-next-line no-console
        console.error(err);
      });
  }

  handleUserInput(e) {
    this.setState({ userInput: e.target.value });
  }

  async handleKeyDown(e) {
    if (e.key === "Enter" && !isEmpty(e.target.value.trim())) {
      e.preventDefault(); // preventing to add a new line within textare when sending request by pressing enter
      this.handleSubmit(e.target.value);
    }
  }

  async submitUserInput() {
    const userInput = this.state.userInput;

    if (!isEmpty(userInput.trim())) {
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

    if (response.ok) {
      const reader = response.body.getReader();
      this.setState({ reader });
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

          for (
            let bufferIndex = 0;
            bufferIndex < buffer.length;
            bufferIndex++
          ) {
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
                  this.lastVariant.current = varObj.variant;
                  this.setState({ dynamicAnswer: "", dynamicVariant: "" });
                  varObj = jsonBuffer;
                } else {
                  // if object has same variant, add content
                  // eslint-disable-next-line no-lonely-if
                  if (
                    varObj.variant === "Code" ||
                    varObj.variant === "CodeOutput"
                  ) {
                    varObj.content[0] =
                      varObj.content[0] + jsonBuffer.content[0];
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
    } else {
      this.props.dispatch(
        addElement({
          variant: "ServerError",
          content: response.statusText,
        })
      );
    }
  }

  async getOldThread(thread) {
    const queryObject = { thread_id: thread };
    const response = await fetch(
      `/api/chatbot/getthread?` + queryString.stringify(queryObject)
    );

    const variantArray = await response.json();
    this.props.dispatch(setConversation(variantArray));
  }

  async handleStop(dispatchStopMessage = true) {
    // stop of thread only possible if a thread id is given
    if (this.state.reader) {
      await this.state.reader.cancel();
    }
    const queryObject = { thread_id: this.props.frevaGPT.thread };
    if (this.props.frevaGPT.thread) {
      await fetch(`/api/chatbot/stop?` + queryString.stringify(queryObject));
    }

    this.setState({ loading: false, reader: undefined });
    if (dispatchStopMessage) {
      this.props.dispatch(
        addElement({ variant: "UserStop", content: "Request stopped manually" })
      );
    }
  }

  toggleBotSelect() {
    this.setState({ hideBotModelList: !this.state.hideBotModelList });
  }

  setPosition() {
    const position = getPosition();
    this.setState({
      atBottom: position.atBottom,
      atTop: position.atTop,
    });
  }

  resizeInputField() {
    const inputField = document.getElementById("inputField");
    const style = inputField.style;

    style.height = inputField.style.minHeight = "auto";
    style.minHeight = `${Math.min(inputField.scrollHeight, parseInt(inputField.style.maxHeight))}px`;
    style.height = `${inputField.scrollHeight}px`;
  }

  scrollDown() {
    if (chatExceedsWindow() && this.state.atBottom) {
      scrollToChatBottom();
    }
  }

  renderAlert() {
    return (
      <Alert key="botError" variant="danger">
        The bot is currently not available. Please retry later.
      </Alert>
    );
  }

  renderSuggestions() {
    return (
      <>
        {this.state.showSuggestions ? (
          <>
            {botSuggestions.map((element) => {
              return (
                <div key={`${element}-div`} className="col-md-3 mb-2">
                  <OverlayTrigger
                    key={`${element}-tooltip`}
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
          </>
        ) : null}
      </>
    );
  }

  renderBotInput() {
    return (
      <Col id="botInput">
        <InputGroup className="mb-2 pb-2">
          <FormControl
            as="textarea"
            id="inputField"
            rows={1}
            value={this.state.userInput}
            onChange={(e) => {
              this.handleUserInput(e);
              this.resizeInputField();
            }}
            onKeyDown={this.handleKeyDown}
            placeholder="Ask a question"
          />
          {this.state.loading ? (
            <Button
              variant="outline-danger"
              onClick={this.handleStop}
              className="d-flex align-items-center"
            >
              <FaStop />
            </Button>
          ) : (
            <Button
              variant="outline-success"
              onClick={this.submitUserInput}
              className="d-flex align-items-center"
            >
              <FaPlay />
            </Button>
          )}
        </InputGroup>
      </Col>
    );
  }

  renderChatSpinner() {
    return (
      <>
        {this.state.loading && !this.state.dynamicAnswer ? (
          <Row className="mb-3">
            <Col md={3}>
              <Card className="shadow-sm card-body border-0 border-bottom mb-3 bg-light d-flex flex-row align-items-center">
                <Spinner size="sm" />
                <span className="ms-2">
                  {this.lastVariant.current === "Code"
                    ? "Executing..."
                    : "Thinking..."}
                </span>
              </Card>
            </Col>
          </Row>
        ) : null}
      </>
    );
  }

  renderScrollButtons() {
    // here also no suitable solutions using bootstrap found -> need for better solution
    const scrollButtonStyle = {
      zIndex: 10,
      right: "40px",
      bottom: "10px",
      position: "sticky",
    };

    return (
      <>
        <Col
          md={12}
          style={scrollButtonStyle}
          className="d-flex flex-row justify-content-end"
        >
          <div className="d-flex flex-column">
            {!this.state.atTop ? (
              <Button
                variant="secondary"
                className={!this.state.atBottom ? "mb-2" : ""}
                onClick={() =>
                  document
                    .getElementById("chatContainer")
                    .scrollTo({ top: 0, behavior: "smooth" })
                }
              >
                <FaArrowUp />
              </Button>
            ) : null}

            {!this.state.atBottom ? (
              <Button variant="secondary" onClick={() => scrollToChatBottom()}>
                <FaArrowDown />
              </Button>
            ) : null}
          </div>
        </Col>
      </>
    );
  }

  renderBotContent() {
    const windowHeight = document.documentElement.clientHeight * 0.8;

    // better solution needed (wasn't able to find any suitable bootstrap class -> need of fixed height for overflow-auto -> scrolling)
    const chatWindow = {
      height: windowHeight,
    };

    return (
      <>
        <Col md={3}>
          <SidePanel />
        </Col>

        <Col
          md={9}
          className={
            "d-flex flex-column " +
            (this.state.showSuggestions
              ? "justify-content-start"
              : "justify-content-between")
          }
          style={chatWindow}
        >
          <Row
            className="overflow-auto position-relative"
            id="chatContainer"
            onScroll={debounce(this.setPosition, 100)}
          >
            <Col md={12}>
              <ChatBlock onScrollDown={this.scrollDown} />

              <PendingAnswerComponent
                content={this.state.dynamicAnswer}
                variant={this.state.dynamicVariant}
                atBottom={this.state.atBottom}
                ref={{
                  lastVariant: this.lastVariant,
                }}
              />

              {this.renderChatSpinner()}
            </Col>
            {this.renderScrollButtons()}
          </Row>

          <Row>
            {this.renderSuggestions()}
            {this.renderBotInput()}
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
          {this.state.botModelList.map((model) => {
            return <option key={model}>{model}</option>;
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
