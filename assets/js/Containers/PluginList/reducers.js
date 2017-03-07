import { combineReducers } from 'redux'
import * as constants from './constants';
import _ from 'lodash';

const pluginListInitialState = {
    pluginsLoaded: false,
    plugins: [],
    filteredPlugins: [],
    exported: null,
    tags: [],
    categories: [],
    categoriesFilter: [],
    tagsFilter: [],
    searchFilter: ''
};

function sortObject(o) {
    return Object.keys(o).sort().reduce((r, k) => (r[k] = o[k], r), {});
}

const createCategories = plugins => {
    let categories = {};
    plugins.map(p => {
        const newCat = p[1].category ? p[1].category : 'other';
        p[1].category = newCat;
        let cat = categories[newCat];
        if (cat) {
            cat.push(p[1].name)
        } else {
            cat = [p[1].name]
        }
        categories[newCat] = cat
    });
    return sortObject(categories)
};

const createTags = plugins => {
    let tags = [];
    plugins.map(p => {
        if (p[1].tags)
            tags = tags.concat(p[1].tags)
    });
    return _.sortBy(_.uniq(tags))
};

const filterPlugins = (plugins, categoriesFilter, tagsFilter, searchFilter) => {
    // filter for categories
    if (categoriesFilter.length > 0) {
        plugins = _.filter(plugins, (p) => {
            return _.includes(categoriesFilter, p[1].category)
        });
    }

    // filter for tags
    // tool must have ALL tags
    if (tagsFilter.length > 0) {
        plugins = _.filter(plugins, (p) => {
            for (let i=0; i<tagsFilter.length; i++) {
                if (!_.includes(p[1].tags, tagsFilter[i]))
                    return false;
            }
            return true
        })
    }

    // filter for string
    plugins = _.filter(plugins, (p) => {
        const title = _.includes(p[1].name.toLowerCase(), searchFilter.toLowerCase());
        const description = _.includes(p[1].description.toLowerCase(), searchFilter.toLowerCase());
        let tags = false
        if (p[1].tags)
            tags = _.includes(p[1].tags.join().toLowerCase(), searchFilter.toLowerCase());
        return title || description || tags
    });
    return plugins
};


export const pluginListReducer = (state = pluginListInitialState, action) => {
    switch (action.type) {
        case constants.FILTER_PLUGINS:
            let filteredPlugins = filterPlugins([...state.plugins], state.categoriesFilter, state.tagsFilter, state.searchFilter);
            return {...state, filteredPlugins, tags: createTags(filteredPlugins)};
        case constants.LOAD_PLUGINS:
            let exported = false;
            action.payload.map(v => {
                if (v[1].user_exported)
                    exported = v[1].plugin_module;
            });
            return {...state, plugins: action.payload, exported, categories: createCategories(action.payload),
                    tags: createTags(action.payload),
                    filteredPlugins: filterPlugins(action.payload, state.categoriesFilter, state.tagsFilter, state.searchFilter),
                    pluginsLoaded: true};
        case constants.UPDATE_CATEGORY_FILTER:
            let {categoriesFilter} = state;
            if (_.includes(categoriesFilter, action.category)) {
                _.pull(categoriesFilter, action.category)
            } else {
                categoriesFilter.push(action.category);
            }
            return {...state, categoriesFilter};
        case constants.UPDATE_TAG_FILTER:
            let {tagsFilter} = state;
            if (_.includes(tagsFilter, action.tag)) {
                _.pull(tagsFilter, action.tag)
            } else {
                tagsFilter.push(action.tag);
            }
            return {...state, tagsFilter};
        case constants.UPDATE_SEARCH_FILTER:
            return {...state, searchFilter: action.value};
        default:
            return state
    }
};
