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
            results: null,
            exlude: null
        }
        this.fetchRecommendations = this.fetchRecommendations.bind(this);
        this.setRecommendations = this.setRecommendations.bind(this);
    }


    setRecommendations(result) {
        if (typeof result !== 'undefined' && result.length > 0) {
            this.setState({
                results: result,
            });
        }
    }

    fetchRecommendations() {
        fetch('/follow/by_affinity/', {
            method: 'GET',
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
        })
            .then(response => response.json())
            .then(body => this.setRecommendations(body)); 
    }

    render() {
        const list = this.state.results; 
        const results = this.state.results;
        return (
            <div className="page">
                <div className="interactions center">
                    <FilterButton buttonName={'by_affinity'} buttonText={'Por afinidad'} onClick={() => this.fetchRecommendations()}/>
                </div>
                {
                    results && <Items list={list} />
                }
            </div>
        );
    }
}

const Items = ({ list }) => ( 
    <div className="recommendantions row">
        {
            list.map(item =>
                <div key={item.username} className="col l3 m10 s12 offset-m1">
                    <div className="personal-card">
                        <div className="row">
                            <div className="col s12">
                                <div className="header">
                                    <img className="back-profile-user lazyload" data-src={item.back_image} />
                                    <i className="material-icons affinity">mood</i>
                                    <div className="bg-user">
                                        <div className="profile-user-bg"><a href={'/profile/' + item.username}><img src={item.avatar} alt={item.username} /></a>
                                        </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col s12">
                            <div className="name-friend">
                                <a href={'/profile/' + item.username}>@{item.username}</a><br></br>
                                <p>{item.first_name} {item.last_name}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            )
        }
    </div>
);

ReactDOM.render(
    <RecommendationForm />,
    document.getElementById('by_affinity'));
