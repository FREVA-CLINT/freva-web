import { combineReducers } from 'redux'
import {appReducer} from './Containers/App/reducers'

const rootReducer = combineReducers({
    appReducer
});

export default rootReducer;