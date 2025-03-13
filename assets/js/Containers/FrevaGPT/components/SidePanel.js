import React from "react";
import { Card, OverlayTrigger, Tooltip } from "react-bootstrap";

import { browserHistory } from "react-router";

import { botRequests } from "../exampleRequests";

function SidePanel() {
  function changeToThread(thread) {
    browserHistory.push({
      pathname: "/chatbot/",
      search: `?thread_id=${thread}`,
    });
  }

  return (
    <>
      <Card className="mb-3 shadow-sm">
        <Card.Header className="outline-secondary border-0 p-3 rounded-top text-start card-header shadow-sm">
          General requests
        </Card.Header>
        <Card.Body className="p-3 py-2">
          {botRequests.general.map((element) => {
            return (
              <div key={element.thread} className="mb-2 text-truncate color">
                <OverlayTrigger
                  key={`${element.title}-tooltip`}
                  overlay={<Tooltip>{element.title}</Tooltip>}
                >
                  <a href="" onClick={() => changeToThread(element.thread)}>
                    {element.title}
                  </a>
                </OverlayTrigger>
              </div>
            );
          })}
        </Card.Body>
      </Card>

      <Card className="mb-3 shadow-sm">
        <Card.Header className="outline-secondary border-0 p-3 rounded-top text-start card-header shadow-sm">
          Freva requests
        </Card.Header>
        <Card.Body className="p-3 py-2">
          {botRequests.freva.map((element) => {
            return (
              <div key={element.thread} className="mb-2 text-truncate color">
                <OverlayTrigger
                  key={`${element.title}-tooltip`}
                  overlay={<Tooltip>{element.title}</Tooltip>}
                >
                  <a href="" onClick={() => changeToThread(element.thread)}>
                    {element.title}
                  </a>
                </OverlayTrigger>
              </div>
            );
          })}
        </Card.Body>
      </Card>
    </>
  );
}

export default SidePanel;
