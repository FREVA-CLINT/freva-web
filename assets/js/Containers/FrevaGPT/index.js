import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, FormControl, InputGroup, Card } from 'react-bootstrap';
// import JSONStream from 'JSONStream';
import { browserHistory } from "react-router";

import Spinner from "../../Components/Spinner";

import CodeBlock from "./CodeBlock";
import SidePanel from "./SidePanel";

const ChatBot = () => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [code, setCode] = useState("");
  const [image, setImage] = useState("");
  const [conversation, setConversation] = useState([]);
  const [answerLoading, setAnswerLoading] = useState(false);
  const thread = useRef("");
  const endpoint = useRef("streamresponse");

  useEffect(() => {
    if (answer !== "") setConversation(prevConversation => [...prevConversation, {variant: 'Assistant', content: answer}])
  }, [answer]);

  useEffect(() => {
    if (code !== "") setConversation(prevConversation => [...prevConversation, {variant: 'Code', content: [code]}])
  }, [code])

  useEffect(() => {
    if (image !== "") setConversation(prevConversation => [...prevConversation, {variant: 'Image', content: image}])
  }, [image])

  useEffect(() => {
    // when starting a new conversation there is no thread_id set on mount
    // when jumping to an old conversion a thread_id is given (needed for loading old conversation)
    const givenQueryParams = browserHistory.getCurrentLocation().query;

    if ("thread_id" in givenQueryParams && givenQueryParams.thread_id !== "") {
      thread.current = givenQueryParams.thread_id;
      endpoint.current = "getthread";
      requestBot();
    }
  }, [])

  const fetchData = async () => {
    // response of a new bot request is streamed
    const response = await fetch(`/api/chatbot/${endpoint.current}?` + new URLSearchParams({
      input: encodeURIComponent(question),
      auth_key: process.env.BOT_AUTH_KEY,
      thread_id: thread.current,
    }).toString());

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    // let unresolvedChunk = "";

    let botAnswer = "";
    let botCode = "";

    // } else if (endpoint.current === "getthread") {
    //   jsonStream.on("data", (value) => {
    //     // old threads are streamed as one package (an array containing all conversation parts)
    //     console.log(value);
    //     setConversation(value);
    //   })
    // }
    
    let buffer = "";

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
            buffer = buffer.slice(bufferIndex + 1);

            switch(jsonBuffer.variant) {
              case "Assistant":
                botAnswer = botAnswer + jsonBuffer.content;
                break;
              case "Code":
                botCode = botCode + jsonBuffer.content[0];
                break;
              case "Image":
                setImage(jsonBuffer.content);
                break;
              default:
                botAnswer = botAnswer + jsonBuffer.content;
            }

            foundSomething = true;
            break;
          } catch(err) {
            // don't do anything
          }  
        }
      }
    }
    setCode(botCode);
    setAnswer(botAnswer);
    
  };

  async function requestBot() {
    setAnswerLoading(true);
    try {
      await fetchData();
    } catch(error) {
      console.log(error);
      // indicate error
      setConversation(prevConversation => [...prevConversation, { variant: "Error", content: "An error occured, please try again!"}])
    }
    setAnswerLoading(false);
  }

  function handleBotRequest(){
    if (question !== "") {
      const newQuestion = {variant: 'User', content: question};
      setConversation(prevConversation => [...prevConversation, newQuestion]);
      setQuestion("");

      requestBot();
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      handleBotRequest();
    }
  }

  function handleInputChange(event) {
    setQuestion(event.target.value);
  }
  
  return (
    <Container>
      <Row>
        <div className="d-flex justify-content-between">
          <h2>FrevaGPT</h2>
        </div>

        <Col md={4}>
          <SidePanel/>
        </Col>

        <Col md={8}>
          <Col>
            {conversation.map((element, index) => {
              if (element.variant !== "ServerHint" && element.variant !== "StreamEnd") {
                switch(element.variant){
                  case "Image":
                    return (
                      <Col key={index} md={{span: 10, offset: 0}}>
                        <img className="w-100" src={`data:image/jpeg;base64,${element.content}`} />
                      </Col>
                    );

                  case "Code":
                  case "CodeOutput":
                    return (<Col md={{span:10, offset: 0}} key={index}><CodeBlock title={element.variant} code={element.content}/></Col>);

                  default:
                    return (
                      <Col md={element.variant !== 'User' ? {span: 10, offset: 0} : {span: 10, offset: 2}} key={index}>
                        <Card 
                          className={element.variant !== 'User' ? "shadow-sm card-body border-0 border-bottom mb-3 bg-light"
                                                                : "shadow-sm card-body border-0 border-bottom mb-3 bg-info"}
                          key={index}>
                            {decodeURI(element.content)}
                        </Card>
                      </Col>
                    );  
                }
              }
            }
            )}
          </Col>

          {answerLoading ? (<Row className="mb-3"><Col md={1}><Spinner/></Col></Row>) : null}

          <Row>
            <Col md={10}>
              <InputGroup className="mb-2 pb-2">
                <FormControl type="text" value={question} onChange={handleInputChange} onKeyDown={handleKeyDown} placeholder="Ask a question"/>
              </InputGroup>
            </Col>

            <Col md={2}>
              <button onClick={handleBotRequest} disabled={answerLoading} className="btn btn-secondary w-100">Send</button>
            </Col>
          </Row>
          
        </Col>
      </Row>
    </Container>
  );
};

export default ChatBot;
