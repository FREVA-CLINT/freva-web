import React from 'react';
import ReactDOM from 'react-dom';
import {connect} from 'react-redux';
import {
    Row, Col, Button, ListGroup, ListGroupItem, Grid, Modal, ButtonGroup, Input,
    FormGroup, ControlLabel, FormControl, InputGroup
} from 'react-bootstrap'
import FileTree from '../../Components/FileTree'
import {fetchDir, closeDir, changeRoot} from '../../Components/FileTree/actions'
import {exportPlugin} from './actions'
import _ from 'lodash';
import ActionSearch from 'material-ui/svg-icons/action/search';

class PluginList extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            showModal: false,
            value: '',
            searchValue: ''
        };
    }

    handleExport() {
        this.props.dispatch(exportPlugin(this.state.value));
        this.setState({showModal: false})
    }

    render() {

        let {plugins, exported} = this.props.pluginList;
        const {nodes, root} = this.props.fileTree;
        const {currentUser} = this.props;

        const {searchValue} = this.state;

        plugins = _.filter(plugins, (p) => {
            const title = _.includes(p[1].name.toLowerCase(), searchValue.toLowerCase());
            const description = _.includes(p[1].description.toLowerCase(), searchValue.toLowerCase());
            return title || description
        });

        let childs = nodes.map(n =>
            <FileTree node={n}
                      key={n.name}
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
                        <Button bsStyle="info" className="pull-right"
                                onClick={() => exported ? this.props.dispatch(exportPlugin()) : this.setState({showModal: true})}>
                            {exported ? 'Remove exported Plugin' : 'Plug-my-Plugin'}
                        </Button>
                    </Col>
                </Row>
                <Row>
                    <Col md={8}>
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
                    <Col md={4}>
                        <InputGroup style={{marginTop: 20}}>
                            <FormControl type="text" ref="searchInput" value={this.state.searchValue}
                                         onChange={() => this.setState({searchValue: ReactDOM.findDOMNode(this.refs.searchInput).value})}
                                         placeholder="Search for plugins"/>
                            <InputGroup.Addon style={{padding: 0, paddingLeft: 8, paddingRight: 8}}>
                                <ActionSearch />
                            </InputGroup.Addon>
                        </InputGroup>
                    </Col>

                </Row>

                <Modal show={this.state.showModal}
                       onShow={() => this.props.dispatch(changeRoot({id: 'home', path: currentUser.home}, 'py'))}
                       onHide={() => this.setState({showModal: false})}>
                    <Modal.Header closeButton>
                        <Modal.Title>Plug-in your own plugin</Modal.Title>
                    </Modal.Header>

                    <Modal.Body>
                        <p>Here you can plugin your own plugin</p>
                        <ButtonGroup style={{marginBottom: 10}}>
                            <Button bsStyle="primary" active={root.id === 'home'}
                                    onClick={() => this.props.dispatch(changeRoot({id: 'home', path: currentUser.home}, 'py'))}>
                                Home
                            </Button>
                            <Button bsStyle="primary" active={root.id === 'scratch'}
                                    onClick={() => this.props.dispatch(changeRoot({id: 'scratch', path: currentUser.scratch}, 'py'))}>
                                Scratch
                            </Button>
                        </ButtonGroup>
                        {childs}
                        <FormGroup style={{marginTop: 10}}>
                            <ControlLabel>File to plugin</ControlLabel>
                            <FormControl type="text" ref="input" value={this.state.value}
                                         onChange={() => this.setState({value: ReactDOM.findDOMNode(this.refs.input).value})}/>
                        </FormGroup>
                    </Modal.Body>

                    <Modal.Footer>
                        <Button bsStyle="primary" onClick={() => this.handleExport()}>Export Plugin</Button>
                    </Modal.Footer>

                </Modal>

            </Grid>
        )
    }
}

const mapStateToProps = state => ({
    pluginList: state.pluginListReducer,
    fileTree: state.fileTreeReducer,
    currentUser: state.appReducer.currentUser
});

export default connect(mapStateToProps)(PluginList);