var React = require('react');
var ReactDOM = require('react-dom');


var FilmPage = React.createClass({
    render: function() {
        if (this.props.data.filmId) {
            return <div>
                <h1>{this.props.data.filmData.origTitle} ({this.props.data.filmData.year})</h1>
                <p>{this.props.data.filmData.plot}</p>
                <p><span className="clickable" onClick={ (e) => { e.preventDefault(); this.props.navTo({page: 'index'}); } }>Back to Index</span></p>
            </div>;
        }
        return <div>
            <p>Loading film...</p>
        </div>;
    }
});

var FilmItem = React.createClass({
    render: function() {
        return <div>
            <h2>
                <span className="clickable" onClick={ (e) => { e.preventDefault(); this.props.navTo({page: 'film', filmId: this.props.data.id}); } }>
                    {this.props.data.origTitle} ({this.props.data.year})
                </span>
            </h2>
            <p>{this.props.data.plot}</p>
        </div>;
    }
});

var IndexPage = React.createClass({
    render: function() {
        if (this.props.data.listOfFilms.length) {
            return <div>
                {this.props.data.listOfFilms.map(function(film) {
                    return <FilmItem key={film.id} data={film} navTo={this.props.navTo} />;
                }.bind(this))}
            </div>;
        }
        return <div>
            <p>Loading...</p>
        </div>;
    }
});

var KTApp = React.createClass({
    getInitialState: function() {
        return {
            location: {
                page: ''
            },
            indexData: {
                listOfFilms: []
            },
            filmData: {
                filmId: 0,
                filmData: {
                    id: 0,
                    origTitle: '',
                    year: null,
                    plot: ''
                }
            }
        };
    },
    componentWillMount: function() {
        this.navTo({
            page: 'index'
        });
    },
    navTo: function(newLocation) {
        this.setState({
            location: newLocation
        });
        switch(newLocation.page) {
            case 'film':
                this.setState({
                    filmData: {
                        filmId: 0,
                        filmData: {
                            id: 0,
                            origTitle: '',
                            year: null,
                            plot: ''
                        }
                    }
                });
                $.ajax('/m/api/?page=film&film_id=' + newLocation.filmId)
                    .done(function(data) {
                        this.setState({
                            filmData: {
                                filmId: data.filmId,
                                filmData: data.filmData
                            }
                        });
                    }.bind(this))
                    .fail(function() {
                        console.log('AJAX fail')
                    });
                break;
            default:
                $.ajax('/m/api/?page=index')
                    .done(function(data) {
                        this.setState({
                            indexData: {
                                listOfFilms: data.listOfFilms
                            }
                        });
                    }.bind(this))
                    .fail(function() {
                        console.log('AJAX fail')
                    });
        };
    },
    render: function() {
        switch(this.state.location.page) {
            case 'film':
                return <FilmPage data={this.state.filmData} navTo={this.navTo} />;
            default:
                return <IndexPage data={this.state.indexData} navTo={this.navTo} />;
        };
    }
});


ReactDOM.render(<KTApp />, document.getElementById('container'));
