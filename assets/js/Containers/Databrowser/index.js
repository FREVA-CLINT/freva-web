import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Alert,
  Badge,
  OverlayTrigger,
  Tooltip,
} from "react-bootstrap";

import { FaAlignJustify, FaList } from "react-icons/fa";

import queryString from "query-string";
import { withRouter } from "react-router";

import AccordionItemBody from "../../Components/AccordionItemBody";
import OwnPanel from "../../Components/OwnPanel";
import Spinner from "../../Components/Spinner";

import { initCap, underscoreToBlank } from "../../utils";

import {
  loadFacets,
  setMetadata,
  loadFiles,
  updateFacetSelection,
} from "./actions";

import TimeRangeSelector from "./TimeRangeSelector";
import FilesPanel from "./FilesPanel";
import DataBrowserCommand from "./DataBrowserCommand";
import FacetDropdown from "./FacetDropdown";

const ViewTypes = {
  RESULT_CENTERED: "RESULT_CENTERED",
  FACET_CENTERED: "FACET_CENTERED",
};

class Databrowser extends React.Component {
  constructor(props) {
    super(props);
    this.clickFacet = this.clickFacet.bind(this);
    this.dropFacet = this.dropFacet.bind(this);
    this.state = { viewPort: ViewTypes.RESULT_CENTERED };
  }

  /**
   * On mount we load all facets and files to display
   * Also load the metadata.js script
   */
  componentDidMount() {
    this.props.dispatch(loadFacets(this.props.location));
    this.props.dispatch(loadFiles(this.props.location));
    this.props.dispatch(updateFacetSelection(this.props.location.query));
    const script = document.createElement("script");
    script.src = "/static/js/metadata.js";
    script.async = true;
    script.onload = () =>
      this.props.dispatch(
        setMetadata({
          variable: window.variable,
          model: window.model,
          institute: window.institute,
        })
      );
    document.body.appendChild(script);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.location.search !== this.props.location.search) {
      this.props.dispatch(loadFacets(this.props.location));
      this.props.dispatch(loadFiles(this.props.location));
      this.props.dispatch(updateFacetSelection(this.props.location.query));
    }
  }

  clickFacet(category, value) {
    const currentLocation = this.props.location.pathname;
    const query = queryString.stringify({
      ...this.props.location.query,
      [category]: value,
    });
    if (query) {
      this.props.router.push(currentLocation + "?" + query);
    } else {
      this.props.router.push(currentLocation);
    }
  }

  dropFacet(category) {
    const currentLocation = this.props.location.pathname;
    const { [category]: toRemove, ...queryObject } = this.props.location.query;
    const query = queryString.stringify(queryObject);
    this.props.router.push(currentLocation + "?" + query);
  }

  /**
   * Loop all facets and render the panels
   */
  renderFacetPanels() {
    const { facets, selectedFacets, metadata } = this.props.databrowser;
    // const { dispatch } = this.props;

    return Object.keys(facets).map((key) => {
      const value = facets[key];
      let panelHeader;
      const isFacetSelected = !!selectedFacets[key];
      if (isFacetSelected) {
        panelHeader = (
          <span>
            {initCap(underscoreToBlank(key))}:{" "}
            <strong>{selectedFacets[key]}</strong>
          </span>
        );
      } else if (value.length === 2) {
        panelHeader = (
          <span>
            {initCap(underscoreToBlank(key))}: <strong>{value[0]}</strong>
          </span>
        );
      } else {
        const numberOfValues = value.length / 2;
        panelHeader = (
          <span className="d-flex justify-content-between">
            <span>{initCap(underscoreToBlank(key))}</span>
            <Badge bg="secondary">{numberOfValues}</Badge>
          </span>
        );
      }
      return (
        <OwnPanel
          header={panelHeader}
          key={key}
          removeFacet={isFacetSelected ? () => this.dropFacet(key) : null}
        >
          <AccordionItemBody
            eventKey={key}
            value={value}
            isFacetCentered={this.state.viewPort === ViewTypes.FACET_CENTERED}
            facetClick={this.clickFacet}
            metadata={metadata[key] ? metadata[key] : null}
          />
        </OwnPanel>
      );
    });
  }

  renderTimeSelectionPanel() {
    const key = "time_range";
    const { dateSelector, minDate, maxDate } = this.props.databrowser;
    const isDateSelected = !!minDate;
    const title = isDateSelected ? (
      <span>
        Time Range: &nbsp;
        <span className="fw-bold">
          {dateSelector}: {minDate} to {maxDate}
        </span>
      </span>
    ) : (
      <span>Time Range</span>
    );
    return (
      <OwnPanel
        header={title}
        key={key}
        removeFacet={
          isDateSelected
            ? () => {
                const currentLocation = this.props.location.pathname;
                const {
                  dateSelector: ignore1,
                  minDate: ignore2,
                  maxDate: ignore3,
                  ...queryObject
                } = this.props.location.query;
                const query = queryString.stringify(queryObject);
                if (query) {
                  this.props.router.push(currentLocation + "?" + query);
                } else {
                  this.props.router.push(currentLocation);
                }
              }
            : null
        }
      >
        <TimeRangeSelector />
      </OwnPanel>
    );
  }

  render() {
    const { facets, selectedFacets } = this.props.databrowser;
    if (this.props.error) {
      return (
        <Container>
          <Alert variant="danger">
            <div className="fs-4">{this.props.error}</div>
          </Alert>
        </Container>
      );
    }
    // Wait until facets are loaded
    if (!facets) {
      return <Spinner />;
    }

    const facetPanels = this.renderFacetPanels();
    const isFacetCentered = this.state.viewPort === ViewTypes.FACET_CENTERED;
    return (
      <Container>
        <Row>
          <FacetDropdown
            clickFacet={this.clickFacet}
            dropFacet={this.dropFacet}
          />
          <div className="d-flex justify-content-between">
            <h2>
              Data-Browser&nbsp;
              {this.props.databrowser.facetLoading && (
                <Spinner outerClassName="d-inline fs-6 align-bottom" />
              )}
            </h2>
            <div>
              <OverlayTrigger
                overlay={<Tooltip>Change view with results in focus</Tooltip>}
              >
                <Button
                  className="me-1"
                  variant="outline-secondary"
                  active={!isFacetCentered}
                  onClick={() =>
                    this.setState({ viewPort: ViewTypes.RESULT_CENTERED })
                  }
                >
                  <FaList />
                </Button>
              </OverlayTrigger>
              <OverlayTrigger
                overlay={<Tooltip>Change view with facets in focus</Tooltip>}
              >
                <Button
                  variant="outline-secondary"
                  active={isFacetCentered}
                  onClick={() =>
                    this.setState({ viewPort: ViewTypes.FACET_CENTERED })
                  }
                >
                  <FaAlignJustify />
                </Button>
              </OverlayTrigger>
            </div>
          </div>

          <Col md={isFacetCentered ? 12 : 4}>
            {isFacetCentered && <DataBrowserCommand className="mb-3" />}
            {Object.keys(selectedFacets).length !== 0 ? (
              <Col md={12}>
                <Card className="shadow-sm mb-3">
                  <a
                    className="m-3"
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      this.props.router.push(this.props.location.pathname);
                    }}
                  >
                    Clear all
                  </a>
                </Card>
              </Col>
            ) : null}
            {facetPanels}
            {this.renderTimeSelectionPanel()}
          </Col>
          <Col md={isFacetCentered ? 12 : 8}>
            {!isFacetCentered && <DataBrowserCommand />}
            <FilesPanel />
          </Col>
        </Row>
      </Container>
    );
  }
}

Databrowser.propTypes = {
  databrowser: PropTypes.shape({
    facets: PropTypes.object,
    files: PropTypes.array,
    fileLoading: PropTypes.bool,
    facetLoading: PropTypes.bool,
    numFiles: PropTypes.number,
    selectedFacets: PropTypes.object,
    ncdumpStatus: PropTypes.string,
    ncdumpOutput: PropTypes.string,
    ncdumpError: PropTypes.string,
    metadata: PropTypes.object,
    dateSelector: PropTypes.string,
    minDate: PropTypes.string,
    maxDate: PropTypes.string,
  }),
  location: PropTypes.object.isRequired,
  router: PropTypes.object.isRequired,
  error: PropTypes.string,
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  databrowser: state.databrowserReducer,
  error: state.appReducer.error,
});

export default withRouter(connect(mapStateToProps)(Databrowser));
