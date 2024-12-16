import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";

import { Router, Route, browserHistory } from "react-router";

import configureStore from "./configureStore";

// Import containers
import App from "./Containers/App";
import PluginList from "./Containers/PluginList";
import PluginDetail from "./Containers/PluginDetail";
import Databrowser from "./Containers/Databrowser";
import Resultbrowser from "./Containers/Resultbrowser";
import FrevaGTP from "./Containers/FrevaGPT";

const initialState = window.INITIAL_STATE || {};

const store = configureStore(initialState);

ReactDOM.render(
  <Provider store={store}>
    <Router history={browserHistory}>
      <Route path="/" component={App}>
        <Route path="plugins/" component={PluginList} />
        <Route path="chatbot/" component={FrevaGTP} />
        <Route path="history/result-browser/" component={Resultbrowser} />
        <Route path="databrowser/*" component={Databrowser} />
        <Route path="plugins/:pluginName/detail/" component={PluginDetail} />
      </Route>
    </Router>
  </Provider>,
  document.getElementById("react-app")
);
