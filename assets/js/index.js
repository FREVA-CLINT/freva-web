import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux'
import {createStore, applyMiddleware} from 'redux';
import configureStore from './configureStore'
import App from './Containers/App'


const initialState = window.INITIAL_STATE || {};

const store = configureStore(initialState);

ReactDOM.render(
    <Provider store={store}>
        <App/>
    </Provider>,
    document.getElementById('react-app')
);