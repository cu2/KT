var React = require('react');
var ReactDOM = require('react-dom');


var blankData = {
    filmData: {
        filmId: 0,
        filmData: {
            id: 0,
            origTitle: '',
            secondTitle: '',
            year: null,
            plot: '',
            poster: ''
        }
    }
};

var FilmPage = React.createClass({
    render: function() {
        if (this.props.data.filmId) {
            return <div>
                <p><img className="poster" src={this.props.data.filmData.poster} /></p>
                <p className="title">{this.props.data.filmData.origTitle} ({this.props.data.filmData.year})</p>
                <p className="title">{this.props.data.filmData.secondTitle}</p>
                <p>{this.props.data.filmData.plot}</p>
                <br className="clear" />
                <p><span className="clickable" onClick={ (e) => { e.preventDefault(); this.props.navTo({page: 'search'}); } }>Back</span></p>
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
            <p><img className="poster" src={this.props.data.poster} /></p>
            <p className="title">
                <span className="clickable" onClick={ (e) => { e.preventDefault(); this.props.navTo({page: 'film', filmId: this.props.data.id}); } }>
                    {this.props.data.origTitle} ({this.props.data.year})
                </span>
            </p>
            <p>{this.props.data.plot}</p>
            <br className="clear" />
        </div>;
    }
});

var FilmList = React.createClass({
    render: function() {
        if (this.props.searchResults.length) {
            return <div>
                {this.props.searchResults.map(function(film) {
                    return <FilmItem key={film.id} data={film} navTo={this.props.navTo} />;
                }.bind(this))}
            </div>;
        }
        return <div>
            <p>Loading...</p>
        </div>;
    }
});

var SearchPage = React.createClass({
    render: function() {
        return <div>
            <p>Cím: <input type="text" value={this.props.searchQuery.title} onChange={this.props.handleSearchChange} /></p>
            <FilmList searchResults={this.props.searchResults} navTo={this.props.navTo} />
        </div>;
    }
});

var KTApp = React.createClass({
    getInitialState: function() {
        return {
            location: {
                page: ''
            },
            pageTitle: '',
            searchQuery: {
                domain: '',
                title: '',
            },
            searchResults: [],
            filmData: blankData.filmData
        };
    },
    componentWillMount: function() {
        this.navTo({
            page: 'search'
        });
    },
    navTo: function(newLocation, newSearchQuery) {
        this.setState({
            location: newLocation
        });
        if (newSearchQuery) {
            this.setState({
                searchQuery: newSearchQuery
            });
        } else {
            newSearchQuery = this.state.searchQuery;
        }
        switch(newLocation.page) {
            case 'film':
                this.setState({
                    filmData: blankData.filmData
                });
                $.ajax('/m/api/?page=film&film_id=' + newLocation.filmId)
                    .done(function(data) {
                        this.setState({
                            filmData: {
                                filmId: data.filmId,
                                filmData: data.filmData
                            }
                        });
                        this.setState({
                            pageTitle: data.filmData.origTitle + ' (' + data.filmData.year + ')'
                        });
                    }.bind(this))
                    .fail(function() {
                        console.log('AJAX fail');
                    });
                break;
            case 'search':
                this.setState({
                    pageTitle: ''
                });
                $.ajax('/m/api/?page=search&domain=' + newSearchQuery.domain +
                    '&title=' + newSearchQuery.title)
                    .done(function(data) {
                        this.setState({
                            searchResults: data
                        });
                    }.bind(this))
                    .fail(function() {
                        console.log('AJAX fail');
                    });
                break;
        };
    },
    handleSearchChange: function(event) {
        var title = event.target.value
        if (title) {
            this.navTo(
                {
                    page: 'search'
                }, {
                    domain: 'film',
                    title: title
                }
            );
            // this.setState({
            //     searchQuery: {
            //         domain: 'film',
            //         title: title
            //     }
            // });
        } else {
            this.setState({
                searchQuery: {
                    domain: '',
                    title: ''
                }
            });
        }
    },
    render: function() {
        var content;
        switch(this.state.location.page) {
            case 'film':
                content = <FilmPage data={this.state.filmData} navTo={this.navTo} />;
                break;
            default:
                content = <SearchPage
                    searchResults={this.state.searchResults}
                    searchQuery={this.state.searchQuery}
                    handleSearchChange={this.handleSearchChange}
                    navTo={this.navTo}
                />;
        };
        return <div>
            <div>
                <span className="logo clickable" onClick={ () => {
                    this.navTo(
                        {
                            page: 'search'
                        }, {
                            domain: '',
                            title: ''
                        }
                    );
                } }>KT</span>
                <span>{this.state.pageTitle}</span>
            </div>
            <div>{content}</div>
        </div>;
    }
});


ReactDOM.render(<KTApp />, document.getElementById('container'));
