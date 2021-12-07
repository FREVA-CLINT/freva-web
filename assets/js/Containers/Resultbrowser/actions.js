import * as constants from './constants'
import fetch from 'isomorphic-fetch'
import {getCookie} from '../../utils'
import _ from 'lodash';

export const selectResultFacet = (facet, value) => dispatch => {
    setTimeout(function(){
        dispatch({
            type: constants.SELECT_RESULT_FACET,
            facet,
            value
        });
        dispatch(setActiveResultFacet(facet));
        dispatch(loadResultFacets());
        dispatch(loadResultFiles());
    },50);

};

export const clearResultFacet = (facet) => dispatch => {
    dispatch({
        type: constants.CLEAR_RESULT_FACET,
        facet
    });
    dispatch(loadResultFacets());
    dispatch(loadResultFiles());
};


export const setMetadata = (metadata) => ({
    type: constants.SET_METADATA,
    metadata
});

export const clearAllResultFacets = (facet) => dispatch => {
    dispatch({
        type: constants.CLEAR_ALL_RESULT_FACETS,
        facet
    });
    dispatch(loadResultFacets());
    dispatch(loadResultFiles());
};

export const setActiveResultFacet = (facet) => ({
    type: constants.SET_ACTIVE_RESULT_FACET,
    facet
});

export const loadResultFacets = () => (dispatch, getState) => {

    const {selectedFacets} = getState().resultbrowserReducer;
    let params = '';
    _.map(selectedFacets, (value, key) => {
        params += `&${key}=${value}`
    });
    let url = `/api/history/result-browser/?${params}`;

    return fetch(url, {
        credentials: 'same-origin',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }}
        ).then(response => response.json())
        .then(json => {
            dispatch({
                type: constants.LOAD_RESULT_FACETS,
                payload: json
            });
        })
};

export const loadResultFiles = () => (dispatch, getState) => {
    const {selectedFacets, page, limit, sortName, sortOrder, searchText} = getState().resultbrowserReducer;
    let params = '';
    _.map(selectedFacets, (value, key) => {
        params += `&${key}=${value}`
    });
    let offset = (page-1)*limit;
    params +=`&limit=${limit}&offset=${offset}`;
    params +=`&sortName=${sortName}&sortOrder=${sortOrder}`;
    params +=`&searchText=${searchText}`;

    let url = `/api/history/result-browser-files/?${params}`;
    return fetch(url, {
        credentials: 'same-origin',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }}
        ).then(response => response.json())
        .then(json => {
            dispatch({
                type: constants.LOAD_RESULT_FILES,
                payload: json
            });
        })
};

export const selectActivePage = (page) => dispatch => {

    dispatch({
        type: constants.SELECT_ACTIVE_PAGE,
        page
    });
    dispatch(loadResultFiles());

};
export const sortActivePage = (sortName,sortOrder) => dispatch => {

    dispatch({
        type: constants.SORT_ACTIVE_PAGE,
        sortName,
        sortOrder
    });
    dispatch(loadResultFiles());

};

export const searchInText = (searchText) => dispatch => {
    dispatch({
        type: constants.ON_SEARCH,
        searchText
    });
    dispatch(loadResultFiles());
};


