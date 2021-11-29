import React from 'react'
import {Card} from 'react-bootstrap'

class OwnPanel extends Card {
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

export default OwnPanel;