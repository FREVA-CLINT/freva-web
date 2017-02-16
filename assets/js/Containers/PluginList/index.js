import React from 'react';
import ReactDOM from 'react-dom';
import { Link, browserHistory } from 'react-router'
import {connect} from 'react-redux';
import {
    Row, Col, Button, ListGroup, ListGroupItem, Grid, Modal, ButtonGroup, Input,
    FormGroup, ControlLabel, FormControl, InputGroup, Badge, Label, Panel
} from 'react-bootstrap'
import FileTree from '../../Components/FileTree'
import {fetchDir, closeDir, changeRoot} from '../../Components/FileTree/actions'
import {exportPlugin, loadPlugins, updateCategoryFilter, updateTagFilter, updateSearchFilter} from './actions'
import _ from 'lodash';
import ActionSearch from 'material-ui/svg-icons/action/search';
import Checkbox from 'material-ui/Checkbox';

const styles = {
    chip: {
        cursor: 'pointer',
        margin: 5,
        padding: 6
    }
};


class PluginList extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            showModal: false,
            value: '',
        };
    }

    componentDidMount() {
        this.props.dispatch(loadPlugins());
    }

    handleExport() {
        this.props.dispatch(exportPlugin(this.state.value));
        this.setState({showModal: false})
    }

    render() {

        let {plugins, exported, tags, categories, categoriesFilter, tagsFilter, filteredPlugins, searchFilter} = this.props.pluginList;
        const {nodes, root} = this.props.fileTree;
        const {currentUser, dispatch} = this.props;

        let decadalPlugins = _.filter(filteredPlugins, (val) => {
            return val[1].category === 'decadal';
        });

        let statisticPlugins = _.filter(filteredPlugins, (val) => {
            return val[1].category === 'statistical';
        });

        let postprocPlugins = _.filter(filteredPlugins, (val) => {
            return val[1].category === 'postproc';
        });

        let supportPlugins = _.filter(filteredPlugins, (val) => {
            return val[1].category === 'support';
        });

        let otherPlugins = _.filter(filteredPlugins, (val) => {
            return val[1].category.toLowerCase() === 'other';
        });

        let categoryTitle = {
            decadal: 'Decadal Evaluation',
            statistical: 'Statistical Analysis',
            postproc: 'Post-Processing',
            support: 'Support Plugins',
            other: 'Others'
        };

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
                        {!currentUser.isGuest ?
                        <Button bsStyle="info" className="pull-right"
                                onClick={() => exported ? this.props.dispatch(exportPlugin()) : this.setState({showModal: true})}>
                            {exported ? 'Remove exported Plugin' : 'Plug-my-Plugin'}
                        </Button> : null}
                    </Col>
                </Row>
                <Row>
                    <Col md={8}>
                        {decadalPlugins.length > 0 ?
                            <Panel header={<h2>Decadal Evaluation</h2>}>
                                <ListGroup fill>
                                    {decadalPlugins.map(val => {
                                        return (
                                            <ListGroupItem header={val[1].name}
                                                           onClick={(e) => {e.preventDefault(); browserHistory.push(`/plugins/${val[0]}/detail/`)}}
                                                           href={`/plugins/${val[0]}/detail/`}
                                                           key={val[0]}>
                                                {val[1].user_exported ?
                                                    <span
                                                        style={{color:'red'}}>You have plugged in this tool.<br/><br/></span> : null}
                                                {val[1].description}
                                            </ListGroupItem>
                                        )
                                    })}
                                </ListGroup>
                            </Panel> : null}

                        {statisticPlugins.length > 0 ?
                            <Panel header={<h2>Statistical Analysis</h2>}>
                                <ListGroup fill>
                                    {statisticPlugins.map(val => {
                                        return (
                                            <ListGroupItem header={val[1].name}
                                                           onClick={(e) => {e.preventDefault(); browserHistory.push(`/plugins/${val[0]}/detail/`)}}
                                                           href={`/plugins/${val[0]}/detail/`}
                                                           key={val[0]}>
                                                {val[1].user_exported ?
                                                    <span
                                                        style={{color:'red'}}>You have plugged in this tool.<br/><br/></span> : null}
                                                {val[1].description}
                                            </ListGroupItem>
                                        )
                                    })}
                                </ListGroup>
                            </Panel> : null}

                        {postprocPlugins.length > 0 ?
                            <Panel header={<h2>Post-Processing</h2>}>
                                <ListGroup fill>
                                    {postprocPlugins.map(val => {
                                        return (
                                            <ListGroupItem header={val[1].name}
                                                           onClick={(e) => {e.preventDefault(); browserHistory.push(`/plugins/${val[0]}/detail/`)}}
                                                           href={`/plugins/${val[0]}/detail/`}
                                                           key={val[0]}>
                                                {val[1].user_exported ?
                                                    <span
                                                        style={{color:'red'}}>You have plugged in this tool.<br/><br/></span> : null}
                                                {val[1].description}
                                            </ListGroupItem>
                                        )
                                    })}
                                </ListGroup>
                            </Panel> : null}

                        {supportPlugins.length > 0 ?
                            <Panel header={<h2>Supporting Plugins</h2>}>
                                <ListGroup fill>
                                    {supportPlugins.map(val => {
                                        return (
                                            <ListGroupItem header={val[1].name}
                                                           onClick={(e) => {e.preventDefault(); browserHistory.push(`/plugins/${val[0]}/detail/`)}}
                                                           href={`/plugins/${val[0]}/detail/`}
                                                           key={val[0]}>
                                                {val[1].user_exported ?
                                                    <span
                                                        style={{color:'red'}}>You have plugged in this tool.<br/><br/></span> : null}
                                                {val[1].description}
                                            </ListGroupItem>
                                        )
                                    })}
                                </ListGroup>
                            </Panel> : null}

                        {otherPlugins.length > 0 ?
                            <Panel header={<h2>Other</h2>}>
                                <ListGroup fill>
                                    {otherPlugins.map(val => {
                                        return (
                                            <ListGroupItem header={val[1].name}
                                                           onClick={(e) => {e.preventDefault(); browserHistory.push(`/plugins/${val[0]}/detail/`)}}
                                                           href={`/plugins/${val[0]}/detail/`}
                                                           key={val[0]}>
                                                {val[1].user_exported ?
                                                    <span
                                                        style={{color:'red'}}>You have plugged in this tool.<br/><br/></span> : null}
                                                {val[1].description}
                                            </ListGroupItem>
                                        )
                                    })}
                                </ListGroup>
                            </Panel> : null}
                    </Col>
                    <Col md={4}>
                        <InputGroup style={{marginTop: 20}}>
                            <FormControl type="text" ref="searchInput" value={searchFilter}
                                         onChange={() => dispatch(updateSearchFilter(ReactDOM.findDOMNode(this.refs.searchInput).value))}
                                         placeholder="Search for plugins"/>
                            <InputGroup.Addon style={{padding: 0, paddingLeft: 8, paddingRight: 8}}>
                                <ActionSearch />
                            </InputGroup.Addon>
                        </InputGroup>

                        <div style={{marginTop:10}}>
                            <ControlLabel>Categories:</ControlLabel>
                            <div>
                                {

                                    _.map(categories, (v, k) => {
                                        return <Checkbox label={`${categoryTitle[k]} (${v.length})`}
                                                         onCheck={() => dispatch(updateCategoryFilter(k))}
                                                         checked={_.includes(categoriesFilter, k)}
                                                         key={k}/>
                                    })
                                }
                            </div>
                        </div>

                        <div style={{marginTop:10}}>
                            <ControlLabel>Tags:</ControlLabel>
                            <div>
                                {
                                    tags.map(tag => {
                                        return <Col md={4} style={{paddingLeft:0}} key={tag}>
                                            <Label bsStyle={_.includes(tagsFilter, tag) ? "success" : 'default'}
                                                   style={styles.chip}
                                                   onClick={() => dispatch(updateTagFilter(tag))}
                                                   >
                                                {tag}
                                            </Label></Col>
                                    })
                                }

                            </div>
                        </div>
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