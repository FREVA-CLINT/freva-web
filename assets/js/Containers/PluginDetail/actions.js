import * as constants from './constants'
import fetch from 'isomorphic-fetch'
import {getCookie} from '../../utils'

export const resetPlugin = () => {
    return {
        type: constants.RESET_PLUGIN
    }
};

export const loadPlugin = pluginName => dispatch => {
    let url = `/api/plugins/${pluginName}/`;
    return fetch(url, {
        credentials: 'same-origin',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        })
        .then(response => response.json())
        .then(json => {
            dispatch({
                type: constants.LOAD_PLUGIN,
                payload: json
            });
            return json;
        })
        .then(json => dispatch(loadPlugins()))
};

export const sendDeveloperMail = (text, tool_name) => dispatch => {
    let url = `/api/utils/mail-to-developer/`;
    return fetch(url, {
        credentials: 'same-origin',
        method: 'POST',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text,
            tool_name
        })
    })
};
