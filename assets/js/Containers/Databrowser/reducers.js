import { combineReducers } from 'redux'
import * as constants from './constants';
import _ from 'lodash';

const databrowserInitialState = {
    facets: [],
    files: [],
    numFiles: 0,
    selectedFacets: {},
    activeFacet: 'files',
    metadata: {},
    ncdumpStatus: 'pw',
    ncdumpOutput: null,
};

export const databrowserReducer = (state = databrowserInitialState, action) => {
    switch (action.type) {
        case constants.LOAD_FACETS:
            return {...state, facets: action.payload.data};
        case constants.SELECT_FACET:
            let selectedFacets = {...state.selectedFacets};
            selectedFacets[action.facet] = action.value;
            return {...state, selectedFacets};
        case constants.CLEAR_FACET:
            let newFacets = {...state.selectedFacets};
            newFacets = _.omit(newFacets, action.facet);
            return {...state, selectedFacets: newFacets};
        case constants.CLEAR_ALL_FACETS:
            return {...state, selectedFacets: {}};
        case constants.SET_ACTIVE_FACET:
            if (state.activeFacet === action.facet)
                return {...state, activeFacet: databrowserInitialState.activeFacet};
            return {...state, activeFacet: action.facet};
        case constants.SET_METADATA:
            return {...state, metadata: action.metadata};
        case constants.LOAD_FILES:
            return {...state, files: action.payload.data, numFiles: action.payload.metadata.numFound};
        case constants.LOAD_NCDUMP_ERROR:
            return {...state, ncdumpStatus: 'pw_fail'};
        case constants.LOAD_NCDUMP:
            return {...state, ncdumpStatus: 'loading'};
        case constants.LOAD_NCDUMP_SUCCESS:
            return {...state, ncdumpStatus: 'ready', ncdumpOutput: action.payload};
        case constants.RESET_NCDUMP:
            return {...state, ncdumpStatus: 'pw', ncdumpOutput: null};
        default:
            return state
    }
};