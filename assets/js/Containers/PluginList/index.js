import React from "react";
import PropTypes from "prop-types";
import { browserHistory } from "react-router";
import { connect } from "react-redux";
import { FaTimes } from "react-icons/fa";
import {
  Row,
  Col,
  Button,
  ListGroup,
  ListGroupItem,
  Container,
  Modal,
  ButtonGroup,
  FormCheck,
  FormGroup,
  FormLabel,
  FormControl,
  InputGroup,
  Alert,
  Badge,
} from "react-bootstrap";

import _ from "lodash";

import FileTree from "../../Components/FileTree";
import {
  fetchDir,
  closeDir,
  changeRoot,
} from "../../Components/FileTree/actions";

import Spinner from "../../Components/Spinner";

import { initCap } from "../../utils";

import {
  exportPlugin,
  loadPlugins,
  updateCategoryFilter,
  updateTagFilter,
  updateSearchFilter,
} from "./actions";

class PluginList extends React.Component {
  constructor(props) {
    super(props);
    this.handleExport = this.handleImport.bind(this);
    this.handleSearchFilter = this.handleSearchFilter.bind(this);
    this.handlePluginValue = this.handlePluginValue.bind(this);
    this.renderCategoryCheckbox = this.renderCategoryCheckbox.bind(this);

    this.state = {
      showModal: false,
      value: "",
    };
  }

  componentDidMount() {
    this.props.dispatch(loadPlugins());
  }

  handleImport() {
    this.props.dispatch(exportPlugin(this.state.value));
    this.setState({ showModal: false });
  }

  handleSearchFilter(e) {
    this.props.dispatch(updateSearchFilter(e.target.value));
  }

  handlePluginValue(e) {
    this.setState({ value: e.target.value });
  }

  renderPluginBlock(filteredPlugins, category) {
    const plugins = filteredPlugins.filter((val) => {
      return (
        val[1].category.toLowerCase().trim() === category.toLowerCase().trim()
      );
    });

    if (plugins.length <= 0) {
      return null;
    }
    return (
      <ListGroup className="mb-3 card" key={category + "plugins"}>
        <div className="card-header">
          <h3 className="mb-0">{initCap(category)}</h3>
        </div>
        {plugins.map((val) => {
          return (
            <ListGroupItem
              className="shadow-sm card-body border-0 border-bottom"
              action
              onClick={(e) => {
                e.preventDefault();
                browserHistory.push(`/plugins/${val[0]}/detail/`);
              }}
              href={`/plugins/${val[0]}/detail/`}
              key={val[0]}
            >
              <div className="fs-5">{val[1].name}</div>
              {val[1].user_exported ? (
                <span className="text-danger">
                  You have plugged in this tool.
                  <br />
                </span>
              ) : null}
              {val[1].description}
            </ListGroupItem>
          );
        })}
      </ListGroup>
    );
  }

  renderCategoryCheckbox(categories, categoriesFilter, categoryName) {
    if (!categories[categoryName]) {
      return null;
    }

    return (
      <FormCheck
        className="d-flex justify-content-between"
        key={categoryName + "checkbox"}
      >
        <span>
          <FormCheck.Input
            className="me-2"
            type="checkbox"
            onChange={() =>
              this.props.dispatch(updateCategoryFilter(categoryName))
            }
            checked={_.includes(categoriesFilter, categoryName)}
            id={categoryName + "-cat"}
          />
          <FormCheck.Label htmlFor={categoryName + "-cat"}>
            {initCap(categoryName)}
          </FormCheck.Label>
        </span>
        <div>
          <Badge bg="secondary">{categories[categoryName].length}</Badge>
        </div>
      </FormCheck>
    );
  }

  render() {
    const {
      exported,
      tags,
      categories,
      categoriesFilter,
      tagsFilter,
      filteredPlugins,
      searchFilter,
      pluginsLoaded,
    } = this.props.pluginList;

    const { nodes, root, error } = this.props.fileTree;
    const { currentUser, dispatch } = this.props;
    let children;
    if (nodes && nodes.length > 0) {
      children = nodes.map((n) => {
        return (
          <FileTree
            node={n}
            key={n.name}
            extension="py"
            handleOpen={(e, path) => {
              e.preventDefault();
              this.props.dispatch(fetchDir(path, "py"));
            }}
            handleClose={(e, path) => {
              e.preventDefault();
              this.props.dispatch(closeDir(path));
            }}
            handleFileClick={(e, path) => {
              e.preventDefault();
              this.setState({ value: path });
            }}
          />
        );
      });
    } else if (error) {
      children = <div className="text-danger">{error}</div>;
    }

    if (
      (!pluginsLoaded && !this.props.pluginList.errorMessage) ||
      !currentUser
    ) {
      return <Spinner />;
    }
    if (this.props.pluginList.errorMessage) {
      return (
        <Container>
          <Alert variant="danger">
            <div className="fs-4">{this.props.pluginList.errorMessage}</div>
          </Alert>
        </Container>
      );
    }
    const defaultSelection = { id: "scratch", path: currentUser.scratch };

    return (
      <Container>
        <Row className="mb-3">
          <Col md={6}>
            <h2>Plugins</h2>
          </Col>
          <Col md={6} className="pt-2">
            <Button
              variant="info"
              className="float-end"
              onClick={() => {
                return exported
                  ? this.props.dispatch(exportPlugin())
                  : this.setState({ showModal: true });
              }}
            >
              {exported ? "Remove imported Plugin" : "Plug-my-Plugin"}
            </Button>
          </Col>
        </Row>

        <Row>
          <Col md={8}>
            {Object.keys(categories).map((key) => {
              return this.renderPluginBlock(filteredPlugins, key);
            })}
          </Col>

          <Col md={4}>
            <InputGroup className="mb-2 pb-2">
              <FormControl
                type="text"
                value={searchFilter}
                onChange={this.handleSearchFilter}
                placeholder="Search for plugins"
              />
            </InputGroup>

            <div className="mb-2 pb-2 border-bottom">
              <FormLabel className="d-flex justify-content-between">
                Categories
                {categoriesFilter.length > 0 && (
                  <span>
                    <Button
                      className="p-0 link-danger d-flex align-items-center"
                      variant="link"
                      onClick={() =>
                        this.props.dispatch(updateCategoryFilter(null))
                      }
                    >
                      <FaTimes />
                    </Button>
                  </span>
                )}
              </FormLabel>
              <div>
                {Object.keys(categories).map((key) => {
                  return this.renderCategoryCheckbox(
                    categories,
                    categoriesFilter,
                    key
                  );
                })}
              </div>
            </div>
            <div>
              <FormLabel className="d-flex justify-content-between">
                Tags
                {tagsFilter.length > 0 && (
                  <span>
                    <Button
                      className="p-0 link-danger d-flex align-items-center"
                      variant="link"
                      onClick={() => this.props.dispatch(updateTagFilter(null))}
                    >
                      <FaTimes />
                    </Button>
                  </span>
                )}
              </FormLabel>
              <div className="d-flex flex-wrap justify-content-between">
                {tags.map((tag) => {
                  const variant = _.includes(tagsFilter, tag)
                    ? "success"
                    : "secondary";
                  const disabled = !filteredPlugins.some((x) => {
                    return _.includes(x[1].tags, tag);
                  });
                  return (
                    <Button
                      className={
                        "badge mb-2 me-2 " +
                        (variant === "success" && disabled
                          ? "btn-success-muted"
                          : "")
                      }
                      variant={variant}
                      key={tag}
                      disabled={disabled && variant !== "success"}
                      onClick={() => dispatch(updateTagFilter(tag))}
                    >
                      {tag}
                    </Button>
                  );
                })}
              </div>
            </div>
          </Col>
        </Row>

        <Modal
          show={this.state.showModal}
          onShow={() => this.props.dispatch(changeRoot(defaultSelection, "py"))}
          onHide={() => this.setState({ showModal: false })}
        >
          <Modal.Header closeButton>
            <Modal.Title>Plug-in your own plugin</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>Here you can plugin your own plugin</p>
            <ButtonGroup className="mb-2">
              {currentUser.scratch && (
                <Button
                  variant="primary"
                  active={root.id === "scratch"}
                  onClick={() =>
                    this.props.dispatch(
                      changeRoot(
                        { id: "scratch", path: currentUser.scratch },
                        "py"
                      )
                    )
                  }
                >
                  Workspace
                </Button>
              )}
            </ButtonGroup>
            {children}
            <FormGroup style={{ marginTop: 10 }}>
              <FormLabel>File to plugin</FormLabel>
              <FormControl
                type="text"
                value={this.state.value}
                onChange={this.handlePluginValue}
              />
            </FormGroup>
          </Modal.Body>

          <Modal.Footer>
            <Button variant="primary" onClick={() => this.handleExport()}>
              Import Plugin
            </Button>
          </Modal.Footer>
        </Modal>
      </Container>
    );
  }
}

PluginList.propTypes = {
  pluginList: PropTypes.shape({
    exported: PropTypes.bool,
    tags: PropTypes.array,
    categories: PropTypes.object,
    categoriesFilter: PropTypes.array,
    tagsFilter: PropTypes.array,
    filteredPlugins: PropTypes.array,
    searchFilter: PropTypes.string,
    pluginsLoaded: PropTypes.bool,
    errorMessage: PropTypes.string,
  }),
  fileTree: PropTypes.shape({
    nodes: PropTypes.array,
    root: PropTypes.shape({
      id: PropTypes.string,
    }),
    error: PropTypes.string,
  }),
  currentUser: PropTypes.shape({
    id: PropTypes.number,
    username: PropTypes.string,
    email: PropTypes.string,
    scratch: PropTypes.string,
  }),
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  pluginList: state.pluginListReducer,
  fileTree: state.fileTreeReducer,
  currentUser: state.appReducer.currentUser,
});

export default connect(mapStateToProps)(PluginList);
