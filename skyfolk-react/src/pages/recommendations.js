import React from 'react';
import ReactDOM from 'react-dom';
import { FilterButton } from './buttons.js';

const itemStyle = {
    boxShadow: '0 1px 5px 0 rgba(165,214,167,1)'
};

class RecommendationForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            exclude: props.exclude,
            results: null
        };
        this.fetchRecommendations = this.fetchRecommendations.bind(this);
        this.setRecommendations = this.setRecommendations.bind(this);
    }

    componentDidMount() {
       this.fetchRecommendations();
    }

    setRecommendations(result) {
        var exclude_ids = this.state.exclude.slice();
        if (typeof result !== 'undefined' && result.length > 0) {
            result.map(item =>
                exclude_ids.push(item.id)
            );
            this.setState({
                results: result,
                exclude: exclude_ids
            });
        } else {
            if (typeof exclude_ids !== 'undefined' && exclude_ids.length > 0) {
                this.setState({
                    exclude: window.follows
                });
            }
        }
    }

    fetchRecommendations() {
        const exclude = this.state.exclude;
        fetch('/recommendations/users/', {
            method: 'POST',
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(exclude)
        })
            .then(response => response.json())
            .then(body => this.setRecommendations(body));
    }

    render() {
        const { exclude, results } = this.state;
        const list = results;

        return (
            <div className="page">
                <div className="interactions center">
                    <FilterButton buttonName={'show_more_users'} buttonText={'Mostrar más usuarios'} onClick={() => this.fetchRecommendations()}/>
                </div>
                {
                    results && <Items list={list} />
                }
            </div>
        );
    }
}

const Items = ({ list }) => (
    <div className="recommendantions">
        {
            list.map(item =>
                <div key={item.id} className="col l2 m12 s12">
                    <div  style={itemStyle} className="notice-item">
                        <div className="col l3 m2 s3 img">
                            <img src={item.avatar} alt={item.title} width="120" height="120" />
                        </div>
                        <div className="col l8 m9 s8 author">
                            <a href={'/profile/' + item.username}>@{item.username}</a>
                            <i>{item.first_name} {item.last_name}</i>
                        </div>
                    </div>
                </div>
            )
        }
    </div>
);

ReactDOM.render(
    <RecommendationForm exclude={window.follows} />,
    document.getElementById('recommendation-user'));
