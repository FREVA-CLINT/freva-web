import React from 'react';
import ReactDOM from 'react-dom';
import {Grid, Row, Col, Panel, FormControl, Tooltip, OverlayTrigger, Modal, Button} from 'react-bootstrap';


class AccordionItemBody extends React.Component {

    constructor(props, context) {
        super(props, context);
        this.state = {needle: ''};
    }

    handleChange() {
        const needle = ReactDOM.findDOMNode(this.refs.searchInput).value;
        this.setState({needle});
    }

    shouldComponentUpdate(nextProps) {
        return this.props.visible || nextProps.visible
    }

    renderFilteredItems(filteredValues) {
        const {metadata, facetClick, eventKey} = this.props;
        return filteredValues.map((item, i) => {
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
        });
    }

    render() {
        const {eventKey, value, metadata} = this.props;
        let {needle} = this.state;
        needle = needle.toLowerCase();
        const filteredValues = [];
        value.map((val, i) => {
            if (i%2==0) {
                if (val.toLowerCase().indexOf(needle) !== -1 || (metadata && metadata[val] && metadata[val].toLowerCase().indexOf(needle) !== -1)) {
                    filteredValues.push(val);
                    filteredValues.push(value[i+1]);
                }

            }
        });

        const filteredItems = this.renderFilteredItems(filteredValues);

        return (
            <Row>
                <Col md={12}>
                    <FormControl id={`search`} type="text" placeholder={`Search ${eventKey} name`} ref={`searchInput`}
                                 onChange={() => this.handleChange()}/>
                </Col>
                {filteredItems}
            </Row>
        )

    }
}

export default AccordionItemBody