var ktApp = {
    windowResized: false,
    windowScrolled: false,
    lastScrollTop: 0,
    hasScrolled: function() {
        var st = $(window).scrollTop();
        if (Math.abs(ktApp.lastScrollTop - st) <= 5) {
            return;
        }
        if (st <= 60) {
            $('#top-navbar').removeClass('nav-mini');
        } else if (st > ktApp.lastScrollTop) {
            $('#top-navbar').addClass('nav-mini');
        } else {
            $('#top-navbar').removeClass('nav-mini');
        }
        ktApp.lastScrollTop = st;
    },
    resizeSearchAutocomplete: function() {
        var search_autocomplete_results = $('#search_autocomplete_results');
        if (search_autocomplete_results.css('display') === 'block') {
            var search_input = $('#search_input');
            var input_offset = search_input.offset();
            var input_dim = {
                width: search_input.outerWidth(true) + 1,
                height: search_input.outerHeight(true)
            };
            search_autocomplete_results.offset({
                top: input_offset.top + input_dim.height,
                left: input_offset.left - 1
            });
            search_autocomplete_results.outerWidth(input_dim.width);
        }
    },
    searchInputChanged: false,
    getSearchResults: function() {
        var search_autocomplete_results = $('#search_autocomplete_results');
        var search_input = $('#search_input');
        if (search_input.val().trim().length < 2) {
            search_autocomplete_results.hide();
        } else {
            search_input.addClass('loading');
            $.getJSON('/api/autocomplete/search/', {
                q: search_input.val().trim()
            }, function(data) {
                search_input.removeClass('loading');
                if (data.q === search_input.val().trim()) {
                    if (data.results.length) {
                        var search_autocomplete_results_html = '';
                        for(var domain_idx = 0; domain_idx < data.results.length; domain_idx++) {
                            var domain = data.results[domain_idx].domain;
                            var results = data.results[domain_idx].results;
                            if (domain === 'films') search_autocomplete_results_html += '<h2>Filmek</h2>';
                            if (domain === 'artists') search_autocomplete_results_html += '<h2>Színészek/Rendezők</h2>';
                            if (domain === 'roles') search_autocomplete_results_html += '<h2>Szereplők</h2>';
                            if (domain === 'sequels') search_autocomplete_results_html += '<h2>Adaptációk, folytatások, remake-ek</h2>';
                            if (domain === 'topics') search_autocomplete_results_html += '<h2>Topikok</h2>';
                            if (domain === 'polls') search_autocomplete_results_html += '<h2>Szavazások</h2>';
                            if (domain === 'users') search_autocomplete_results_html += '<h2>Felhasználók</h2>';
                            search_autocomplete_results_html += '<ul>';
                            for(var i = 0; i < results.length; i++) {
                                search_autocomplete_results_html += '<li><a href="' + results[i].url + '">';
                                search_autocomplete_results_html += '<span class="search_autocomplete_results_thumbnail_container">';
                                if (results[i].thumbnail) search_autocomplete_results_html += '<img src="' + results[i].thumbnail + '" />';
                                search_autocomplete_results_html += '</span>';
                                search_autocomplete_results_html += results[i].title;
                                if (results[i].subtitle) search_autocomplete_results_html += '<br /><span class="search_autocomplete_results_subtitle">' + results[i].subtitle + '</span>';
                                if (results[i].subsubtitle) search_autocomplete_results_html += '<br /><span class="search_autocomplete_results_subtitle">' + results[i].subsubtitle + '</span>';
                                search_autocomplete_results_html += '</a></li>';
                            }
                            search_autocomplete_results_html += '</ul>';
                        }
                        search_autocomplete_results.html(search_autocomplete_results_html);
                        search_autocomplete_results.show();
                        ktApp.resizeSearchAutocomplete();
                    } else {
                        search_autocomplete_results.hide();
                    }
                }
            });
        }
    }
};

$(function() {
    $('#search_input').on('input propertychange paste', function() {
        ktApp.searchInputChanged = true;
    });
    setInterval(function() {
        if (ktApp.searchInputChanged) {
            ktApp.getSearchResults();
            ktApp.searchInputChanged = false;
        }
    }, 500);

    $(window).resize(function() {
        ktApp.windowResized = true;
    });
    setInterval(function() {
        if (ktApp.windowResized) {
            ktApp.resizeSearchAutocomplete();
            ktApp.windowResized = false;
        }
    }, 100);

    ktApp.lastScrollTop = $(window).scrollTop();
    $(window).scroll(function(){
        ktApp.windowScrolled = true;
    });
    setInterval(function() {
        if (ktApp.windowScrolled) {
            ktApp.hasScrolled();
            ktApp.resizeSearchAutocomplete();
            setTimeout(function() {
                ktApp.resizeSearchAutocomplete();
            }, 500);
            ktApp.windowScrolled = false;
        }
    }, 250);

    $('.navbar-profile .dropdown-toggle').click(function() {
        setTimeout(function() {
            if ($('.navbar-profile>li').hasClass('open')) {
                $('.navbar-profile .login-username').focus();
            }
        }, 100);
    });

});
