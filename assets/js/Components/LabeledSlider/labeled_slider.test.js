import React from 'react';
import { shallow, render, mount} from 'enzyme';
import {expect} from 'chai';

import LabeledSlider from './index';

const wrapper = shallow(<LabeledSlider label={{id: "test label"}} value={1} onChange={() => console.log('change')}/>);

describe('(Component) LabeledSlider', () => {
  it('renders with minimal props', () => {
    expect(wrapper).to.have.length(1);
  });
});