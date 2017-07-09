import React from 'react'
import ReactDOM from 'react-dom';

class Skyline extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleFormSubmit.bind(this);
        this.onSubmit1 = this.onSubmit1.bind(this);
        this.onSubmit2 = this.onSubmit2.bind(this);
        this.onSubmit3 = this.onSubmit3.bind(this);

        this.state = {
            board_owner: this.props.board_owner,
            typeOfSubmit: '',
        };
    }

    onSubmit1() {
        this.setState({
            typeOfSubmit: 'time'
        }, this.refs.form.handleFormSubmit);
    }

    onSubmit2() {
        this.setState({
            typeOfSubmit: 'like'
        }, this.refs.form.handleFormSubmit);
    }

    onSubmit3() {
        this.setState({
            typeOfSubmit: 'relevance'
        }, this.refs.form.handleFormSubmit);
    }

    handleFormSubmit(e) {
        e.preventDefault();
        var data = {
            board_owner: this.state.board_owner
        };
        var url = '';
        if (this.state.typeOfSubmit === 'time') {
            url = '/publications/filter/time/';
        } else if (this.state.typeOfSubmit === 'like') {
            url = '/publications/filter/like/';
        } else if (this.state.typeOfSubmit === 'relevance') {
            url = '/publications/filter/relevance/';
        }
        fetch(url, {
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
                <form onSubmit={this.handleSubmit} ref="form">
                <FilterButton buttonName={'Tiempo'} buttonText={'Tiempo'} onClick={this.onSubmit1}/>
                <FilterButton buttonName={'Me gusta'} buttonText={'Me gusta'} onClick={this.onSubmit2}/>
                <FilterButton buttonName={'Relevancia'} buttonText={'Relevancia'} onClick={this.onSubmit3}/>
                </form>
               );
    }
}

const FilterButton = ({ buttonName, buttonText, onClick }) => (
        <button className="waffes-effect waves-light btn white black-text" type="submit" name={buttonName} onClick={onClick}>{buttonText}</button>
        );


ReactDOM.render(
        <Skyline board_owner={ window.board_owner } />,
        document.getElementById('react'));
