import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { withRouter } from "react-router";
import queryString from "query-string";
import {
  Button,
  InputGroup,
  Form,
  OverlayTrigger,
  Tooltip,
  Row,
  Col,
} from "react-bootstrap";

function BoundingBoxSelector({ databrowser, router, location }) {
  const [minX, setMinX] = useState("-180");
  const [maxX, setMaxX] = useState("180");
  const [minY, setMinY] = useState("-90");
  const [maxY, setMaxY] = useState("90");

  useEffect(() => {
    if (databrowser.bbox) {
      const [west, east, north, south] = databrowser.bbox
        .replace("ENVELOPE(", "")
        .replace(")", "")
        .split(", ")
        .map(Number);
      setMinX(west.toString());
      setMaxX(east.toString());
      setMinY(south.toString());
      setMaxY(north.toString());
    }
  }, [databrowser]);

  function validateCoordinates() {
    const parsedMinX = parseFloat(minX);
    const parsedMaxX = parseFloat(maxX);
    const parsedMinY = parseFloat(minY);
    const parsedMaxY = parseFloat(maxY);

    if (isNaN(parsedMinX) || isNaN(parsedMaxX) || isNaN(parsedMinY) || isNaN(parsedMaxY)) {
      return "All coordinates must be valid numbers";
    }

    if (parsedMinX < -180 || parsedMaxX > 180) {
      return "Longitude must be between -180 and 180";
    }

    if (parsedMinY < -90 || parsedMaxY > 90) {
      return "Latitude must be between -90 and 90";
    }

    if (parsedMinX >= parsedMaxX) {
      return "East longitude must be greater than West longitude";
    }

    if (parsedMinY >= parsedMaxY) {
      return "North latitude must be greater than South latitude";
    }

    return "";
  }

  function applyChanges() {
    const currentLocation = location.pathname;
    const { bbox: ignore, ...queryObject } = location.query;
    
    const bboxString = `ENVELOPE(${minX}, ${maxX}, ${maxY}, ${minY})`;
    const query = queryString.stringify({
      ...queryObject,
      bbox: bboxString,
    });
    
    router.push(currentLocation + "?" + query);
  }

  function onKeyPress(errorMessage, e) {
    const enterKey = 13;
    if (!errorMessage && e.charCode === enterKey) {
      applyChanges();
    }
  }

  const errorMessage = validateCoordinates();
  const applyButton = errorMessage ? (
    <OverlayTrigger overlay={<Tooltip>{errorMessage}</Tooltip>} placement="top">
      <span>
        <Button variant="danger" disabled>
          Apply
        </Button>
      </span>
    </OverlayTrigger>
  ) : (
    <Button variant="primary" onClick={applyChanges}>
      Apply
    </Button>
  );

  return (
    <div onKeyPress={onKeyPress.bind(this, errorMessage)}>
      <Row className="mb-3">
        <Col>
          <InputGroup>
            <InputGroup.Text>West</InputGroup.Text>
            <Form.Control
              type="number"
              step="0.1"
              value={minX}
              onChange={(e) => setMinX(e.target.value)}
              placeholder="-180"
            />
          </InputGroup>
        </Col>
        <Col>
          <InputGroup>
            <InputGroup.Text>East</InputGroup.Text>
            <Form.Control
              type="number"
              step="0.1"
              value={maxX}
              onChange={(e) => setMaxX(e.target.value)}
              placeholder="180"
            />
          </InputGroup>
        </Col>
      </Row>
      <Row className="mb-3">
        <Col>
          <InputGroup>
            <InputGroup.Text>South</InputGroup.Text>
            <Form.Control
              type="number"
              step="0.1"
              value={minY}
              onChange={(e) => setMinY(e.target.value)}
              placeholder="-90"
            />
          </InputGroup>
        </Col>
        <Col>
          <InputGroup>
            <InputGroup.Text>North</InputGroup.Text>
            <Form.Control
              type="number"
              step="0.1"
              value={maxY}
              onChange={(e) => setMaxY(e.target.value)}
              placeholder="90"
            />
          </InputGroup>
        </Col>
      </Row>
      <div className="text-danger mb-2">{errorMessage}&nbsp;</div>
      {applyButton}
    </div>
  );
}

BoundingBoxSelector.propTypes = {
  databrowser: PropTypes.object,
  location: PropTypes.object.isRequired,
  router: PropTypes.object.isRequired,
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  databrowser: state.databrowserReducer,
});

export default withRouter(connect(mapStateToProps)(BoundingBoxSelector));