import React from 'react';
import ReactDOM from 'react-dom';
import { FilterButton } from './buttons.js';

class Recommendation extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user_id: this.props.user_id
        };
    }
    render() {
        return (
            <form onSubmit={this.handleSubmit} ref="form">
                <FilterButton buttonName={'actualizar'} buttonText={'Actualizar'} onClick={this.onSubmit}/>
            </form>
        );
    }
}

ReactDOM.render(
    <Recommendation user_id={ window.user_id } />,
    document.getElementById('recommendation-user'));
