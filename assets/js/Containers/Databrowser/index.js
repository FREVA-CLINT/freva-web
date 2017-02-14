import React from 'react';
import ReactDOM from 'react-dom';
import {connect} from 'react-redux';
import {Grid, Row, Col, Accordion, Panel, FormControl, Tooltip, OverlayTrigger} from 'react-bootstrap';
import {loadFacets, selectFacet, clearFacet, clearAllFacets, setActiveFacet, setMetadata} from './actions';
import _ from 'lodash'
import $ from 'jquery';

class OwnPanel extends Panel {
    constructor(props, context) {
        super(props, context);
        this.handleClickTitle = this.handleClickTitle.bind(this);
    }

    /**
     * Override the method to allow different title click behaviour
     */
    handleClickTitle(e) {
        if (e.target.className.indexOf('remove') !== -1) {
            this.props.removeFacet();
        }else
            this.props.collapse();
            super.handleClickTitle(e);
    }
}

class AccordionItemBody extends React.Component {

    constructor(props, context) {
        super(props, context);
        this.state = {needle: ''};
    }

    handleChange() {
        const needle = ReactDOM.findDOMNode(this.refs.searchInput).value;
        this.setState({needle});
    }

    render() {
        const {eventKey, value, facetClick, metadata} = this.props;
        let {needle} = this.state;
        needle = needle.toLowerCase()
        const filteredValues = [];
        value.map((val, i) => {
            if (i%2==0) {
                if (val.toLowerCase().indexOf(needle) !== -1 || (metadata[val] && metadata[val].toLowerCase().indexOf(needle) !== -1)) {
                    filteredValues.push(val);
                    filteredValues.push(value[i+1]);
                }

            }
        });
        return (
            <Row>
                <Col md={12}>
                    <FormControl id={`search`} type="text" placeholder={`Search ${eventKey} name`} ref={`searchInput`}
                                 onChange={() => this.handleChange()}/>
                </Col>
                {filteredValues.map((item, i) => {
                    if (i%2==0) {
                        if (metadata && metadata[item]) {
                            return (
                                <Col md={3} xs={6} key={item}>
                                    <OverlayTrigger overlay={<Tooltip>{metadata[item]}</Tooltip>}>
                                        <a href="#" onClick={(e) => {e.preventDefault(); facetClick(eventKey, item)}}>{item}</a>
                                    </OverlayTrigger>
                                    {" "}[{filteredValues[i+1]}]
                                </Col>
                            )
                        }
                        return (
                            <Col md={3} xs={6} key={item}>
                                <a href="#" onClick={(e) => {e.preventDefault(); facetClick(eventKey, item)}}>{item}</a> [{filteredValues[i+1]}]
                            </Col>
                        )
                    }
                })}
            </Row>
        )

    }
}



class Databrowser extends React.Component {

    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.dispatch(loadFacets());
        $.getScript({
            url: 'https://freva.met.fu-berlin.de/static/js/metadata.js',
            dataType: "script",
            success: (script, textStatus) => this.props.dispatch(setMetadata({variable: window.variable, model: window.model, institute: window.institute}))

        })
    }

    render() {

        const {facets, selectedFacets, activeFacet, metadata} = this.props.databrowser;
        const {dispatch} = this.props;
        const facetPanels = _.map(facets, (value, key) => {
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
                        metadata={metadata[key] ? metadata[key] : null}/>
                </OwnPanel>
            )
        });

        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <h2>Data-Browser</h2>
                    </Col>
                </Row>
                <Row>
                    {Object.keys(selectedFacets).length !== 0 ?
                    <Col md={12}>
                        <Panel>
                            <a href="#" onClick={(e) => {e.preventDefault(); dispatch(clearAllFacets())}}>Clear all</a>
                        </Panel>
                    </Col> : null}
                </Row>
                <Row>
                    <Col md={12}>
                        <Accordion activeKey={activeFacet}>
                            {facetPanels}
                        </Accordion>
                        <Panel style={{marginTop: 5}}>
                            freva --databrowser
                            {_.map(selectedFacets, (value, key) => {
                                return <span> {key}=<strong>{value}</strong></span>
                            })}
                        </Panel>
                    </Col>
                </Row>
            </Grid>
        )
    }

}

const mapStateToProps = state => ({
    databrowser: state.databrowserReducer
});

export default connect(mapStateToProps)(Databrowser);