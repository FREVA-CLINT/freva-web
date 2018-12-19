
import React, { Component } from 'react';
import {connect} from 'react-redux';
import {Grid, Row, Col, Accordion, Panel} from 'react-bootstrap';
import { setActiveResultFacet,loadResultPictures,loadResultFacets, loadResultFiles,
         selectActivePage, sortActivePage, searchInText,} from '../Resultbrowser/actions';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import CircularProgress from 'material-ui/CircularProgress';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';
import Gallery from '../../Components/Gallery/Gallery';
import { dateformatter } from '../../utils'

class Resulttype extends React.Component{

    constructor(props) {
        super(props);
        this.state = {
            searchtext : ''
        }
        this._searchInText = this._searchInText.bind(this)
    }

    componentDidMount()
        {
            this.props.dispatch(loadResultFacets());
            if (this.props.app.table) {
                this.props.dispatch(loadResultPictures());
            } else {
                this.props.dispatch(loadResultFiles());
            }
        }

    _searchInText(searchText) {
        this.setState({searchtext:searchText})
        if (this.state.searchtext.length > 2 || this.state.searchtext.length == 0)
            setTimeout(() => {
                if (this.state.searchtext.length === searchText.length)
                    this.props.dispatch(searchInText(searchText))
     }, 500)
    }

    render(){
        const {table} = this.props.app;
        const {activeFacet, results, numResults, page, limit } = this.props.resultbrowser;
        const {dispatch} = this.props;
        if (!table) {
            return (
            <Panel header={<a href="#" onClick={() => dispatch(setActiveResultFacet('results'))}>
                Results [{numResults}]</a>} collapsible expanded={activeFacet === 'results'} id='result-browser'>
                { numResults === null ?
                    <MuiThemeProvider>
                        <Grid style={{textAlign: 'center'}}>
                            <CircularProgress />
                        </Grid>
                    </MuiThemeProvider>
                    :
                   <BootstrapTable data={results}
                                   remote = { true }
                                   search = { true }
                                   multiColumnSearch={ true }
                                   pagination = { true }
                                   fetchInfo={ { dataTotalSize: numResults } }
                                   tableStyle = {{border:'none'}}
                                   options={ {
                                       noDataText: 'No results available',
                                       sizePerPage: limit,
                                       hideSizePerPage: true,
                                       page: page,
                                       onPageChange: (page) => dispatch(selectActivePage(page)),
                                       onSortChange: (sortName,sortOrder) => dispatch(sortActivePage(sortName,sortOrder)),
                                       onSearchChange: this._searchInText,
                                       clearSearch: true
                                   } }
                   >
                       <TableHeaderColumn dataField='id' isKey hidden>ID</TableHeaderColumn>
                       <TableHeaderColumn dataField='timestamp' dataSort={ true } dataFormat={dateformatter}>Timestamp</TableHeaderColumn>
                       <TableHeaderColumn dataField='tool' dataSort={ true }>Plugin</TableHeaderColumn>
                       <TableHeaderColumn dataField='caption' dataSort={ true }>Caption</TableHeaderColumn>
                       <TableHeaderColumn dataField='uid' dataSort={ true }>User</TableHeaderColumn>
                       <TableHeaderColumn dataField='link2results' dataFormat={ cell => (
                           <a href={ cell }>{`Show`}</a>
                       )}>Link</TableHeaderColumn>
                   </BootstrapTable>
                }
            </Panel>
            )
        }
        else {
            return (
                <Panel header={<a href="#" onClick={() => dispatch(setActiveResultFacet('results'))}>
                    Results [{numResults}]</a>} collapsible expanded={activeFacet === 'results'}>
                    { numResults === null ?
                        <MuiThemeProvider>
                            <Grid style={{textAlign: 'center'}}>
                                <CircularProgress />
                            </Grid>
                        </MuiThemeProvider>
                        :
                        <Gallery images={
                            results.map((n, i) => ({
                                src: n.preview_file,
                                thumbnail: n.preview_file,
                                caption: n.caption,
                                useForDemo: i < 100 ? true : false,
                                history: n.link2results
                            }))
                        } showThumbnails
                        />
                    }
                </Panel>

            )
        }
    }
}


const mapStateToProps = (state) => ({
    resultbrowser: state.resultbrowserReducer,
    app: state.appReducer
});

export default connect(mapStateToProps) (Resulttype)
