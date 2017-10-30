var d3 = require('d3');
import React from 'react';
import continentborder from '../../data/continentborder.json'
import {feature} from 'topojson';
import ReactDOM from 'react-dom';
import Colorbar from '../Colorbar'

class AbstractMap extends React.Component {

    constructor(props) {
        super(props);
        this.zoomLevel = 'Global';
        this.regionClick = this.regionClick.bind(this);
        this.renderChildAreas = this.renderChildAreas.bind(this);
    }

    componentDidMount() {
        this.renderMap();
    }

    componentWillUpdate(nextProps) {
        this.recalc(nextProps);
    }

    shouldComponentUpdate(nextProps) {
        if (this.props.regionOptions !== nextProps.regionOptions && nextProps.regionOptions[0].label !== 'Loading...') {
            this.renderChildAreas(nextProps)
        }
        if (this.props.mapData !== nextProps.mapData)
            this.props.loadRegions()

        return this.props.mapData !== nextProps.mapData
    }

    renderBorders(svg, path) {
        let g = svg.append("g").attr('class', 'my-g');
        g.append("path", ".graticule")
            .datum(feature(continentborder, continentborder.objects.land))
            .attr("class", "land")
            .attr("fill", 'none')
            .attr("stroke", "#000")
            .attr("d", path);
        return g
    }

    renderMap() {
        let {width, mapData, scale, center, height} = this.props;

        let el = this.refs.map;
        let node = ReactDOM.findDOMNode(el);
        let svg = d3.select(node);
        width = width ? width : 650;

        height = height ? height : width / 2;

        if (!scale)
            scale = height / Math.PI;
        let projection = d3.geoEquirectangular()
            .scale(scale);


        if (center)
            projection = projection.center(center);
        else
            projection = projection.translate([width / 2, height / 2]).rotate([70, 0, 0]);

        this.projection = projection;

        let path = d3.geoPath()
            .projection(projection)
            .pointRadius(4);

        svg.attr("id", 'map-svg');

        const g = this.renderBorders(svg, path)
        this.globalG = g;
        this.path = path;

        if (mapData) {
            this.createMap(mapData);
        }
    }

    createMap(mapData) {
        if(mapData) {

            this.globalG.selectAll('.geojson').remove().transition().duration(500)
            this.globalG.selectAll('.geojson').data(mapData)
                .enter()
                .insert('path', ':first-child')
                .attr('class', 'geojson')
                .attr('d', this.path)
                .attr('stroke', (d) => this.getColorByValue(d))
                .attr('fill', (d) => this.getColorByValue(d));

            this.globalG.selectAll(".geojson").data(mapData).transition().duration(5)
                .attr("d", this.path)
                .attr('class', 'geojson')
                .attr("stroke",  (d) => this.getColorByValue(d))
                .attr("fill",  (d) => this.getColorByValue(d));


            // significance circles
            const significanceMap = mapData.filter(d => d.score_sign !== '0.0');
            this.globalG.selectAll('.signCircles').remove();
            const signCircles = this.globalG.selectAll('.signCircles').data(significanceMap).enter().append('circle');
            signCircles
                .attr('cx', d => this.projection([parseFloat(d.coordinates[0][0]) + 2.5, parseFloat(d.coordinates[0][1]) + 2.5])[0])
                .attr('cy', d => this.projection([parseFloat(d.coordinates[0][0]) + 2.5, parseFloat(d.coordinates[0][1]) + 2.5])[1])
                .attr('r', 1)
                .attr('class', 'signCircles');

            this.setState({isDrawed: true})
        }
    }

    recalc(nextProps) {
        let {mapData} = this.props;
        let {isDrawed} = this.state;
        if (nextProps)
            mapData = nextProps.mapData;

        if (!isDrawed) {
            this.createMap(mapData);
        } else {

             // should we zoom?
            if (nextProps && (nextProps.region !== this.props.region || nextProps.region.label !== this.zoomLevel)) {
                let lonlat = [-180,180,-90,90];
                const zoomOffset = {
                    'Global': 200,
                    'North Atlantic': 115,
                    'Nino3.4': -340
                };

                if (nextProps.region)
                    lonlat = nextProps.region.value.split('_');
                lonlat = lonlat.map(v => parseFloat(v));

                const trans = this.projection.translate();
                const new_center = this.projection(
                    [lonlat[0] + (lonlat[1] + lonlat[0]) / 2 ,
                     lonlat[2] + (lonlat[3] - lonlat[2]) / 2]
                );

                const lo = this.projection([lonlat[0], lonlat[3]]);
                const ru = this.projection([lonlat[1], lonlat[2]]);

                const offset = nextProps.region ? zoomOffset[nextProps.region.label] : zoomOffset['Global']

                let dx = - lo[0] + ru[0],
                  dy = - lo[1] + ru[1],
                  x = new_center[0] + offset,
                  y = new_center[1],
                  scale = Math.max(1, Math.min(8, 0.65 / Math.max(dx / 650, dy / 325))),
                  translate = [650 / 2 - scale * x, 325 / 2 - scale * y];

                this.globalG.transition()
                    .duration(1000)
                    .style("stroke-width", 1)
                    .attr("transform", `translate(${translate[0]},${translate[1]}), scale(${scale})`)
            }

            let self = this;
            let mapSelection;
            if (nextProps && (nextProps.region !== this.props.region || nextProps.region.label !== this.zoomLevel)) {
                // remove old values because of new grid
                this.globalG.selectAll('.geojson').remove();
                mapSelection = this.globalG.selectAll(".geojson").data(mapData).enter().insert('path', ':first-child');
                this.zoomLevel = nextProps.region.label
            }else {
                mapSelection = this.globalG.selectAll(".geojson").data(mapData).transition().duration(500)
            }


            mapSelection
                .attr("d", this.path)
                .attr('class', 'geojson')
                .attr("stroke", function (d) {
                    return self.getColorByValue(d)
                })
                .attr("fill", function (d) {
                    return self.getColorByValue(d)
                });

            if (nextProps && (nextProps.region !== this.props.region || nextProps.region.label !== this.zoomLevel)) {
                this.globalG.selectAll(".geojson").data(mapData).transition().duration(5)
                    .attr("d", this.path)
                    .attr('class', 'geojson')
                    .attr("stroke",  (d) => this.getColorByValue(d))
                    .attr("fill",  (d) => this.getColorByValue(d));
            }

            // significance circles
            const significanceMap = mapData.filter(d => d.score_sign !== '0.0');
            this.globalG.selectAll('.signCircles').remove();
            const signCircles = this.globalG.selectAll('.signCircles').data(significanceMap).enter().append('circle');
            signCircles
                .attr('cx', d => this.projection([parseFloat(d.coordinates[0][0]) + 2.5, parseFloat(d.coordinates[0][1]) + 2.5])[0])
                .attr('cy', d => this.projection([parseFloat(d.coordinates[0][0]) + 2.5, parseFloat(d.coordinates[0][1]) + 2.5])[1])
                .attr('r', 1)
                .attr('class', 'signCircles');
        }

    }

    getColorByValue(d) {
        let RdBu_5 = ['#08519c', '#3182bd', '#6baed6', '#bdd7e7', '#eff3ff',
            '#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15'];
        const missing = '#bdbdbd';
        // missing values in evaluation
        if (d.score >= 1e+20) {
            return missing
        }
        if (d.score <= -1e+29)
            return missing;

        const minVal = -1,
            steps = 10,
            stepSize = 0.2,
            value = d.score;
        let test_val = minVal;
        for (let i = 0; i < steps; i++) {
            test_val += stepSize;
            if (test_val >= value) {
                return RdBu_5[i];
            }
        }
        if (value > test_val)
            return RdBu_5[9];
        return 'black';
    }


    regionClick(activeRegion) {
        this.props.selectRegion(activeRegion.value === this.props.region.value ? {value: "-180_180_-90_90", label: "Global"} : activeRegion)
    }


    renderChildAreas(nextProps) {

        let {regionOptions, mapData} = this.props.regionOptions;
        if (nextProps) {
            regionOptions = nextProps.regionOptions;
            mapData = nextProps.mapData;
        }

        if (regionOptions !== this.props.regionOptions)
            this.globalG.selectAll('.region-rect').remove();

        if(mapData) {
            const result = regionOptions.map(v => {
                if (v.value !== '-180_180_-90_90' && v.value) {

                    let lonlat = v.value.split('_');
                    lonlat = lonlat.map(v => parseFloat(v));
                    const coords = this.projection([lonlat[0], lonlat[3] - 2.5]);
                    const ru = this.projection([lonlat[1] + 5, lonlat[2] - 2.5]);
                    const rect = this.globalG.append("rect")
                        .attr("x", coords[0])
                        .attr("y", coords[1])
                        .attr("width", Math.abs(coords[0] - ru[0]))
                        .attr("height", Math.abs(coords[1] - ru[1]))
                        .attr("class", "region-rect")
                        .attr("style", "fill-opacity: 0; fill: #fff; stroke: #000; stroke-width: 1px; cursor: pointer")
                        .on('click', (e) => {
                            this.regionClick(v);
                        })
                }
            })
        }

    }

    render() {
        return (
            <div>
                <svg style={{width: '100%', backgroundColor: '#bdbdbd'}} viewBox="0 0 650 325" ref="map_parent">
                    <g id="map" ref="map"/>
                    {this.props.children}

                </svg>
                <Colorbar width={650} height={50} arrows={'both'} minVal={-1.} maxVal={1.} dx={0} arrows={this.props.metric && this.props.metric.value === 'correlation' ? null : 'left'}/>
            </div>

        )
    }
}


export default AbstractMap;
