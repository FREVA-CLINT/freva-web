import React from "react";
import { Card } from "react-bootstrap";

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
    <div>
      <Card className="mb-3 shadow-sm">
        <div className="btn btn-outline-secondary border-0 p-3 rounded-top text-start card-header shadow-sm button-div">
          General requests
        </div>
        <div className="p-3 py-2 collapse show">
          {botRequests.general.map((element) => {
            return (
              <div key={element.thread}>
                <a
                  className="text-wrap"
                  href=""
                  onClick={() => changeToThread(element.thread)}
                >
                  {element.title}
                </a>
              </div>
            );
          })}
        </div>
      </Card>

      <Card className="mb-3 shadow-sm">
        <div className="btn btn-outline-secondary border-0 p-3 rounded-top text-start card-header shadow-sm button-div">
          Freva requests
        </div>
        <div className="p-3 py-2 collapse show">
          {botRequests.freva.map((element) => {
            return (
              <div key={element.thread}>
                <a
                  className="text-wrap"
                  href=""
                  onClick={() => changeToThread(element.thread)}
                >
                  {element.title}
                </a>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

export default SidePanel;
