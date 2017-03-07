import React from 'react';
import {connect} from 'react-redux';
import {Row, Col, Button, ListGroup, ListGroupItem, Grid} from 'react-bootstrap'

class FileTree extends React.Component {

    render() {
        let {node} = this.props;
        let childNodes, cN, click;
        if (node.childNodes != null) {
            childNodes = node.childNodes.map((n, i) => {
                return <FileTree {...this.props} node={n}/>
            });
            cN = 'directory expanded';
            click = this.props.handleClose;
        }else if (node.type === 'file'){
            cN = `file ext_${node.ext}`;
            click = this.props.handleFileClick;
        }else {
            cN = 'directory collapsed';
            click = this.props.handleOpen;
        }
        return (
            <ul className="jqueryFileTree">
                <li className={cN}>
                    <a onClick={(e) => click(e, node.path)} href="#">{node.name}</a>
                    {childNodes}
                </li>
            </ul>
        )
    }
}


export default FileTree