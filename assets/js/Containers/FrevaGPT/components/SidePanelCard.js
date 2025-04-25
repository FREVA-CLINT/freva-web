import React from "react";

import PropTypes from "prop-types";

import { Card, OverlayTrigger, Tooltip } from "react-bootstrap";

import { browserHistory } from "react-router";

import { isEmpty } from "lodash";

function SidePanelCard(props) {
  function changeToThread(thread) {
    browserHistory.push({
      pathname: "/chatbot/",
      search: `?thread_id=${thread}`,
    });
  }

  return (
    <>
      {!isEmpty(props.data) ? (
        <Card className="mb-3 shadow-sm">
          <Card.Header className="outline-secondary border-0 p-3 rounded-top text-start card-header shadow-sm">
            {props.title}
          </Card.Header>
          <Card.Body className="p-3 py-2">
            {props.data.map((element) => {
              return (
                <div
                  key={element.thread_id}
                  className="mb-2 text-truncate color"
                >
                  <OverlayTrigger
                    key={`${element.topic}-tooltip`}
                    overlay={<Tooltip>{element.topic}</Tooltip>}
                  >
                    <a
                      href=""
                      onClick={() => changeToThread(element.thread_id)}
                    >
                      {element.topic}
                    </a>
                  </OverlayTrigger>
                </div>
              );
            })}
          </Card.Body>
        </Card>
      ) : null}
    </>
  );
}

SidePanelCard.propTypes = {
  title: PropTypes.string,
  data: PropTypes.array,
};

export default SidePanelCard;
