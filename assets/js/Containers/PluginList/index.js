import React from 'react';
import ReactDOM from 'react-dom';
import {connect} from 'react-redux';
import {Row, Col, Button, ListGroup, ListGroupItem, Grid, Modal, ButtonGroup, Input,
    FormGroup, ControlLabel, FormControl} from 'react-bootstrap'
import FileTree from '../../Components/FileTree'
import {fetchDir, closeDir, changeRoot} from '../../Components/FileTree/actions'

class PluginList extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            showModal: false,
            value: ''
        };
    }

    componentDidMount() {
        this.props.dispatch(fetchDir(this.props.fileTree.root.path, 'py'))
    }

    render() {

        const {plugins, exported} = this.props.pluginList;
        const {nodes, root} = this.props.fileTree;

        let childs = nodes.map(n =>
            <FileTree node={n}
                      extension="py"
                      handleOpen={(e, path) => {e.preventDefault(); this.props.dispatch(fetchDir(path, "py"))}}
                      handleClose={(e, path) => {e.preventDefault(); this.props.dispatch(closeDir(path))}}
                      handleFileClick={(e, path) => {e.preventDefault(); this.setState({value:path})}}/>
        );

        return (
            <Grid>
                <Row>
                    <Col md={6}><h2>Plugins</h2></Col>
                    <Col md={6} style={{paddingTop: 10}}>
                        <Button bsStyle="info" className="pull-right" onClick={() => this.setState({showModal: true})}>
                            {exported ? 'Remove exported Plugin' : 'Plug-my-Plugin'}
                        </Button>
                    </Col>
                </Row>
                <Row>
                    <Col md={12}>
                        <ListGroup style={{marginTop: 20}}>
                            {plugins.map(val => {
                                return (
                                    <ListGroupItem header={val[1].name} href={`/plugins/${val[0]}/detail/`}
                                                   key={val[0]}>
                                        {val[1].user_exported ?
                                            <span
                                                style={{color:'red'}}>You have plugged in this tool.<br/><br/></span> : null}
                                        {val[1].description}
                                    </ListGroupItem>
                                )
                            })}
                        </ListGroup>
                    </Col>


                </Row>

                <Modal show={this.state.showModal} onHide={() => this.setState({showModal: false})}>
                    <Modal.Header closeButton>
                        <Modal.Title>Plug-in your own plugin</Modal.Title>
                    </Modal.Header>

                    <Modal.Body>
                        <p>Here you can plugin your own plugin</p>
                        <ButtonGroup>
                            <Button bsStyle="primary" active={root.id === 'home'}
                                onClick={() => this.props.dispatch(changeRoot({id: 'home', path:'/home/illing/'}, 'py'))}>
                                Home
                            </Button>
                            <Button bsStyle="primary" active={root.id === 'scratch'}
                                onClick={() => this.props.dispatch(changeRoot({id: 'scratch', path:'/net/scratch/illing/'}, 'py'))}>
                                Scratch
                            </Button>
                        </ButtonGroup>
                        {childs}
                        <FormGroup>
                            <ControlLabel>File to plugin</ControlLabel>
                            <FormControl type="text" ref="input" value={this.state.value}
                                         onChange={() => this.setState({value: ReactDOM.findDOMNode(this.refs.input).value})}/>
                        </FormGroup>
                    </Modal.Body>

                    <Modal.Footer>
                        <Button bsStyle="primary">Export Plugin</Button>
                    </Modal.Footer>

                </Modal>

            </Grid>
        )
    }
}

const mapStateToProps = state => ({
    pluginList: state.pluginListReducer,
    fileTree: state.fileTreeReducer
});

export default connect(mapStateToProps)(PluginList);