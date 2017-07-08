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
        var data = {
                board_owner: window.board_owner
        };
        fetch('/publications/filter/time/', {
            method: 'POST',
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
            .then(function(response) {
                return response.json()
            }).then(function(body) {
                const pubs = body.map((elem) =>
                    <li key={elem.id}>
                        <p>{elem.content}</p>
                    </li>
                );
                ReactDOM.render(
                    <ul>{pubs}</ul>,
                    document.getElementById('react')
                );
            });
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
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
