var ktapp = {

    FILM: {
        orig_title: 'Age of Ultron',
        other_titles: 'Az ultronok kora',
        year: 2014,
        countries: ['amerikai'],
        genres: ['akció']
    },

    BUZZ: [],

    appState: {
        page: 'index',
        tab: 'index-buzz',
        filmId: null,
        commentPage: 0,
        loadedCommentPage: 0
    },

    /*****************************************************************************************/

    showPage: function(name) {
        ktapp.appState.page = name;
        var pageId = 'page-' + name;
        $('.page').each(function() {
            if ($(this).attr('id') === pageId) {
                $(this).addClass('active-page');
            } else {
                $(this).removeClass('active-page');
            }
        });
    },

    showTab: function(selectedTabId) {
        ktapp.appState.tab = selectedTabId;
        $('.main-content').each(function() {
            var currentTabId = $(this).attr('id').substr(13);
            if (currentTabId === selectedTabId) {
                $('#tab-' + currentTabId).addClass('active-tab');
                $(this).addClass('active-main-content');
            } else {
                $('#tab-' + currentTabId).removeClass('active-tab');
                $(this).removeClass('active-main-content');
            }
        });
    },

    showPageAndTab: function(pageName, tabName) {
        window.scrollTo(0, 0);
        ktapp.showTab(tabName);
        ktapp.showPage(pageName);
    },

    loaderTimerId: null,

    loaderTimer: function() {
        $('#loader').show();
    },

    loadData: function(url, handleFunction, mockObject) {
        if (mockObject) {
            handleFunction(mockObject);
        } else {
//            ktapp.loaderTimerId = setTimeout(ktapp.loaderTimer, 100);
            $.get(url, function(data) {
//                clearTimeout(ktapp.loaderTimerId);
                handleFunction(data);
//                $('#loader').hide();
            });
        }
    },

    nearBottomHandler: function() {
        if (ktapp.appState.page === 'film' && ktapp.appState.tab === 'film-comments' && ktapp.appState.commentPage === ktapp.appState.loadedCommentPage) {
            ktapp.appState.commentPage += 1;
            ktapp.loadData('/api/comment_page/film/' + ktapp.appState.filmId + '/?p=' + ktapp.appState.commentPage, function(data) {
                var x = $('#main-content-film-comments').html();
                for(var i=0; i < data.length; i++) {
                    var comment = data[i];
                    x += '<div class="comment_block">';
                    x += '<div class="comment_block_author">';
                    x += '<div>' + comment.created_at + ' ';
                    x += '</div>';
                    x += '<div class="comment_block_author_right">' + comment.created_by.username + '</div>';
                    x += '</div>';
                    x += '<div class="comment_block_content">';
                    x += '<p>' + comment.content + '</p>';
                    x += '</div>';
                    x += '</div>';
                }
                $('#main-content-film-comments').html(x);
                ktapp.appState.loadedCommentPage += 1;
            }, mockObject);
        }
    },

    didScroll: false,
    lastScrollTop: 0,
    hasScrolled: function() {
        var st = $(window).scrollTop();
        if (Math.abs(ktapp.lastScrollTop - st) <= 5) return;
        if (st > ktapp.lastScrollTop && st > 48) {
            if (st > 96) {
                $('#status-bar').animate({top: -96}, 200);
                $('.main-navigation').animate({top: -48}, 200);
            } else {
                $('#status-bar').animate({top: -48}, 200);
                $('.main-navigation').animate({top: 0}, 200);
            }
        } else {
            $('#status-bar').animate({top: 0}, 200);
            $('.main-navigation').animate({top: 48}, 200);
        }
        ktapp.lastScrollTop = st;
    },

    /*****************************************************************************************/

    loadFilm: function(id, tab) {
        ktapp.appState.filmId = id;
        ktapp.showPageAndTab('film', tab);
        mockObject = ktapp.FILM;
        mockObject = null;
        ktapp.loadData('/api/films/' + id + '/', function(data) {
            $('#title').html(data.orig_title + ' (' + data.year + ')');
            $('#orig_title').html(data.orig_title);
            $('#year').html(data.year);
            $('#other_titles').html(data.second_title + ((data.third_title != '')?('<br />\n' + data.third_title):''));
            $('#director').html(data.directors.map(function(obj) {return obj.name}).join(' - '));
            $('#plot_summary').html(data.plot_summary);
            $('#countries').html(data.countries.map(function(obj) {return obj.name}).join('-'));
            $('#genres').html(data.genres.map(function(obj) {return obj.name}).join(', '));
            var max_rating = Math.max(
                parseInt(data.number_of_ratings_1),
                parseInt(data.number_of_ratings_2),
                parseInt(data.number_of_ratings_3),
                parseInt(data.number_of_ratings_4),
                parseInt(data.number_of_ratings_5)
            );
            $('#rating_bar_1').width(Math.round(200.0 / max_rating * parseInt(data.number_of_ratings_1)));
            $('#rating_bar_2').width(Math.round(200.0 / max_rating * parseInt(data.number_of_ratings_2)));
            $('#rating_bar_3').width(Math.round(200.0 / max_rating * parseInt(data.number_of_ratings_3)));
            $('#rating_bar_4').width(Math.round(200.0 / max_rating * parseInt(data.number_of_ratings_4)));
            $('#rating_bar_5').width(Math.round(200.0 / max_rating * parseInt(data.number_of_ratings_5)));
            $('#number_of_ratings_1').html(data.number_of_ratings_1);
            $('#number_of_ratings_2').html(data.number_of_ratings_2);
            $('#number_of_ratings_3').html(data.number_of_ratings_3);
            $('#number_of_ratings_4').html(data.number_of_ratings_4);
            $('#number_of_ratings_5').html(data.number_of_ratings_5);
            $('#num_rating').html(data.number_of_ratings);
            $('#avg_rating').html(data.average_rating);
        }, mockObject);
        ktapp.appState.commentPage = 1;
        ktapp.loadData('/api/comment_page/film/' + id + '/', function(data) {
            var x = '';
            for(var i=0; i < data.length; i++) {
                var comment = data[i];
                x += '<div class="comment_block">';
                x += '<div class="comment_block_author">';
                x += '<div>' + comment.created_at + ' ';
                x += '</div>';
                x += '<div class="comment_block_author_right">' + comment.created_by.username + '</div>';
                x += '</div>';
                x += '<div class="comment_block_content">';
                x += '<p>' + comment.content + '</p>';
                x += '</div>';
                x += '</div>';
            }
            $('#main-content-film-comments').html(x);
            ktapp.appState.loadedCommentPage = 1;
        }, mockObject);
    },

    loadBuzz: function() {
        mockObject = ktapp.BUZZ;
        mockObject = null;
        ktapp.loadData('/api/buzz/', function(data) {
            var x = '';
            for(var i=0; i < data.length; i++) {
                var comment = data[i];
                x += '<div class="comment_block">';
                x += '<div class="comment_block_author">';
                x += '<div>' + comment.created_at + ' ';
                if (comment.domain === 'F') {
                    x += '<span class="link link_film_comments" data-id="' + comment.domain_object.id + '">' + comment.domain_object.title + '</span>';
                } else if (comment.domain === 'T') {
                    x += '[<span class="link link_topic" data-id="' + comment.domain_object.id + '">' + comment.domain_object.title + '</span>]';
                } else {
                    x += '[<span class="link link_poll" data-id="' + comment.domain_object.id + '">' + comment.domain_object.title + '</span>]';
                }
                x += '</div>';
                x += '<div class="comment_block_author_right">' + comment.created_by.username + '</div>';
                x += '</div>';
                x += '<div class="comment_block_content">';
                x += '<p>' + comment.content + '</p>';
                x += '</div>';
                x += '</div>';
            }
            $('#main-content-index-buzz').html(x);
        }, mockObject);
    },

    main: function() {
        $('#logo').click(function() {
            $('#title').html('Kritikus Tömeg');
            ktapp.showPageAndTab('index', 'index-buzz');
        });

        $('.tab').click(function() {
            ktapp.showTab($(this).attr('id').substr(4));
        });

        $(document).on('click', '.link_film_main', function() {
            ktapp.loadFilm($(this).data('id'), 'film-main');
            return false;
        });
        $(document).on('click', '.link_film_comments', function() {
            ktapp.loadFilm($(this).data('id'), 'film-comments');
            return false;
        });

        $(window).scroll(function() {
            ktapp.didScroll = true;
            if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
                ktapp.nearBottomHandler();
            }
        });

        setInterval(function() {
            if (ktapp.didScroll) {
                ktapp.hasScrolled();
                ktapp.didScroll = false;
            }
        }, 250);

        ktapp.loadBuzz();
    }

};

$(function() {
    ktapp.main();
});
