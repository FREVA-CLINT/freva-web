import React from 'react';
import {connect} from 'react-redux';
import {Grid, Row, Col, Accordion, Panel} from 'react-bootstrap';
import {loadResultFacets, selectResultFacet, clearResultFacet,
    clearAllResultFacets, setActiveResultFacet, loadResultFiles,
    setMetadata } from './actions';
import _ from 'lodash';
import AccordionItemBody from '../../Components/AccordionItemBody';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import CircularProgress from 'material-ui/CircularProgress';
import OwnPanel from '../../Components/OwnPanel'
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';

class Resultbrowser extends React.Component {

    constructor(props) {
        super(props);
    }

    /**
     * On mount we load all facets and files to display
     * Also load the metadata.js script
     */
    componentDidMount() {
        this.props.dispatch(loadResultFacets());
        this.props.dispatch(loadResultFiles());
    }



    /**
     * Loop all facets and render the panels
     */
    renderFacetPanels() {

        const {facets, selectedFacets, activeFacet, metadata, } = this.props.resultbrowser;
        const {dispatch} = this.props;
        return _.map(facets, (value, key) => {
            let panelHeader;
            if (selectedFacets[key]) {
                panelHeader = <span style={{cursor: 'pointer'}}>{key}: <strong>{selectedFacets[key]} <a href="#"
                                                                                                        onClick={(e) => e.preventDefault()}><span
                    className="glyphicon glyphicon-remove-circle"
                    onClick={(e) => e.preventDefault()}/></a></strong></span>
            } else if (value.length === 2) {
                panelHeader = <span style={{cursor: 'pointer'}}>{key}: <strong>{value[0]}</strong></span>
            } else {
                panelHeader = <span style={{cursor: 'pointer'}}>{key} ({value.length / 2})</span>
            }
            return (
                <OwnPanel header={panelHeader} eventKey={key} key={key} removeFacet={() => dispatch(clearResultFacet(key))}
                          collapse={() => dispatch(setActiveResultFacet(key))}>
                    <AccordionItemBody eventKey={key} value={value}
                                       facetClick={(key, item) => dispatch(selectResultFacet(key, item))}
                                       metadata={metadata[key] ? metadata[key] : null} visible={key === activeFacet}/>
                </OwnPanel>
            )
        });
    }

    renderFilesPanel() {
        //TODO: This should be a separate component
        const {activeFacet,results, numResults} = this.props.resultbrowser;
        const {dispatch} = this.props;


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
                                    pagination
                                    tableStyle = {{border:'none'}}
                                    options={ {
                                        noDataText: 'No results available',
                                        sizePerPage: 25,
                                        hideSizePerPage: true
                                    }}
                                    striped hover condensed>
                        <TableHeaderColumn dataField='id' isKey hidden>ID</TableHeaderColumn>
                        <TableHeaderColumn dataField='tool'>Plugin</TableHeaderColumn>
                        <TableHeaderColumn dataField='link2results' dataFormat={ cell => (
                            <a href={ cell }>{`Show`}</a>
                        )}>Link</TableHeaderColumn>
                    </BootstrapTable>
                }
            </Panel>
        )
    }

    render() {
        const {facets, selectedFacets, activeFacet} = this.props.resultbrowser;
        const {dispatch} = this.props;

        // Wait until facets are loaded
        if (facets.length === 0){
            return (
                <MuiThemeProvider>
                    <Grid style={{textAlign: 'center'}}>
                        <CircularProgress />
                    </Grid>
                </MuiThemeProvider>
            )
        }

        const facetPanels = this.renderFacetPanels();

        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <h2>Resultbrowser</h2>
                    </Col>
                </Row>
                <Row>
                    {Object.keys(selectedFacets).length !== 0 ?
                    <Col md={12}>
                        <Panel>
                            <a href="#" onClick={(e) => {e.preventDefault(); dispatch(clearAllResultFacets())}}>Clear all</a>
                        </Panel>
                    </Col> : null}
                </Row>
                <Row>
                    <Col md={12}>
                        <Accordion activeKey={activeFacet}>
                            {facetPanels}
                        </Accordion>
                        {this.renderFilesPanel()}
                    </Col>
                </Row>
            </Grid>
        )
    }
}

const mapStateToProps = (state) => ({
    resultbrowser: state.resultbrowserReducer
});

export default connect(mapStateToProps) (Resultbrowser)