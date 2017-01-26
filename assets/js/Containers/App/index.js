import React from 'react';
import {connect} from 'react-redux';
import {appStartup} from './actions'

class App extends React.Component {
 
  componentDidMount() {
      this.props.dispatch(appStartup())
  }

  render() {
    console.log(this.props)
    return <h1>Hello World</h1>
  }
}

const mapStateToProps = state => ({
    state: state
});

export default connect(mapStateToProps)(App);