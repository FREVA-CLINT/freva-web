import React from 'react';
import ReactDOM from 'react-dom';
import {connect} from 'react-redux';
import {Grid, Row, Col, Accordion, Panel} from 'react-bootstrap';
import {loadFacets, selectFacet, clearFacet} from './actions';
import _ from 'lodash'

class OwnPanel extends Panel {
    constructor(props, context) {
        super(props, context);
        this.handleClickTitle = this.handleClickTitle.bind(this);
        this.renderBody = this.renderBody.bind(this);
    }

    /**
     * Override the method to allow different title click behaviour
     */
    handleClickTitle(e) {
        console.log(this.props);
        console.log(this.state)
        if (e.target.className.indexOf('remove') !== -1) {
            this.props.removeFacet();
        }else
            super.handleClickTitle(e);
    }

    //renderBody(rawChildren, bsProps) {
    //    if (this.state.expanded)
    //        return super.renderBody(rawChildren, bsProps)
    //}
}


class Databrowser extends React.Component {

    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.dispatch(loadFacets());
    }

    render() {

        const {facets, selectedFacets} = this.props.databrowser;
        const {dispatch} = this.props;
        const facetPanels = _.map(facets, (value, key) => {
            let panelHeader;
            if (selectedFacets[key]) {
                panelHeader = <span style={{cursor: 'pointer'}}>{key}: <strong>{selectedFacets[key]} <span className="glyphicon glyphicon-remove-circle" onClick={(e) => {e.preventDefault();console.log('click')}}/></strong></span>
            }else if(value.length == 2) {
                panelHeader = <span style={{cursor: 'pointer'}}>{key}: <strong>{value[0]}</strong></span>
            }else {
                panelHeader = <span style={{cursor: 'pointer'}}>{key} ({value.length/2})</span>
            }
            return (
                <OwnPanel header={panelHeader} eventKey={key} key={key} removeFacet={() => dispatch(clearFacet(key))}>
                    <Row>
                        {value.map((item, i) => {
                            if (i%2==0) {
                                return (
                                    <Col md={3} xs={6}>
                                        <a href="#" onClick={(e) => {e.preventDefault(); dispatch(selectFacet(key, item))}}>{item}</a> [{value[i+1]}]
                                    </Col>
                                )
                            }
                        })}
                    </Row>
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
                    <Col md={12}>
                        <Accordion>
                            {facetPanels}
                        </Accordion>
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