import {createStore, applyMiddleware} from 'redux';
import reducer from './reducers'
import thunk from 'redux-thunk';
import createLogger from 'redux-logger';

const middleware =[thunk];

if (process.env.NODE_ENV !== 'production') {
    middleware.push(createLogger())
}

export default function configureStore(initialState) {
  const store = createStore(
      reducer,
      initialState,
      applyMiddleware(...middleware)
  );

  if (module.hot) {
    // Enable Webpack hot module replacement for reducers
    module.hot.accept('./reducers', () => {
      const nextRootReducer = require('./reducers');
      store.replaceReducer(nextRootReducer);
    });
  }

  return store;
}
