import React from 'react';
import PropTypes from "prop-types";
import { connect } from 'react-redux';

import { 
  Container,
  Row,
  Col,
  FormControl,
  InputGroup,
  Button,
  Form,
  OverlayTrigger,
  Tooltip,
  Spinner } from 'react-bootstrap';

  import {
    FaAlignJustify,
    FaList,
  } from "react-icons/fa";

import { browserHistory } from 'react-router';
import { isEmpty, has } from 'lodash';

import ChatBlock from './ChatBlock';
import SidePanel from "./SidePanel";

import { objectToQueryString } from './utils';

import {
  setThread,
  setConversation,
  addElement,
} from './actions';

import { ViewTypes } from './constants';

import 'bootstrap-icons/font/bootstrap-icons.css';

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

    const firstViewPort = localStorage.FrevaGPTViewPort ?? ViewTypes.SIDE_PANEL_SHOWN;
    localStorage.FrevaGPTViewPort = firstViewPort;

    this.state = {
      loading: false,
      userInput: "",
      botModelList: [],
      botModel: "",
      hideBotModelList: true,
      viewPort: firstViewPort,
    };
  }

  componentDidMount() {

    // if thread giving on mounting the component, set thread within store
    const givenQueryParams = browserHistory.getCurrentLocation().query;
    if (has(givenQueryParams, "thread_id") && !isEmpty(givenQueryParams.thread_id)) {
      this.props.dispatch(setThread(givenQueryParams.thread_id));

      // request content of old thread if threa_id is given
      this.setState({ loading: true });
      this.getOldThread(givenQueryParams.thread_id);
      this.setState({ loading: false });
    }

    const getBotModels = async () => {
      const queryObject = {
        auth_key: process.env.BOT_AUTH_KEY,
      };
      const response = await fetch(`/api/chatbot/availablechatbots?` + objectToQueryString(queryObject));
      this.setState({ botModelList: await response.json()});
    }

    getBotModels();
  }

  createNewChat() {

    this.props.dispatch(setConversation([]));
    this.props.dispatch(setThread(""));
    browserHistory.push({
      pathname: '/chatbot/',
      search: "",
    });
    window.scrollTo(0, 0)
  }

  handleUserInput(e) {
    this.setState({ userInput: e.target.value });
  }

  async handleKeyDown(e) {
    if (e.key === "Enter") {
      this.handleSubmit();
    }
  }

  async handleSubmit() {
    this.props.dispatch(addElement({ variant: "User", content: this.state.userInput}));
    this.setState({ userInput: "" });

    this.setState({ loading: true });
    try {
      await this.fetchData()
    } catch(err) {
      this.props.dispatch(addElement({ variant: "FrontendError", content: "An error occured during rendering!" }))
      console.error(err);
    }
    this.setState({ loading: false });
  }

  async fetchData() {

    const queryObject = {
      input: this.state.userInput,
      auth_key: process.env.BOT_AUTH_KEY,
      thread_id: this.props.frevaGPT.thread,
      chatbot: this.state.botModel,
      freva_config: "/work/ch1187/clint/freva-dev/freva/evaluation_system.conf",
    };

    // response of a new bot request is streamed
    const response = await fetch(`/api/chatbot/streamresponse?` + objectToQueryString(queryObject)); //, signal);

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    
    let buffer = "";
    let varObj = {};

    // eslint-disable-next-line no-constant-condition
    while (true) {
      // eslint-disable-next-line no-await-in-loop
      const { done, value } = await reader.read();
      if (done) break;

      const decodedValues = decoder.decode(value);
      buffer = buffer + decodedValues;

      let foundSomething = true;

      while (foundSomething) {
        foundSomething = false;

        for (let bufferIndex = 0; bufferIndex < buffer.length; bufferIndex ++) {

          if (buffer[bufferIndex] !== "}") continue;
          const subBuffer = buffer.slice(0, bufferIndex + 1);

          try {
            const jsonBuffer = JSON.parse(subBuffer);
            buffer = buffer.slice(bufferIndex + 1); // shorten string by already evaluated string        

            // object is not empty so compare variants
            if (Object.keys(varObj).length !== 0) {
              // if object has not same variant, add answer to conversation and override object
              if (varObj.variant !== jsonBuffer.variant) {
                this.props.dispatch(addElement(varObj));
                varObj = jsonBuffer;
              } else {
                // if object has same variant, add content
                // eslint-disable-next-line no-lonely-if
                if (varObj.variant === "Code" || varObj.variant === "CodeOutput") varObj.content[0] = varObj.content[0] + jsonBuffer.content[0];
                else varObj.content = varObj.content + jsonBuffer.content;
              }
            } else {
              // object is empty so add content
              varObj = jsonBuffer;

              // set thread id
              if (this.props.frevaGPT.thread === "" && varObj.variant === "ServerHint") {
                try {
                  this.props.dispatch(setThread(JSON.parse(varObj.content).thread_id));
                  browserHistory.push({
                    pathname: '/chatbot/',
                    search: `?thread_id=${this.props.frevaGPT.thread}`,
                  });
                } catch(err) {
                  // handle warning
                }
              }
            }
            
            foundSomething = true;
            break;
          } catch(err) {
            console.error(err);
          }  
        }
      }
    }

  }

  async getOldThread(thread) {
    const response = await fetch(`/api/chatbot/getthread?` + new URLSearchParams({
      auth_key: process.env.BOT_AUTH_KEY,
      thread_id: thread,
      }).toString());
    
    const variantArray = await response.json();
    this.props.dispatch(setConversation(variantArray));
  }

  async handleStop() {
    // stop of thread only possible if a thread id is given
    if (this.props.frevaGPT.thread) {
      await fetch(`/api/chatbot/stop?` + new URLSearchParams({
        auth_key: process.env.BOT_AUTH_KEY,
        thread_id: this.props.frevaGPT.thread,
      }).toString());
    }

    // abort fetch request anyway (especially if no thread is given)
    // if (abortController.current) abortController.current.abort();
      
    this.setState({loading: false });
    this.props.dispatch(addElement({variant: "UserStop", content: "Request stopped manually"}))
  }

  toggleBotSelect() {
    this.setState({ hideBotModelList: !this.state.hideBotModelList });
    console.log("hi");
  }

  render() {
    const showSidePanel = this.state.viewPort === ViewTypes.SIDE_PANEL_SHOWN;

    return (
      <Container>
        <Row>
          <div className="d-flex justify-content-between">
            <h2 onClick={this.toggleBotSelect}>FrevaGPT</h2>
            <div className="d-flex justify-content-between mb-2">
              <Form.Select 
                value={this.botModel}
                onChange={(x) => { this.setState({ botModel: x.target.value }); }}
                className="me-1 mb-3"
                placeholder="Choose Chatbot"
                hidden={this.state.hideBotModelList}>
                {this.state.botModelList.map((x) => {
                    return <option key={x}>{x}</option>;
                })}
              </Form.Select>
              <OverlayTrigger overlay={<Tooltip>Hide side panel</Tooltip>}>
                <Button 
                  className="me-1"
                  variant="outline-secondary"
                  active={!showSidePanel}
                  onClick={() =>
                    this.setState(
                      { viewPort: ViewTypes.SIDE_PANEL_HIDDEN },
                      () => {
                        localStorage.FrevaGPTViewPort =
                          this.state.viewPort;
                      }
                    )
                  }>
                    <FaAlignJustify/>
                  </Button>
              </OverlayTrigger>
              <OverlayTrigger overlay={<Tooltip>Show side panel</Tooltip>}>
                <Button 
                  className="me-1"
                  variant="outline-secondary"
                  active={showSidePanel}
                  onClick={() =>
                    this.setState(
                      { viewPort: ViewTypes.SIDE_PANEL_SHOWN },
                      () => {
                        localStorage.FrevaGPTViewPort =
                          this.state.viewPort;
                      }
                    )
                  }>
                    <FaList/>
                  </Button>
              </OverlayTrigger>
            </div>
          </div>
  
          { showSidePanel ? (<Col md={4}><SidePanel/></Col>) : null }
            
          <Col md={showSidePanel ? 8 : 12}>

            <ChatBlock></ChatBlock>
            
            {this.state.loading ? (<Row className="mb-3"><Col md={1}><Spinner/></Col></Row>) : null}
  
            <Row>
              <Col md={10}>
                <InputGroup className="mb-2 pb-2">
                  <FormControl type="text" value={this.state.userInput} onChange={this.handleUserInput} onKeyDown={this.handleKeyDown} placeholder="Ask a question"/>
                  {this.state.loading 
                    ? (<Button variant="outline-danger" onClick={this.handleStop}><i className="bi bi-stop-fill"></i></Button>)
                    : (<Button variant="outline-success" onClick={this.handleSubmit}><i className="bi bi-play-fill"></i></Button>)
                  } 
                </InputGroup>
              </Col>
  
              <Col md={2}>
                <button className="btn btn-info w-100" onClick={this.createNewChat}>New Chat</button>
              </Col>
            </Row>
            
          </Col>
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
}

const mapStateToProps = (state) => ({
  frevaGPT: state.frevaGPTReducer,
})

export default connect(mapStateToProps)(FrevaGPT);
