import * as constants from './constants';
import dummyData from '../../data/testmap.json'
import { combineReducers } from 'redux'
import _ from 'lodash'

/*// Hardcoded options for select fields
export const variableOptions = [
    {value: 'pr', label: 'Precipitation (pr)'},
    {value: 'tas', label: 'Temperature (tas)'}
];
export const hindcastSetOptions = [
    {value: 'clim', label: 'Climatology'},
    {value: 'b1-lr', label: 'Baseline1-LR'},
    {value: 'b1-mr', label: 'Baseline1-MR'},
    {value: 'preop-lr', label: 'Preop-LR'},
    {value: 'preop-hr', label: 'Preop-HR'},
    {value: 'unini', label: 'Uninitialized'}

];
export const metricOptions = [
    {value: 'correlation', label: 'Correlation'},
    {value: 'msss', label: 'MSESS'}
];*/

const selectMenuInitialState = {
    variable: {selected: {value: 'tas', label: 'tas'}},
    metric: {selected: {value: 'msss', label: 'msess'}},
    hindcastSet: {selected: {value: 'b1-lr', label: 'b1-lr'}},
    reference: {selected: {value: 'vs_clim', label: 'vs_clim'}},
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
