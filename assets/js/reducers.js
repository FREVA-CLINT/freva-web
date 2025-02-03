import { combineReducers } from "redux";

import { appReducer } from "./Containers/App/reducers";
import { pluginListReducer } from "./Containers/PluginList/reducers";
import { fileTreeReducer } from "./Components/FileTree/reducers";
import { pluginDetailReducer } from "./Containers/PluginDetail/reducers";
import { databrowserReducer } from "./Containers/Databrowser/reducers";
import { resultbrowserReducer } from "./Containers/Resultbrowser/reducers";
import { frevaGPTReducer } from "./Containers/FrevaGPT/reducers";

const rootReducer = combineReducers({
  appReducer,
  pluginListReducer,
  fileTreeReducer,
  pluginDetailReducer,
  databrowserReducer,
  resultbrowserReducer,
  frevaGPTReducer,
});

export default rootReducer;
