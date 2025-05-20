import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import {
  Container,
  Row,
  Col,
  Button,
  Alert,
  OverlayTrigger,
  Tooltip,
  Form,
  Collapse,
} from "react-bootstrap";
import {
  FaAlignJustify,
  FaList,
  FaMinusSquare,
  FaPlusSquare,
  FaTimes,
} from "react-icons/fa";
import queryString from "query-string";
import { withRouter } from "react-router";

import OwnPanel from "../../Components/OwnPanel";
import Spinner from "../../Components/Spinner";
import { initCap, underscoreToBlank } from "../../utils";

import {
  setMetadata,
  loadFiles,
  updateFacetSelection,
  setFlavours,
} from "./actions";
import TimeRangeSelector from "./TimeRangeSelector";
import FilesPanel from "./FilesPanel";
import DataBrowserCommand from "./DataBrowserCommand";
import FacetDropdown from "./MetaFacet";
import {
  ViewTypes,
  DEFAULT_FLAVOUR,
  STREAM_CATALOGUE_MAXIMUM,
} from "./constants";
import { FacetPanel } from "./FacetPanel";
import { prepareSearchParams } from "./utils";
import CatalogExportDropdown from "./CatalogExportDropdown";
import BBoxSelector from "./BBoxSelector";

class Databrowser extends React.Component {
  constructor(props) {
    super(props);
    this.clickFacet = this.clickFacet.bind(this);
    this.renderFacetBadges = this.renderFacetBadges.bind(this);
    this.createCatalogLink = this.createCatalogLink.bind(this);
    const firstViewPort =
      localStorage.FrevaDatabrowserViewPort ?? ViewTypes.RESULT_CENTERED;
    localStorage.FrevaDatabrowserViewPort = firstViewPort;
    this.state = {
      viewPort: firstViewPort,
      additionalFacetsVisible: false,
    };
  }

  /**
   * On mount we load all facets and files to display
   * Also load the metadata.js script
   */
  componentDidMount() {
    this.props.dispatch(setFlavours());
    this.props.dispatch(loadFiles(this.props.location));
    this.props.dispatch(updateFacetSelection(this.props.location.query));
    const script = document.createElement("script");
    script.src = "/static/js/metadata.js";
    script.async = true;
    script.onload = () =>
      this.props.dispatch(
        setMetadata({
          project: window.project,
          product: window.product,
          model: window.model,
          institute: window.institute,
          time_frequency: window.time_frequency,
          realm: window.realm,
          variable: window.variable,
          grid_label: window.grid_label,
          time_aggregation: window.time_aggregation,
          fs_type: window.fs_type,
          cmor_table: window.cmor_table,
        })
      );
    document.body.appendChild(script);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.location.search !== this.props.location.search) {
      this.props.dispatch(loadFiles(this.props.location));
      this.props.dispatch(updateFacetSelection(this.props.location.query));
    }
  }

  createCatalogLink(type) {
    const baseUrl = `/api/freva-nextgen/databrowser/${type}-catalogue/`;
    const searchParams = prepareSearchParams(
      this.props.location,
      "translate=false"
    );
    return `${baseUrl}${searchParams}`;
  }

  clickFacet(category, value = null) {
    const currentLocation = this.props.location.pathname;
    const originalQueryObject = this.props.location.query;
    const previousValue = originalQueryObject[category];
    if (previousValue && (value === null || value === previousValue)) {
      // delete
      const { [category]: toRemove, ...queryObject } =
        this.props.location.query;
      const query = queryString.stringify({ ...queryObject, start: 0 });
      this.props.router.push(currentLocation + "?" + query);
      return;
    }
    const query = queryString.stringify({
      ...this.props.location.query,
      [category]: value,
      start: 0,
    });
    if (query) {
      this.props.router.push(currentLocation + "?" + query);
    } else {
      this.props.router.push(currentLocation);
    }
  }

  clickFlavour(value = DEFAULT_FLAVOUR) {
    const currentLocation = this.props.location.pathname;
    const query = queryString.stringify({
      ...this.props.location.query,
      flavour: value,
    });
    if (query) {
      this.props.router.push(currentLocation + "?" + query);
    } else {
      this.props.router.push(currentLocation);
    }
  }

  /**
   * Loop all facets and render the panels
   */
  renderFacetPanels() {
    const { facets, primaryFacets, selectedFacets, facetMapping, metadata } =
      this.props.databrowser;

    return primaryFacets.map((key) => {
      const value = facets[key];
      if (!value) {
        return undefined;
      }

      return (
        <FacetPanel
          value={value}
          key={key}
          keyVar={key}
          metadata={metadata}
          selectedFacets={selectedFacets}
          facetMapping={facetMapping}
          clickFacet={this.clickFacet}
          isFacetCentered={this.state.viewPort === ViewTypes.FACET_CENTERED}
        />
      );
    });
  }

  renderAdditionalFacets() {
    const { facets, primaryFacets, selectedFacets, facetMapping, metadata } =
      this.props.databrowser;
    const primaryFacetsSet = new Set(primaryFacets);

    return Object.keys(facetMapping)
      .filter((x) => {
        return !primaryFacetsSet.has(x);
      })
      .map((key) => {
        const value = facets[key];
        if (!value) {
          return undefined;
        }

        return (
          <FacetPanel
            value={value}
            key={key}
            keyVar={key}
            metadata={metadata}
            selectedFacets={selectedFacets}
            facetMapping={facetMapping}
            clickFacet={this.clickFacet}
            isFacetCentered={this.state.viewPort === ViewTypes.FACET_CENTERED}
          />
        );
      });
  }
  dropBBoxSelection() {
    const currentLocation = this.props.location.pathname;
    const {
      bboxSelector: ignore1,
      minLon: ignore2,
      maxLon: ignore3,
      minLat: ignore4,
      maxLat: ignore5,
      ...queryObject
    } = this.props.location.query;
    const query = queryString.stringify(queryObject);
    if (query) {
      this.props.router.push(currentLocation + "?" + query);
    } else {
      this.props.router.push(currentLocation);
    }
  }

  renderBBoxPanel() {
    const { databrowser } = this.props;
    const { minLon, maxLon, minLat, maxLat } = databrowser;
    const isBBoxSelected = !!(minLon || maxLon || minLat || maxLat);
    const title = isBBoxSelected ? (
      <span>
        BBox: &nbsp;
        <span className="fw-bold">
          {minLon},{maxLon} by {minLat},{maxLat}
        </span>
      </span>
    ) : (
      <span>Bounding Box</span>
    );

    return (
      <OwnPanel
        header={title}
        key="bbox_range"
        removeFacet={isBBoxSelected ? () => this.dropBBoxSelection() : null}
      >
        <BBoxSelector />
      </OwnPanel>
    );
  }

  dropTimeSelection() {
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

  renderTimeSelectionPanel() {
    const { dateSelector, minDate, maxDate } = this.props.databrowser;
    const isDateSelected = !!minDate;
    const title = isDateSelected ? (
      <span>
        Time : &nbsp;
        <span className="fw-bold">
          {dateSelector}: {minDate} to {maxDate}
        </span>
      </span>
    ) : (
      <span>Time</span>
    );
    return (
      <OwnPanel
        header={title}
        key="time_range"
        removeFacet={isDateSelected ? () => this.dropTimeSelection() : null}
      >
        <TimeRangeSelector />
      </OwnPanel>
    );
  }

  renderFacetBadges() {
    const { dateSelector, minDate, maxDate } = this.props.databrowser;
    const isDateSelected = !!minDate;
    const isBBoxSelected = !!(
      this.props.databrowser.minLon ||
      this.props.databrowser.maxLon ||
      this.props.databrowser.minLat ||
      this.props.databrowser.maxLat
    );
    let values = [];
    if (
      Object.keys(this.props.databrowser.selectedFacets).length > 0 ||
      isDateSelected ||
      isBBoxSelected
    ) {
      values.push(
        <Button
          variant="danger"
          className="me-2 mb-2 badge d-flex align-items-center"
          onClick={(e) => {
            e.preventDefault();
            this.props.router.push(this.props.location.pathname);
          }}
          key={"clearall"}
        >
          Clear all
          <FaTimes className="ms-2 fs-6" />
        </Button>
      );
    }
    if (
      this.props.databrowser.minLon ||
      this.props.databrowser.maxLon ||
      this.props.databrowser.minLat ||
      this.props.databrowser.maxLat
    ) {
      const bboxBadge = (
        <Button
          variant="secondary"
          className="me-2 mb-2 badge d-flex align-items-center"
          onClick={() => this.dropBBoxSelection()}
          key={"bbox-selection"}
        >
          BBox ({this.props.databrowser.bboxSelector}):{" "}
          {this.props.databrowser.minLon},{this.props.databrowser.maxLon} by{" "}
          {this.props.databrowser.minLat},{this.props.databrowser.maxLat}
          <FaTimes className="ms-2 fs-6" />
        </Button>
      );
      values.push(bboxBadge);
    }
    values = [
      ...values,
      ...Object.keys(this.props.databrowser.selectedFacets).map((x) => {
        return (
          <Button
            variant="secondary"
            className="me-2 mb-2 badge d-flex align-items-center"
            onClick={() => {
              this.clickFacet(x);
            }}
            key={"selected-" + x + this.props.databrowser.selectedFacets[x]}
          >
            {initCap(underscoreToBlank(this.props.databrowser.facetMapping[x]))}
            : {this.props.databrowser.selectedFacets[x]}
            <FaTimes className="ms-2 fs-6" />
          </Button>
        );
      }),
    ];

    if (isDateSelected) {
      const timeBadge = (
        <Button
          variant="secondary"
          className="me-2 mb-2 badge d-flex align-items-center"
          onClick={() => this.dropTimeSelection()}
          key={"time-selection" + { dateSelector } + { minDate } + { maxDate }}
        >
          Time: {minDate} to {maxDate} ({dateSelector})
          <FaTimes className="ms-2 fs-6" />
        </Button>
      );
      values.push(timeBadge);
    }

    return (
      <div className="d-flex justify-content-between flex-after flex-wrap my-2">
        {values}
      </div>
    );
  }

  render() {
    const { facets } = this.props.databrowser;
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
    const additionalFacetPanels = this.renderAdditionalFacets();
    const isFacetCentered = this.state.viewPort === ViewTypes.FACET_CENTERED;
    const flavour = this.props.location.query.flavour;

    return (
      <Container>
        <Row>
          <div className="d-flex justify-content-between">
            <h2>
              Data-Browser&nbsp;
              {this.props.databrowser.facetLoading && (
                <Spinner outerClassName="d-inline fs-6 align-bottom" />
              )}
            </h2>
            <div className="d-flex justify-content-between mb-2">
              <Form.Select
                aria-label="Default select example"
                className="me-1"
                value={flavour}
                onChange={(x) => {
                  this.clickFlavour(x.target.value);
                }}
              >
                {this.props.databrowser.flavours.map((x) => {
                  return <option key={x}>{x}</option>;
                })}
              </Form.Select>

              <CatalogExportDropdown
                disabled={
                  this.props.databrowser.numFiles > STREAM_CATALOGUE_MAXIMUM
                }
                createCatalogLink={this.createCatalogLink}
                numFiles={this.props.databrowser.numFiles}
                maxFiles={STREAM_CATALOGUE_MAXIMUM}
                className="me-1"
              />

              <OverlayTrigger
                overlay={<Tooltip>Change view with facets in focus</Tooltip>}
              >
                <Button
                  className="me-1"
                  variant="outline-secondary"
                  active={isFacetCentered}
                  onClick={() =>
                    this.setState(
                      { viewPort: ViewTypes.FACET_CENTERED },
                      () => {
                        localStorage.FrevaDatabrowserViewPort =
                          this.state.viewPort;
                      }
                    )
                  }
                >
                  <FaAlignJustify />
                </Button>
              </OverlayTrigger>
              <OverlayTrigger
                overlay={<Tooltip>Change view with results in focus</Tooltip>}
              >
                <Button
                  variant="outline-secondary"
                  active={!isFacetCentered}
                  onClick={() =>
                    this.setState(
                      { viewPort: ViewTypes.RESULT_CENTERED },
                      () => {
                        localStorage.FrevaDatabrowserViewPort =
                          this.state.viewPort;
                      }
                    )
                  }
                >
                  <FaList />
                </Button>
              </OverlayTrigger>
            </div>
          </div>

          <Col md={isFacetCentered ? 12 : 4}>
            <div className={"shadow-sm " + (isFacetCentered ? "mb-2" : "mb-3")}>
              <FacetDropdown clickFacet={this.clickFacet} />
            </div>
            {isFacetCentered && this.renderFacetBadges()}

            {facetPanels}
            {this.renderTimeSelectionPanel()}
            {this.renderBBoxPanel()}
            <Button
              className="w-100 mb-3 shadow-sm p-3"
              variant="secondary"
              onClick={() =>
                this.setState({
                  additionalFacetsVisible: !this.state.additionalFacetsVisible,
                })
              }
              aria-expanded={this.state.additionalFacetsVisible}
            >
              {this.state.additionalFacetsVisible ? (
                <div className="d-flex justify-content-between">
                  <span>Hide additional facets</span>
                  <span className="d-flex align-items-center">
                    <FaMinusSquare className="fs-5" />
                  </span>
                </div>
              ) : (
                <div className="d-flex justify-content-between">
                  <span>Show additional facets</span>
                  <span className="d-flex align-items-center">
                    <FaPlusSquare className="fs-5" />
                  </span>
                </div>
              )}
            </Button>
            <Collapse in={this.state.additionalFacetsVisible}>
              <div>{additionalFacetPanels}</div>
            </Collapse>
          </Col>
          <Col md={isFacetCentered ? 12 : 8}>
            <DataBrowserCommand className={isFacetCentered ? "mb-3" : ""} />
            {!isFacetCentered && this.renderFacetBadges()}
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
    flavours: PropTypes.array,
    fileLoading: PropTypes.bool,
    facetLoading: PropTypes.bool,
    facetMapping: PropTypes.object,
    numFiles: PropTypes.number,
    selectedFacets: PropTypes.object,
    primaryFacets: PropTypes.array,
    metadata: PropTypes.object,
    dateSelector: PropTypes.string,
    minDate: PropTypes.string,
    maxDate: PropTypes.string,
    minLon: PropTypes.string,
    maxLon: PropTypes.string,
    minLat: PropTypes.string,
    maxLat: PropTypes.string,
    bboxSelector: PropTypes.string,
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
