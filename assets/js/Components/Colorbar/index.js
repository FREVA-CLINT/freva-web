var d3 = require('d3')
import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';

const RdBu_r = ['#08519c', '#3182bd', '#6baed6', '#bdd7e7', '#eff3ff',
            '#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15'];

class Colorbar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {};
        this.drawColorbar = this.drawColorbar.bind(this);
        this.drawArrows = this.drawArrows.bind(this)
    }

    componentDidMount() {
        this.drawColorbar();
    }

    componentDidUpdate() {
        this.drawColorbar();
    }

    drawColorbar() {
        let {width, minVal, maxVal, colormap, labelPos, dx} = this.props;
        if (!colormap)
            colormap = RdBu_r;
        let dy = 0;
        if (labelPos === 'top') {
            dy = 20;
        }
        this.colormap = colormap;
        const node = ReactDOM.findDOMNode(this.refs.svg);
        const element = d3.select(node);
        element.html('');
        const offset = this.props.arrows ? 1 : 0;
        this.colorWidth = (width - 18) / (colormap.length + offset) ;
        let steps = colormap.length;
        let stepSize = (maxVal - minVal) / steps;
        let i = this.props.arrows ? this.colorWidth : 0;
        colormap.map((val, j) => {
            element.append("rect")
                .attr("x", i + dx + 9)
                .attr("y", dy)
                .attr("width", this.colorWidth)
                .attr("height", 30)
                .attr("fill", val);

            const value = Math.round((minVal + j * stepSize) * 100) / 100;

            if (j % 2 === 0) {
                element.append("text")
                    .attr("x", (d) => {const s = value > 0 ? -10 : -15; return 9 + dx + s + i})
                    .attr("y", 50 + dy)
                    .attr("color", 'white')
                    .text(function (d) {
                        return value.toFixed(1);
                    })
                    .style('fill', 'grey')
            }
            i += this.colorWidth;
            return 0
        });


        element.append("text")
            .attr("x", 5 + i + dx - 10)
            .attr("y", 50 + dy)
            .attr("color", 'white')
            .text(function (d) {
                return maxVal.toFixed(1)
            })
            .style('fill', 'grey');

        this.drawArrows(element, i, dy, dx)
    }

    drawArrows(element, right, dy, dx) {
        // Add colorbar arrows
        const {arrows} = this.props;
        dx = 9;
        if (arrows) {
            if (arrows === 'left' || arrows === 'both') {
                element.append("svg:polygon")
                    .style('fill', this.colormap[0])
                    .style("stroke-width", "1")
                    .classed("p", true)
                    .attr("points", [[this.colorWidth + dx, dy], [this.colorWidth + dx, 30 + dy], [0 + dx, 15 + dy]]);
            }
            if (arrows === 'right' || arrows === 'both') {
                element.append("svg:polygon")
                    .style('fill', this.colormap[this.colormap.length - 1])
                    .style("stroke-width", "1")
                    .classed("p", true)
                    .attr("points", [[this.colorWidth + right + dx, dy], [this.colorWidth + right + dx, 30 + dy],
                        [right + 2 * this.colorWidth + dx, 15 + dy]]);
            }
        }
    }
    
    render() {
        let {width, style, height} = this.props;
        style = {...style, width: '100%'};
        return (
            <svg style={style} viewBox={`0 0 ${width} ${height}`}>
                <g ref="svg"/>
            </svg>
        )
    }
}

export default Colorbar;