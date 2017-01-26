import React from 'react';
import {connect} from 'react-redux';
import {Row, Col, Button, ListGroup, ListGroupItem, Grid} from 'react-bootstrap'

class PluginList extends React.Component {

    render() {

        const {plugins, exported} = this.props.pluginList;

        return (
            <Grid>
                <Row>
                    <Col md={6}><h2>Plugins</h2></Col>
                    <Col md={6} style={{paddingTop: 10}}>
                        <Button bsStyle="info" className="pull-right">
                            {exported ? 'Remove exported Plugin' : 'Plug-my-Plugin'}
                        </Button>
                    </Col>
                </Row>
                <Row>
                    <Col md={12}>
                        <ListGroup style={{marginTop: 20}}>
                            {plugins.map(val => {
                                return (
                                    <ListGroupItem header={val[1].name} href={`/plugins/${val[0]}/detail/`} key={val[0]}>
                                        {val[1].user_exported ?
                                            <span style={{color:'red'}}>You have plugged in this tool.<br/><br/></span> : null}
                                        {val[1].description}
                                    </ListGroupItem>
                                )
                            })}
                        </ListGroup>
                    </Col>
                </Row></Grid>
        )
    }
}


const mapStateToProps = state => ({
    pluginList: state.pluginListReducer
});

export default connect(mapStateToProps)(PluginList);