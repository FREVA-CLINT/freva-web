import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';

import Spinner from "../../Components/Spinner";

import CodeBlock from "./CodeBlock";

const ChatBot = () => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [code, setCode] = useState("");
  const [image, setImage] = useState("");
  const [conversation, setConversation] = useState([]);
  const [answerLoading, setAnswerLoading] = useState(false);

  const ChatBotStyle = {
    botContainer: {
      display: "flex",
      flexDirection: "column",
    },
    questionInput: {
      width: "90%",
      borderRadius: "10px",
      border: ".1em solid lightgrey",
      padding: "10px",
      boxShadow: "0 .125rem .25rem rgba(0,0,0,.075)",
    },
    questionButton: {
      width: "8%",
      padding: "10px",
      borderRadius: "10px",
      marginLeft: "20px",
      boxShadow: "0 .125rem .25rem rgba(0,0,0,.075)",
    },
    question: {
      backgroundColor: "#aaa",
      borderRadius: "10px",
      padding: "10px",
      boxShadow: "0 .125rem .25rem rgba(0,0,0,.075)",
      listStyle: "none",
      margin: "10px 0px 10px 100px",
    },
    answer: {
      backgroundColor: "#ccc",
      borderRadius: "10px",
      padding: "10px",
      boxShadow: "0 .125rem .25rem rgba(0,0,0,.075)",
      listStyle: "none",
      margin: "10px 100px 10px 0px",
    },
  }

  useEffect(() => {
    if (answer !== "") setConversation(prevConversation => [...prevConversation, {type: 'answer', content: answer}])
  }, [answer]);

  useEffect(() => {
    if (code !== "") setConversation(prevConversation => [...prevConversation, {type: 'code', content: code}])
  }, [code])

  useEffect(() => {
    if (image !== "") setConversation(prevConversation => [...prevConversation, {type: 'image', content: image}])
  }, [image])

  async function requestBot() {

    setAnswerLoading(true);

    try {
      const response = await fetch('/api/chatbot/streamresponse?' + new URLSearchParams({
        input: encodeURIComponent(question),
        auth_key: process.env.BOT_AUTH_KEY,
      }).toString());

      const decoder = new TextDecoder('utf-8');
      let botAnswer = "";
      let botCode = "";
      let botImage = "";

      for await ( const chunk of response.body) {
        (decoder.decode(chunk)).split(/}{/).filter(function(e) { 
          if (!e.startsWith("{") && !e.endsWith("}")) {
            const variantString = JSON.parse(`{${e}}`);
            console.log('####', variantString);

            // the bot mixes code and answer text
            // if an answer starts to prompt code, display the previous answer (if not empty) and the start code box
            if (variantString.variant === 'Code' || variantString.variant === 'CodeOutput') {

              // collect code snippets
              botCode = botCode + variantString.content[0];
            } else if (variantString.variant === 'Image') {
              botImage = botImage + variantString.content;
            } else {
              botAnswer = botAnswer + variantString.content;
            }
          }
        });
      }

      if (botCode !== "") setCode(botCode); botCode = "";
      if (botImage !== "") setImage(botImage); botImage = "";
      if (botAnswer !== "") setAnswer(botAnswer); botAnswer = "";

    } catch(error) {
      setAnswer('Failed to fetch streamresponse');
      console.log(error);
    }
    setAnswerLoading(false);
  }

  function handleInputChange(event) {
    setQuestion(event.target.value);
  }

  function handleBotRequest(){
    const newQuestion = {type: 'question', content: question};
    setConversation(prevConversation => [...prevConversation, newQuestion]);
    setQuestion("");

    requestBot();
  }

  return (
    <Container>
      <div style={ChatBotStyle.botContainer}>
        <ul>
          {conversation.map((element, index) => {
            if (element.type === 'code') {
              return <CodeBlock key={index} code={element.content}/>
            } else if (element.type === 'image') {
              return <img key={index} src={`data:image/jpeg;base64,${element.content}`} />
            } else {
              return <li style={ChatBotStyle[element.type]} key={index}>{element.content}</li>}
            }
          )}
        </ul>
        {answerLoading ? (<Spinner/>) : null}

        <div>
          <input style={ChatBotStyle.questionInput} value={question} onChange={handleInputChange} placeholder="Ask a question"/>
          <button style={ChatBotStyle.questionButton} onClick={handleBotRequest} disabled={answerLoading}>Send</button>
        </div>
      </div>
    </Container>
  );
};

export default ChatBot;
