import React from 'react';
import ReactDOM from 'react-dom';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux'
import {
    Grid,
    Row,
    Col,
    Button,
    ButtonToolbar,
    Modal,
    ButtonGroup,
    FormGroup,
    ControlLabel,
    FormControl,
} from 'react-bootstrap';
import Select from 'react-select';
//import {variableOptions, hindcastSetOptions, metricOptions} from './reducers'
import {changeParamAsync, getHindcastData, loadOptions} from './actions'
import AbstractMap from '../../Components/AbstactMap'
import Timeseries from '../../Components/Timeseries';
import LabeledSlider from '../../Components/LabeledSlider'

class HindcastFrontend extends React.Component {

    constructor(props) {
        super(props);
    }
    
    render() {

        const {mapData, timeseriesData} = this.props.hindcastFrontend.settingsReducer;
        const {variable, hindcastSet,metric, reference, leadtime, region} = this.props.hindcastFrontend.selectMenuReducer
        const {changeParamAsync, getHindcastData, loadOptions} = this.props.actions;
        const leadtimeVal = leadtime.selected;


        const data = timeseriesData.score;
        const data2 = timeseriesData.sign;

        const obsDataset = variable && variable.value == 'tas' ? 'HadCrut4' : 'GPCC';
        const evaTime = variable && variable.value == 'tas' ? '1968-2016' : '1968-2013';
        let refText;
        if (reference.selected && metric.selected)
            refText = reference.selected.value === 'clim' && metric.selected.value === 'correlation' ? '' : ` with ${reference.selected.label} as reference`;

        return (
            <Grid>

                <Row>
                    <Col md={3} xs={12}>
                        <FormGroup controlId="formControlsSelect">
                            <ControlLabel>Variable</ControlLabel>
                            <Select
                                name="variable"
                                value={variable.selected}
                                options={variable.options}
                                isLoading={variable.isLoading}
                                onChange={(val) => {changeParamAsync({variable: val})}}
                                onOpen={() => loadOptions('variable')}
                            />
                        </FormGroup>
                        <FormGroup controlId="formControlsSelect">
                            <ControlLabel>Hindcast-Set</ControlLabel>
                            <Select
                                name="hindcastSet"
                                value={hindcastSet.selected}
                                options={hindcastSet.options}
                                isLoading={hindcastSet.isLoading}
                                onChange={(val) => changeParamAsync({hindcastSet: val})}
                                onOpen={() => loadOptions('hindcastSet')}
                            />
                        </FormGroup>
                        <FormGroup controlId="formControlsSelect">
                            <ControlLabel>Reference</ControlLabel>
                            <Select
                                name="reference"
                                value={reference.selected}
                                options={reference.options}
                                isLoading={reference.isLoading}
                                onChange={(val) => changeParamAsync({reference: val})}
                                onOpen={() => loadOptions('reference')}
                            />
                        </FormGroup>
                        <FormGroup controlId="formControlsSelect">
                            <ControlLabel>Region</ControlLabel>
                            <Select
                                name="reference"
                                value={region.selected}
                                options={region.options}
                                isLoading={region.isLoading}
                                onChange={(val) => changeParamAsync({region: val})}
                                onOpen={() => loadOptions('region')}
                            />
                        </FormGroup>
                        <FormGroup controlId="formControlsSelect">
                            <ControlLabel>Metric</ControlLabel>
                            <Select
                                name="metric"
                                value={metric.selected}
                                options={metric.options}
                                isLoading={metric.isLoading}
                                onChange={(val) => changeParamAsync({metric: val})}
                                onOpen={() => loadOptions('metric')}
                            />

                        </FormGroup>

                        <LabeledSlider disabled={data === undefined ? true : false} step={1} min={1} max={7} value={leadtime.selected} label="Leadtime" onChange={(e,v) => changeParamAsync({leadtime: v})}/>

                    </Col>


                    <Col md={9} xs={12}>

                        {data ? <h2>{`${metric.selected.label} - LY ${leadtimeVal}-${leadtimeVal+3} - ${variable.selected.label}`}</h2> : null}

                        <AbstractMap mapData={mapData} metric={metric.selected} region={region.selected}
                            regionOptions={region.options || []}
                            selectRegion={(v) => changeParamAsync({region: v})}
                            loadRegions={() => loadOptions('region')}
                        />
                        {data ?
                        <p>Map shows the ensemble mean {metric.selected.label} of {variable.selected.label} for leadyear {leadtimeVal}-{leadtimeVal+3}{" "}
                           for the hindcast-set {hindcastSet.selected.label}{refText}.
                            Observational dataset is {obsDataset} and the evaluation period {evaTime}.
                           Crosses denote significance at the 95% level.</p> : null}

                        {data ? <h2>{`${metric.selected.label} - ${region.selected.label} Mean - ${variable.selected.label}`}</h2> : null}
                        {data ?

                        <Timeseries
                            data={data}
                            signData={data2}
                            ylabel={metric.selected ? metric.selected.label : null}
                            onClick={changeParamAsync}
                            onLeaveValue={leadtime.selected}
                        /> : null}
                        {data ?
                        <p>Plot shows the ensemble mean {metric.selected.label} of {variable.selected.label}{" "}
                           for the hindcast-set {hindcastSet.selected.label}{refText}.
                            Observational dataset is {obsDataset} and the evaluation period {evaTime}.
                           Black circles denote significance at the 95% level.</p> : null}
                    </Col>
                </Row>
            </Grid>
        )
    }
}

const mapStateToProps = state => ({
    hindcastFrontend: state.hindcastFrontendReducer
});

const mapDispatchToProps = dispatch => ({
    actions: bindActionCreators({changeParamAsync, getHindcastData, loadOptions}, dispatch)
});

export default connect(mapStateToProps, mapDispatchToProps)(HindcastFrontend);