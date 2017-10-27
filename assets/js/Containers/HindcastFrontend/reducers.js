import * as constants from './constants';
import dummyData from '../../data/testmap.json'
import { combineReducers } from 'redux'
import _ from 'lodash'

const selectMenuInitialState = {
    variable: {},
    metric: {},
    hindcastSet: {},
    reference: {},
    region: {},
    leadtime: {selected: 1}
}

const isLoadingOption = [
    {value: null, label: 'Loading...', disabled: true}
];

const selectMenuReducer = (state = selectMenuInitialState, action) => {
    let newState;
    switch (action.type) {

        case constants.CHANGE_PARAM:
            newState = {...state};
            _.map(action.params, (value, key) => {
                newState[key] = {...newState[key], selected: value}
            });
            return newState;
        case 'LOAD_OPTIONS_SUCCESS':
            newState = {...state};
            newState[action.facet] = {...newState[action.facet], options: action.json, isLoading: false};
            return newState;
        case 'LOAD_OPTIONS':
            newState = {...state};
            newState[action.facet] = {...newState[action.facet], options: isLoadingOption, isLoading: true};
            return newState;
        default:
            return state
    }
};

const hindcastFrontendInitialState = {
    mapData: dummyData,
    timeseriesData: {},
    cache: {}
};

const settingsReducer = (state = hindcastFrontendInitialState, action) => {
    switch (action.type) {
        case constants.CHANGE_PARAM:
            const newState = {...state};
                newState['mapData'] = action.data[0] ? action.data[0] : dummyData;
                newState['timeseriesData'] = action.data[1] ? action.data[1] : {};
            return newState;
        case constants.GET_HINDCAST_DATA:
            return {...state, mapData: action.payload};
        case constants.GET_HINDCAST_TIMESERIES_DATA:
            return {...state, timeseriesData: action.payload};
        case constants.CACHE_DATA:
            const cache = {...state.cache};
            cache[action.key] = action.data;
            return {...state, cache};
        default:
            return state
    }
};


export const hindcastFrontendReducer = combineReducers({
    settingsReducer,
    selectMenuReducer
});
