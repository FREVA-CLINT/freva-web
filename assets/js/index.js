import React from 'react';
import ReactDOM from 'react-dom';
import {Provider} from 'react-redux'
import {createStore, applyMiddleware} from 'redux';
import configureStore from './configureStore'
import {Router, Route, browserHistory} from 'react-router'
import {syncHistoryWithStore, routerReducer} from 'react-router-redux'

// Import containers
import App from './Containers/App'
import PluginList from './Containers/PluginList';
import PluginDetail from './Containers/PluginDetail';
import Databrowser from './Containers/Databrowser';
//import Resultbrowser from './Containers/Resultbrowser';
//import HindcastFrontend from './Containers/HindcastFrontend';

const initialState = window.INITIAL_STATE || {};

const store = configureStore(initialState);


// Create an enhanced history that syncs navigation events with the store
const history = syncHistoryWithStore(browserHistory, store)


ReactDOM.render(
   <Provider store={store}>
        { /* Tell the Router to use our enhanced history */ }
        <Router history={history} onUpdate={() => window.scrollTo(0, 0)}>
            <Route path="/" component={App}>
                <Route path="plugins/" component={PluginList}/>
                <Route path="plugins/:pluginName/detail/" component={PluginDetail}/>
                <Route path="solr/data-browser/" component={Databrowser}/>
                <Route path="history/result-browser/" component={Resultbrowser}/>
                <Route path="hindcast-frontend/" component={HindcastFrontend} />
            </Route>
        </Router>
    </Provider>,
    document.getElementById('react-app')
);
