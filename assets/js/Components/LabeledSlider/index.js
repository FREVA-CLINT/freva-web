import React from 'react';
import PropTypes from 'prop-types';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import Slider from 'material-ui/Slider';
import {ControlLabel} from 'react-bootstrap';
import Checkbox from 'material-ui/Checkbox';


const LabeledSlider = (props) => {
    const {label, value, theme, disabled, onChange, max,
        withCheckBox, checked, onCheck, step, min, markDefault} = props;
    const textValue = value !== 0 ? parseFloat(value)*100 : '0';
    return (
        <div>
            <ControlLabel>
                <table>
                    <tbody>
                        <tr>
                            <td style={!checked ? {color: 'grey'} : null}>

                                {label}: {value}-{value+3}

                            </td>
                            {withCheckBox ?
                                <td>
                                    <Checkbox
                                        disabled={disabled}
                                        checked={checked}
                                        onCheck={onCheck}
                                    />
                                </td> : null
                            }
                        </tr>
                    </tbody>
                </table>
            </ControlLabel>
            <MuiThemeProvider muiTheme={theme}>
                <span>
                    <Slider disabled={disabled || !checked}
                        step={step}
                        min={min}
                        max={max}
                        value={value}
                        sliderStyle={{marginTop:0, marginBottom:0, zIndex: 0}}
                        onChange={onChange}
                    />
                    {markDefault ?
                    <div style={{position: 'relative', overflow: 'visible', height: 12, width: 12, top: -6, left: 3}} onClick={() => onChange(0)}>
                        <div style={{position: 'absolute', height: '100%', width: '100%', top: 0, left: 0, transition: 'transform 450ms cubic-bezier(0.23, 1, 0.32, 1) 0ms, opacity 450ms cubic-bezier(0.23, 1, 0.32, 1) 0ms', WebkitTransition: 'transform 450ms cubic-bezier(0.23, 1, 0.32, 1) 0ms, opacity 450ms cubic-bezier(0.23, 1, 0.32, 1) 0ms; opacity: 1; transform: scale(0.85)'}}>
                            <div style={{position: 'absolute', height: 18, width: '158%', borderTopLeftRadius: '50%', borderTopRightRadius: '50%', borderBottomRightRadius: '50%', borderBottomLeftRadius: '50%', opacity: 1, transition: 'transform 750ms cubic-bezier(0.445, 0.05, 0.55, 0.95) 0ms', WebkitTransition: 'transform 750ms cubic-bezier(0.445, 0.05, 0.55, 0.95) 0ms', top: -12, left: -12, transform: 'scale(1)', backgroundColor: 'rgb(0,150,0)'}}>
                            </div>
                        </div>
                    </div> : null}
                </span>
            </MuiThemeProvider>
        </div>
    )
};

LabeledSlider.defaultProps = {
    disabled: false,
    withCheckBox: false,
    step: 0.1,
    min: 0.,
    checked: true,
    markDefault: false
};

LabeledSlider.propTypes = {
    label: PropTypes.object.isRequired,
    value: PropTypes.number.isRequired,
    min: PropTypes.number,
    step: PropTypes.number,
    theme: PropTypes.object,
    disabled: PropTypes.bool,
    onChange: PropTypes.func.isRequired,
    helpText: PropTypes.object,
    withCheckBox: PropTypes.bool,
    checked: PropTypes.bool,
    onCheck: PropTypes.func,
    markDefault: PropTypes.bool
};

export default LabeledSlider;