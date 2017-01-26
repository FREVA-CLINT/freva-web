import { combineReducers } from 'redux'
import {appReducer} from './Containers/App/reducers'
import {routerReducer} from 'react-router-redux'
import {pluginListReducer} from './Containers/PluginList/reducers'

const rootReducer = combineReducers({
    appReducer,
    pluginListReducer,
    routing: routerReducer
});

export default rootReducer;