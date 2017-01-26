import React from 'react';
import {connect} from 'react-redux';

class PluginList extends React.Component {

  render() {
    return <h1>Plugin List Component</h1>
  }
}

const mapStateToProps = state => ({
    state: state
});

export default connect(mapStateToProps)(PluginList);