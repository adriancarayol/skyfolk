import React from 'react'
import ReactDOM from 'react-dom';
import { FilterButton } from './buttons.js';

class Skyline extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            board_owner: this.props.board_owner,
            typeOfSubmit: '',
            results: null
        };

        this.handleSubmit = this.handleFormSubmit.bind(this);
        this.onSubmit1 = this.onSubmit1.bind(this);
        this.onSubmit2 = this.onSubmit2.bind(this);
        this.onSubmit3 = this.onSubmit3.bind(this);
        this.setPublications = this.setPublications.bind(this);
    }

    setPublications(result) {
        this.setState({
            results: result
        });
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
            .then(response => response.json())
            .then(body => this.setPublications(body));
    }
    render() {
        const { board_owner, typeOfSubmit, results } = this.state;
        return (
            <div className="btns-filter col s12">
                <form className="center" onSubmit={this.handleSubmit} ref="form">
                    <FilterButton buttonName={'Me gusta'} buttonText={'Me gusta'} onClick={this.onSubmit2}/>
                    <FilterButton buttonName={'Relevancia'} buttonText={'Relevancia'} onClick={this.onSubmit3}/>
                </form>
                {
                results && <ItemPublication result={results} />
                }
            </div>
            );
    }
}

const ItemPublication = ({ result }) => (
    <ul className="collection">
    {
        result.map(item =>
        <li key={item.id} className="collection-item avatar">
            <img src={item.author__avatar} className="circle"/>
            <span className="title">{item.created}</span>
            <p>
                <a href={'/profile/' + item.author__username}>@{item.author__username}</a>
            </p>
            <h4 dangerouslySetInnerHTML={{__html: item.content}} />
            <a href={'/publication/' + item.id} className="pink-text secondary-content">{item.likes}
                <i className="material-icons right">favorite</i>
            </a>
        </li>
            )
    }
    </ul>
);

ReactDOM.render(
    <Skyline board_owner={ window.board_owner } />,
    document.getElementById('react'));
