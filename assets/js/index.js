import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";

import { Router, Route, browserHistory } from "react-router";
import { syncHistoryWithStore } from "react-router-redux";

import configureStore from "./configureStore";

// Import containers
import App from "./Containers/App";
import PluginList from "./Containers/PluginList";
import PluginDetail from "./Containers/PluginDetail";
import Databrowser from "./Containers/Databrowser";
import Resultbrowser from "./Containers/Resultbrowser";

const initialState = window.INITIAL_STATE || {};

const store = configureStore(initialState);

// Create an enhanced history that syncs navigation events with the store
const history = syncHistoryWithStore(browserHistory, store);

ReactDOM.render(
  <Provider store={store}>
    <Router history={history} onUpdate={() => window.scrollTo(0, 0)}>
      <Route path="/" component={App}>
        <Route path="plugins/" component={PluginList} />
        <Route path="history/result-browser/" component={Resultbrowser} />
        <Route path="solr/data-browser/" component={Databrowser} />
        <Route path="plugins/:pluginName/detail/" component={PluginDetail} />
      </Route>
    </Router>
  </Provider>
  ,
  document.getElementById("react-app")
);
