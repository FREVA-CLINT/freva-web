import { combineReducers } from 'redux'

import {appReducer} from './Containers/App/reducers'
import {routerReducer} from 'react-router-redux'
import {pluginListReducer} from './Containers/PluginList/reducers'
import {fileTreeReducer} from './Components/FileTree/reducers'
import {pluginDetailReducer} from './Containers/PluginDetail/reducers'
import {databrowserReducer} from './Containers/Databrowser/reducers'

const rootReducer = combineReducers({
    appReducer,
    pluginListReducer,
    fileTreeReducer,
    pluginDetailReducer,
    databrowserReducer,
    routing: routerReducer
});

export default rootReducer;