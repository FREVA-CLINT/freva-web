import React from 'react';
import {connect} from 'react-redux';
import {getCurrentUser} from './actions'
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import CircularProgress from 'material-ui/CircularProgress';
import {Row, Col, Button, ListGroup, ListGroupItem, Grid, Modal, ButtonGroup, Input,
    FormGroup, ControlLabel, FormControl} from 'react-bootstrap';

class App extends React.Component {
 
  componentDidMount() {
      this.props.dispatch(getCurrentUser())
  }

  render() {

    // Wait until the current user is loaded
    if (!this.props.state.appReducer.currentUser){
        return (
            <MuiThemeProvider>
                <Grid style={{textAlign: 'center'}}>
                    <CircularProgress />
                </Grid>
            </MuiThemeProvider>
        )
    }

    return (
        <MuiThemeProvider>
            {this.props.children}
        </MuiThemeProvider>
    )
  }
}

const mapStateToProps = state => ({
    state: state
});

export default connect(mapStateToProps)(App);