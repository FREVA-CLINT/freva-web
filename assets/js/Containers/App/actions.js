import * as constants from './constants';

export const appStartup = () => {
    type: constants.APP_STARTUP
};

export const getCurrentUser = () => (dispatch) => {
    let url = `/api/users/active/`;
    return fetch(url, {
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        })
        .then(response => response.json())
        .then(json => dispatch({
            type: constants.GET_CURRENT_USER_SUCCESS,
            payload: json
        }))
}
