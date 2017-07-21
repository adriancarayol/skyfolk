import React from 'react';
import ReactDOM from 'react-dom';
import { FilterButton } from './buttons.js';

class RecommendationForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user_id: this.props.user_id,
            results: null
        };
        this.fetchRecommendations = this.fetchRecommendations.bind(this);
        this.setRecommendations = this.setRecommendations.bind(this);
    }

    setRecommendations(result) {
        this.setState({
            results: result
        });
    }

    fetchRecommendations() {
        var data = {
            user_ir: this.state.user_id
        };
        fetch('/recommendations/users/', {
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
            }).then(body => this.setRecommendations(body)); 
    }

    render() {
        const { user_id, results } = this.state;
        const list = results; 

        return (
            <div className="page">
            <div className="interactions">
                <FilterButton buttonName={'actualizar'} buttonText={'Actualizar'} onClick={() => this.fetchRecommendations()}/>
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
                <div key={item.id} className="notice-item">
                    <div className="col l3 m2 s3 img">
                    </div>
                    <div className="col l8 m9 s8 author">
                        <a href={'/profile/' + item.title}>{item.title}</a>
                    </div>
                </div>
            )
        }
        </div>
);

ReactDOM.render(
    <RecommendationForm user_id={ window.user_id } />,
    document.getElementById('recommendation-user'));
