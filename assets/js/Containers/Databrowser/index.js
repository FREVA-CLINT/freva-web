import React from 'react';
import {connect} from 'react-redux';
import {Container, Row, Col, Accordion, Card, FormControl, Tooltip, OverlayTrigger, Modal, Button} from 'react-bootstrap';
import {loadFacets, selectFacet, clearFacet, clearAllFacets, setActiveFacet, setMetadata, loadFiles,
        loadNcdump, resetNcdump} from './actions';
import _ from 'lodash'
import $ from 'jquery';
import NcdumpDialog from '../../Components/NcdumpDialog'
//import AccordionItemBody from '../../Components/AccordionItemBody';
//import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
//import CircularProgress from 'material-ui/CircularProgress';
//import OwnPanel from '../../Components/OwnPanel'

class Databrowser extends React.Component {

    constructor(props) {
        super(props);
        this.state = {showDialog: false, fn: null}
    }

    /**
     * On mount we load all facets and files to display
     * Also load the metadata.js script
     */
    componentDidMount() {
        this.props.dispatch(loadFacets());
        this.props.dispatch(loadFiles());
        $.getScript({
            url: '/static/js/metadata.js',
            dataType: "script",
            success: (script, textStatus) => this.props.dispatch(setMetadata({variable: window.variable, model: window.model, institute: window.institute}))

        })
    }

    /**
     * Loop all facets and render the panels
     */
    renderFacetPanels() {
        const {facets, selectedFacets, activeFacet, metadata} = this.props.databrowser;
        const {dispatch} = this.props;
        return _.map(facets, (value, key) => {
            let panelHeader;
            if (selectedFacets[key]) {
                panelHeader = <span style={{cursor: 'pointer'}}>{key}: <strong>{selectedFacets[key]} <a href="#" onClick={(e) => e.preventDefault()}><span className="glyphicon glyphicon-remove-circle" onClick={(e) => e.preventDefault()}/></a></strong></span>
            }else if(value.length == 2) {
                panelHeader = <span style={{cursor: 'pointer'}}>{key}: <strong>{value[0]}</strong></span>
            }else {
                panelHeader = <span style={{cursor: 'pointer'}}>{key} ({value.length/2})</span>
            }
            return (
                <OwnPanel header={panelHeader} eventKey={key} key={key} removeFacet={() => dispatch(clearFacet(key))}
                    collapse={() => dispatch(setActiveFacet(key))}>
                    <AccordionItemBody eventKey={key} value={value} facetClick={(key, item) => dispatch(selectFacet(key, item))}
                        metadata={metadata[key] ? metadata[key] : null} visible={key===activeFacet}/>
                </OwnPanel>
            )
        });
    }

    renderFilesPanel() {
        //TODO: This should be a separate component
        const {activeFacet, files, numFiles,} = this.props.databrowser;
        const {dispatch} = this.props;
        return (
            <Card header={<a href="#" onClick={() => dispatch(setActiveFacet('files'))}>Files [{numFiles}]</a>} collapsible expanded={activeFacet === 'files'}>
                <div style={{maxHeight:500,overflow:'auto'}}>
                    <ul className="jqueryFileTree">
                      {_.map(files, (fn) => {
                          return (

                              <li className="file ext_nc" key={fn} style={{whiteSpace: 'normal'}}>
                                  <OverlayTrigger overlay={<Tooltip>Click to execute 'ncdump -h'<br/>and view metadata</Tooltip>}>
                                    <span className="ncdump glyphicon glyphicon-info-sign"
                                          onClick={() => {this.setState({showDialog: true, fn: fn})}}
                                          style={{cursor: 'pointer'}} />
                                  </OverlayTrigger>
                                  {` `}{fn}
                              </li>
                          )
                      })}
                    </ul>
              </div>
            </Card>
        )
    }

    render() {
        const {files, facets, selectedFacets, activeFacet, ncdumpStatus, ncdumpOutput} = this.props.databrowser;
        const {dispatch} = this.props;

        // Wait until facets are loaded
        if (facets.length === 0){
            return (
                <MuiThemeProvider>
                    <Container style={{textAlign: 'center'}}>
                        <CircularProgress />
                    </Container>
                </MuiThemeProvider>
            )
        }

        const facetPanels = this.renderFacetPanels();

        return (
            <Container>
                <Row>
                    <Col md={12}>
                        <h2>Data-Browser</h2>
                    </Col>
                </Row>
                <Row>
                    {Object.keys(selectedFacets).length !== 0 ?
                    <Col md={12}>
                        <Card>
                            <a href="#" onClick={(e) => {e.preventDefault(); dispatch(clearAllFacets())}}>Clear all</a>
                        </Card>
                    </Col> : null}
                </Row>
                <Row>
                    <Col md={12}>
                        <Accordion activeKey={activeFacet}>
                            {facetPanels}
                        </Accordion>
                        
                        <Card style={{marginTop: 5}}>
                            freva --databrowser
                            {_.map(selectedFacets, (value, key) => {
                                return <span key={`command-${key}`}> {key}=<strong>{value}</strong></span>
                            })}
                        </Card>

                        {this.renderFilesPanel()}

                        <NcdumpDialog show={this.state.showDialog}
                                      file={this.state.fn}
                                      onClose={() => {this.setState({showDialog: false}); dispatch(resetNcdump())}}
                                      submitNcdump={(fn, pw) => dispatch(loadNcdump(fn, pw))}
                                      status={ncdumpStatus}
                                      output={ncdumpOutput} />
                    </Col>
                </Row>
            </Container>
        )
    }

}

const mapStateToProps = state => ({
    databrowser: state.databrowserReducer
});

export default connect(mapStateToProps)(Databrowser);
