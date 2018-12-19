import React from 'react';
import '../../../../node_modules/react-vis/dist/style.css';
import {XYPlot, LineSeries, XAxis, YAxis, FlexibleWidthXYPlot, LineMarkSeries, MarkSeries, Crosshair} from 'react-vis';


export default class Timeseries extends React.Component {

    constructor(props) {
        super(props);
        this.state = {i: 0}
    }

    componentWillUpdate(nextProps) {
        if (nextProps.onLeaveValue !== this.props.onLeaveValue)
            this.setState({i: nextProps.onLeaveValue-1})
    }

    render() {

        const {data, ylabel, signData, onLeaveValue} = this.props;
        let min=1e20, max=-1e20;
        if (data) {
            data.map(v => {
                if (v.y < min)
                    min = v.y
                if (v.y > max)
                    max = v.y
            })
            min = Math.round((min-0.1)*10)/10;
            max = Math.round((max+0.1)*10)/10;
            max = Math.min(max, 1);
        }

        return (
            <FlexibleWidthXYPlot height={300} xDomain={[0.5, data.length + 0.5]} yDomain={[min, max]}
                                 onClick={(e) => this.props.onClick({leadtime: this.state.i+1})} animation={500}
                                 onMouseLeave={() => this.setState({i: onLeaveValue-1})} style={{cursor: 'pointer'}}>
                <Crosshair values={[data[this.state.i]]}>
                    <div className="rv-crosshair__inner rv-crosshair__inner rv-crosshair__inner__content">
                        <table style={{width: '100%'}}>
                            <tr>
                                <td>LY {this.state.i + 1}-{this.state.i + 4}</td>
                            </tr>
                            <tr>
                                <td>{ylabel}</td>
                                <td>{data[this.state.i].y}</td>
                            </tr>
                        </table>
                    </div>
                </Crosshair>

                <MarkSeries size={6} data={signData} colorType="literal"
                            style={{cursor: 'pointer'}} color="black"/>
                <LineMarkSeries onNearestX={(v, i) => this.setState({i: i.index})} data={data}
                                colorType="literal"
                                onValueClick={(e,v) => {return {title: 'Leadyear', value: 2}}}
                                style={{cursor: 'pointer'}}/>
                <XAxis tickValues={[1, 2, 3, 4, 5, 6, 7]} tickFormat={(t, i) => <tspan>{t}-{t+3}</tspan>}
                       title="Leadyears"/>
                <YAxis title={ylabel}/>

            </FlexibleWidthXYPlot>
        )
    }
}