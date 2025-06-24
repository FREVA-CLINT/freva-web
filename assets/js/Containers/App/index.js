import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import { Alert } from "react-bootstrap";

import Spinner from "../../Components/Spinner";

import { getCurrentUser } from "./actions";

class App extends React.Component {
  componentDidMount() {
    this.props.dispatch(getCurrentUser());
  }

  render() {
    // Wait until the current user is loaded
    if (!this.props.currentUser && this.props.error === "") {
      return <Spinner />;
    }
    if (this.props.error) {
      return (
        <div className="container">
          <Alert variant="danger">{this.props.error}</Alert>
        </div>
      );
    }

    return <React.Fragment>{this.props.children}</React.Fragment>;
  }
}

App.propTypes = {
  children: PropTypes.node.isRequired,
  currentUser: PropTypes.shape({
    id: PropTypes.number,
    username: PropTypes.string,
    email: PropTypes.string,
    first_name: PropTypes.string,
    scratch: PropTypes.string,
  }),
  error: PropTypes.string,
  dispatch: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  currentUser: state.appReducer.currentUser,
  error: state.appReducer.error,
});

export default connect(mapStateToProps)(App);
