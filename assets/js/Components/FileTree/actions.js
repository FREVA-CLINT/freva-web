import * as constants from './constants'
import fetch from 'isomorphic-fetch'

export const closeDir = (path) => ({
    type: constants.CLOSE_DIR,
    path: path
});

export const changeRoot = (dir, ext) => (dispatch) => {
    dispatch({
        type: constants.CHANGE_ROOT,
        root: dir
    });
    return dispatch(fetchDir(dir.path, ext))
};

export const fetchDir = (dir, ext) => (dispatch) => {
    let url = `/plugins/browse-files-new/?dir=${dir}&file_type=${ext}`;
    return fetch(url, {
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }})
        .then(response => response.json())
        .then(json => {
            dispatch({
                type: constants.FETCH_DIR_SUCCESS,
                payload: json,
                path: dir
            })
        })
};

