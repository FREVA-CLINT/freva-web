import React from 'react';
import {connect} from 'react-redux';
import {appStartup} from './actions'

class App extends React.Component {
 
  componentDidMount() {
      this.props.dispatch(appStartup())
  }

  render() {
    return (
        <div>
            {this.props.children}
        </div>
    )
  }
}

const mapStateToProps = state => ({
    state: state
});

export default connect(mapStateToProps)(App);