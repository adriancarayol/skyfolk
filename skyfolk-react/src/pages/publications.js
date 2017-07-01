import React from 'react'
import ReactDOM from 'react-dom';

class Skyline extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleFormSubmit.bind(this);
        this.state = {
            board_owner: this.props.board_owner,
        };
    }

    handleFormSubmit(e) {
        e.preventDefault();
        //TODO...
        var payload = {
                a: 1,
                b: 2
        };
        fetch('/publications/filter/time/', {
            method: 'POST',
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
            .then(function(response) {
                return response.json()
            }).then(function(body) {
                console.log(body);
            });
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit} ref="filterForm">
                <input type='hidden' name='csrfmiddlewaretoken' value={window.csrf_token} />
                <FilterButton buttonName={'Tiempo'} buttonText={'Tiempo'} />
            </form>
            );
    }
}

const FilterButton = ({ buttonName, buttonText }) => (
    <button className="waffes-effect waves-light btn white black-text" type="submit" name={buttonName}>{buttonText}</button>
);


ReactDOM.render(
    <Skyline board_owner={ window.board_owner } />,
    document.getElementById('react'));
