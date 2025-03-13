import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { withRouter } from "react-router";
import queryString from "query-string";
import {
  BsRecordCircleFill,
  BsRecordCircle,
  BsCircleSquare,
} from "react-icons/bs";
import {
  Button,
  InputGroup,
  Form,
  OverlayTrigger,
  Tooltip,
  Dropdown,
  DropdownButton,
} from "react-bootstrap";

import {
  BBOX_RANGE_FILE,
  BBOX_RANGE_FLEXIBLE,
  BBOX_RANGE_STRICT,
} from "./constants";

function BBoxSelector({ databrowser, router, location }) {
  const [selector, setSelector] = useState(BBOX_RANGE_FLEXIBLE);
  const [minLon, setMinLon] = useState("");
  const [maxLon, setMaxLon] = useState("");
  const [minLat, setMinLat] = useState("");
  const [maxLat, setMaxLat] = useState("");

  useEffect(() => {
    setMinLon(databrowser.minLon || "");
    setMaxLon(databrowser.maxLon || "");
    setMinLat(databrowser.minLat || "");
    setMaxLat(databrowser.maxLat || "");
    setSelector(databrowser.bboxSelector || BBOX_RANGE_FLEXIBLE);
  }, [databrowser]);

  function applyChanges() {
    const currentLocation = location.pathname;
    const {
      bboxSelector: ignore1,
      minLon: ignore2,
      maxLon: ignore3,
      minLat: ignore4,
      maxLat: ignore5,
      ...queryObject
    } = location.query;

    const query = queryString.stringify({
      ...queryObject,
      minLon,
      maxLon,
      minLat,
      maxLat,
      bboxSelector: selector,
    });
    router.push(currentLocation + "?" + query);
  }

  function onKeyPress(errorMessage, e) {
    const enterKey = 13;
    if (!errorMessage && e.charCode === enterKey) {
      applyChanges();
    }
  }

  const isValidLongitude = (value) => {
    const num = Number(value);
    return Number.isFinite(num) && num >= -180 && num <= 180;
  };

  const isValidLatitude = (value) => {
    const num = Number(value);
    return Number.isFinite(num) && num >= -90 && num <= 90;
  };

  const minLonError =
    minLon && !isValidLongitude(minLon)
      ? "Invalid longitude (-180 to 180)"
      : minLon && maxLon && parseFloat(minLon) > parseFloat(maxLon)
        ? "Max longitude must be greater than min longitude"
        : "";

  const maxLonError =
    maxLon && !isValidLongitude(maxLon)
      ? "Invalid longitude (-180 to 180)"
      : minLon && maxLon && parseFloat(minLon) > parseFloat(maxLon)
        ? "Max longitude must be greater than min longitude"
        : "";
  const minLatError =
    minLat && !isValidLatitude(minLat)
      ? "Invalid latitude (-90 to 90)"
      : minLat && maxLat && parseFloat(minLat) > parseFloat(maxLat)
        ? "Max latitude must be greater than min latitude"
        : "";

  const maxLatError =
    maxLat && !isValidLatitude(maxLat)
      ? "Invalid latitude (-90 to 90)"
      : minLat && maxLat && parseFloat(minLat) > parseFloat(maxLat)
        ? "Max latitude must be greater than min latitude"
        : "";

  let errorMessage = minLonError || maxLonError || minLatError || maxLatError;

  if (!minLon || !maxLon || !minLat || !maxLat) {
    errorMessage = "All coordinates are required";
  }
  if (
    !errorMessage &&
    minLon &&
    maxLon &&
    parseFloat(minLon) > parseFloat(maxLon)
  ) {
    errorMessage = "Max longitude must be greater than min longitude";
  }
  if (
    !errorMessage &&
    minLat &&
    maxLat &&
    parseFloat(minLat) > parseFloat(maxLat)
  ) {
    errorMessage = "Max latitude must be greater than min latitude";
  }

  let applyButton;
  if (errorMessage) {
    const tooltip = <Tooltip id="boxWarning">{errorMessage}</Tooltip>;
    applyButton = (
      <OverlayTrigger overlay={tooltip} placement="top">
        <span>
          <Button variant="danger" disabled>
            Apply
          </Button>
        </span>
      </OverlayTrigger>
    );
  } else {
    applyButton = (
      <Button variant="primary" onClick={applyChanges.bind(this)}>
        Apply
      </Button>
    );
  }

  return (
    <div onKeyPress={onKeyPress.bind(this, errorMessage)}>
      <InputGroup className="mb-4">
        <InputGroup.Text id="bbox-text">Operator</InputGroup.Text>
        <DropdownButton
          className="selector-button"
          variant="outline-secondary"
          title={selector}
          id="time-operator-dropdown"
        >
          <Dropdown.Item
            onClick={() => setSelector(BBOX_RANGE_FLEXIBLE)}
            href="#"
          >
            <BsCircleSquare /> {BBOX_RANGE_FLEXIBLE}
          </Dropdown.Item>
          <Dropdown.Item
            onClick={() => setSelector(BBOX_RANGE_STRICT)}
            href="#"
          >
            <BsRecordCircleFill /> {BBOX_RANGE_STRICT}
          </Dropdown.Item>
          <Dropdown.Item onClick={() => setSelector(BBOX_RANGE_FILE)} href="#">
            <BsRecordCircle /> {BBOX_RANGE_FILE}
          </Dropdown.Item>
        </DropdownButton>
      </InputGroup>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: "1rem",
          marginBottom: "1rem",
        }}
      >
        <div>
          <InputGroup>
            <InputGroup.Text>Min Lon</InputGroup.Text>
            <Form.Control
              value={minLon}
              placeholder="-180"
              onChange={(e) => setMinLon(e.target.value)}
              isInvalid={!!minLonError}
            />
          </InputGroup>
          <div className="text-danger small">{minLonError}&nbsp;</div>
        </div>
        <div>
          <InputGroup>
            <InputGroup.Text>Max Lon</InputGroup.Text>
            <Form.Control
              value={maxLon}
              placeholder="180"
              onChange={(e) => setMaxLon(e.target.value)}
              isInvalid={!!maxLonError}
            />
          </InputGroup>
          <div className="text-danger small">{maxLonError}&nbsp;</div>
        </div>
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <InputGroup>
            <InputGroup.Text>Min Lat</InputGroup.Text>
            <Form.Control
              value={minLat}
              placeholder="-90"
              onChange={(e) => setMinLat(e.target.value)}
              isInvalid={!!minLatError}
            />
          </InputGroup>
          <div className="text-danger small">{minLatError}&nbsp;</div>
        </div>
        <div>
          <InputGroup>
            <InputGroup.Text>Max Lat</InputGroup.Text>
            <Form.Control
              value={maxLat}
              placeholder="90"
              onChange={(e) => setMaxLat(e.target.value)}
              isInvalid={!!maxLatError}
            />
          </InputGroup>
          <div className="text-danger small">{maxLatError}&nbsp;</div>
        </div>
      </div>

      {applyButton}
    </div>
  );
}

BBoxSelector.propTypes = {
  databrowser: PropTypes.shape({
    minLon: PropTypes.string,
    maxLon: PropTypes.string,
    minLat: PropTypes.string,
    maxLat: PropTypes.string,
    bboxSelector: PropTypes.string,
  }),
  location: PropTypes.object.isRequired,
  router: PropTypes.object.isRequired,
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  databrowser: state.databrowserReducer,
});

export default withRouter(connect(mapStateToProps)(BBoxSelector));
