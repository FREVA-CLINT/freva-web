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
            <h1>App Component</h1>
            {this.props.children}
        </div>
    )
  }
}

const mapStateToProps = state => ({
    state: state
});

export default connect(mapStateToProps)(App);