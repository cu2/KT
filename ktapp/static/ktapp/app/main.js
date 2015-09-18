(function() {

    function loadData(url, handleFunction, mockObject) {
        if (mockObject) {
            handleFunction(mockObject);
        } else {
            loaderTimerId = setTimeout(loaderTimer, 100);
            $.get(url, function(data) {
                clearTimeout(loaderTimerId);
                handleFunction(data);
                $('#loader').hide();
            });
        }
    }

    function showPage(name) {
        var pageId = 'page-' + name;
        $('.page').each(function() {
            if ($(this).attr('id') == pageId) {
                $(this).addClass('active-page');
            } else {
                $(this).removeClass('active-page');
            }
        });
    }

    function showTab(selectedTabId) {
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
    }

    function showPageAndTab(pageName, tabName) {
        window.scrollTo(0, 0);
        showTab(tabName);
        showPage(pageName);
    }

    var loaderTimerId;

    function loaderTimer() {
        $('#loader').show();
    }

/*****************************************************************************************/

    function loadFilm(id, tab) {
        showPageAndTab('film', tab);
        mockObject = FILM;
        mockObject = null;
        loadData('/api/films/' + id + '/', function(data) {
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
    }

    function loadBuzz() {
        mockObject = BUZZ;
        mockObject = null;
        loadData('/api/buzz/', function(data) {
            var x = '';
            for(var i=0; i < data.length; i++) {
                var comment = data[i];
                x += '<div class="comment_block">';
                x += '<div class="comment_block_author">';
                x += '<div>' + comment.created_at + ' ';
                x += '<span class="link film_link" data-id="' + comment.domain_object.id + '">' + comment.domain_object.title + '</span>';
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
    }

    function main() {
        loadBuzz();
    }

    $(function() {

        $('#logo').click(function() {
            $('#title').html('Kritikus Tömeg');
            showPageAndTab('index', 'index-buzz');
        });

        $('.tab').click(function() {
            showTab($(this).attr('id').substr(4));
        });

        $(document).on('click', '.film_link', function() {
            loadFilm($(this).data('id'), 'film-main');
            return false;
        });

        main();

    });

/*****************************************************************************************/

    FILM = {
        orig_title: 'Age of Ultron',
        other_titles: 'Az ultronok kora',
        year: 2014,
        countries: ['amerikai'],
        genres: ['akció']
    };

    BUZZ = [];

})();
