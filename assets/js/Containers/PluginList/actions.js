import * as constants from './constants';
import fetch from 'isomorphic-fetch'

export const exportPlugin = (path) => (dispatch) => {
    let url = `/plugins/api/export-plugin/?export_file=${path}`;
    return fetch(url)
        .then(response => response.json())
        .then(json => {
            dispatch({
                type: constants.EXPORT_PLUGIN
            });
            return json;
        })
        .then(json => dispatch(loadPlugins()))
};

export const loadPlugins = () => (dispatch) => {

    let url = `/plugins/api/plugin-list/`;
    return fetch(url)
        .then(response => response.json())
        .then(json => dispatch({
            type: constants.LOAD_PLUGINS,
            payload: json
        }))
};