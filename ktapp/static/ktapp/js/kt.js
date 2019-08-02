var ktApp = {
    vote: function(film_id, rating, vote_redate_to) {
        $.post('/szavaz', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            ajax: '1',
            film_id: film_id,
            rating: rating,
            vote_redate_to: vote_redate_to
        }, function(data) {
            if (data.success) {
                document.location.reload();
            }
        });
    },
    followUser: function(user_id) {
        $('.follow_loader').show();
        $.post('/uj_kedvenc', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            ajax: '1',
            whom: user_id
        }, function(data) {
            document.location.reload();
        });
    },
    unfollowUser: function(user_id) {
        $('.follow_loader').show();
        $.post('/torol_kedvenc', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            ajax: '1',
            whom: user_id
        }, function(data) {
            document.location.reload();
        });
    },
    windowResized: false,
    windowScrolled: false,
    lastScrollTop: 0,
    pageY: 0,
    hasScrolled: function() {
        var st = $(window).scrollTop();
        if (st <= 100) {
            $('#top-navbar').removeClass('nav-mini');
            ktApp.lastScrollTop = st;
            return;
        }
        if (Math.abs(ktApp.lastScrollTop - st) <= 200) {
            ktApp.lastScrollTop = st;
            return;
        }
        if (st > ktApp.lastScrollTop) {
            $('#top-navbar').addClass('nav-mini');
            $('ul.nav li.dropdown .dropdown-menu').stop(true, true).hide();
            $('#search-autocomplete-results').hide();
        } else {
            $('#top-navbar').removeClass('nav-mini');
        }
        ktApp.lastScrollTop = st;
    },
    resizeSearchAutocomplete: function() {
        var search_autocomplete_results = $('#search-autocomplete-results');
        if (search_autocomplete_results.css('display') === 'block') {
            var search_input = $('#search-input');
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
        var search_autocomplete_results = $('#search-autocomplete-results');
        var mobile_search_results = $('#mobile-search-results');
        var search_input = $('#search-input');
        var search_input_mobile = $('#search-input-mobile');
        if (search_input.val().trim().length < 2) {
            search_autocomplete_results.hide();
            mobile_search_results.html('');
        } else {
            search_input.addClass('loading');
            search_input_mobile.addClass('loading');
            $.getJSON('/api/autocomplete/search/', {
                q: search_input.val().trim()
            }, function(data) {
                search_input.removeClass('loading');
                search_input_mobile.removeClass('loading');
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
                                if (domain === 'artists') {
                                    search_autocomplete_results_html += '<span class="search-autocomplete-results-artist-thumbnail-container">';
                                    if (results[i].thumbnail) {
                                        search_autocomplete_results_html += '<img src="' + results[i].thumbnail + '" style="margin-left: ' + (results[i].thumbnail_margin_left) + 'px" />';
                                    }
                                    search_autocomplete_results_html += '</span>';
                                } else {
                                    search_autocomplete_results_html += '<span class="search-autocomplete-results-thumbnail-container">';
                                    if (results[i].thumbnail) {
                                        search_autocomplete_results_html += '<img src="' + results[i].thumbnail + '" />';
                                    }
                                    search_autocomplete_results_html += '</span>';
                                }
                                search_autocomplete_results_html += results[i].title;
                                if (results[i].subtitle) search_autocomplete_results_html += '<br /><span class="search-autocomplete-results-subtitle">' + results[i].subtitle + '</span>';
                                if (results[i].subsubtitle) search_autocomplete_results_html += '<br /><span class="search-autocomplete-results-subtitle">' + results[i].subsubtitle + '</span>';
                                search_autocomplete_results_html += '</a></li>';
                            }
                            search_autocomplete_results_html += '</ul>';
                        }
                        search_autocomplete_results.html(search_autocomplete_results_html);
                        search_autocomplete_results.show();
                        mobile_search_results.html(search_autocomplete_results_html);
                        ktApp.resizeSearchAutocomplete();
                    } else {
                        search_autocomplete_results.hide();
                        mobile_search_results.html('');
                    }
                }
            });
        }
    }
};

$(function() {
    $('.vote_star').click(function() {
        var film_id = $(this).data('film');
        var rating = $(this).data('rating');
        if (rating == 0) {
            if (! confirm('Biztos vagy benne?')) {
                return;
            }
        }
        var vote_redate_to = $('#vote_redate_to').val();
        $('.vote_star_loader').show();
        ktApp.vote(film_id, rating, vote_redate_to);
    });
    $('.vote_star_menu_toggle').click(function() {
        $('.vote_star_menu').toggle();
    });

    $('.wish_star').click(function() {
        $('.wish_star_loader').show();
        var film_id = $(this).data('film');
        var action = $(this).data('action');
        $.ajax({
            type: 'POST',
            url: '/kivan',
            data: {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                film_id: film_id,
                wish_type: 'Y',
                action: action,
                ajax: '1'
            },
            success: function(data) {
                if (data.success) {
                    document.location.reload();
                }
            },
            dataType: 'json'
        });
    });

    $('#search-input-mobile').on('input propertychange paste', function() {
        $('#search-input').val($('#search-input-mobile').val());
        ktApp.searchInputChanged = true;
    });
    $('#search-input').on('input propertychange paste', function() {
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

    $('.hamburger-menu-open').click(function() {
        ktApp.pageY = $(window).scrollTop();
        $('#hamburger-menu').show();
        $('#hamburger-menu-ul').scrollTop(0).animate({
            left: '0',
            right: '48px'
        }, 'fast');
        $('html').css('overflowY', 'hidden');
        return false;
    });
    $('.hamburger-menu-close').click(function() {
        $('#hamburger-menu-ul').animate({
            left: '-100%',
            right: '100%'
        }, 'fast', function() {
            $('#hamburger-menu').hide();
        });
        $('html').css('overflowY', 'auto');
        $(window).scrollTop(ktApp.pageY);
        return false;
    });

    $('.mobile-search-open').click(function() {
        ktApp.pageY = $(window).scrollTop();
        $('#mobile-search-screen').show();
        $('#search-input-mobile').focus();
        $('html').css('overflowY', 'hidden');
        return false;
    });
    $('.mobile-search-close').click(function() {
        $('#mobile-search-screen').hide();
        $('#search-input-mobile').blur().val('');
        $('#search-input').val('');
        $('#mobile-search-results').html('');
        ktApp.searchInputChanged = true;
        $('html').css('overflowY', 'auto');
        $(window).scrollTop(ktApp.pageY);
        return false;
    });

    var kt_email = '';
    kt_email += 'krit';
    kt_email += 'ikust';
    kt_email += 'ome';
    kt_email += 'g@g';
    kt_email += 'ma';
    kt_email += 'il.c';
    kt_email += 'om';
    $('#kt_email').html(kt_email);

    $('.follow_user').click(function() {
        $('.follow_user').hide();
        ktApp.followUser($(this).data('id'));
    });
    $('.unfollow_user').click(function() {
        $('.unfollow_user').hide();
        ktApp.unfollowUser($(this).data('id'));
    });

    $('.show_spoilers').click(function() {
        $('.spoiler').removeClass('spoiler').addClass('visible_spoiler');
        $('.show_spoilers_section').css('visibility', 'hidden');
    });
    $('#close_topic_opener').click(function() {
        $('#close_topic_div').toggle();
    });
    $('#set_topic_game_mode_opener').click(function() {
        $('#set_topic_game_mode_div').toggle();
    });
    $('.move_to_off').click(function() {
        $('.move_to_off').hide();
        $('.move_to_off_loader').show();
        var list_of_ids = '';
        $('.comment_to_move_to_off:checked').each(function() {
            list_of_ids += $(this).data('id') + ',';
        });
        $.post('/offba', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            list_of_ids: list_of_ids
        }, function(data) {
            if (data.success) {
                document.location.reload();
            }
        });
    });
    $('tr').on('click', 'td.wish span, td.wish_active span', function() {
        var parent_td = $(this).closest('td');
        if (parent_td.hasClass('wish')) {
            $(this).closest('td').removeClass('wish').addClass('wish_active');
        } else {
            $(this).closest('td').removeClass('wish_active').addClass('wish');
        }
        $.ajax({
            type: 'POST',
            url: '/kivan',
            data: {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                film_id: $(this).data('id'),
                wish_type: 'Y',
                action: parent_td.hasClass('wish_active')?'+':'-',
                ajax: '1'
            },
            context: $(this),
            success: function(data) {
                var parent_td = $(this).closest('td');
                if (data.success) {
                    if (parent_td.hasClass('wish_active')) {
                        $(this).html('&#9733;');
                    } else {
                        $(this).html('&#9734;');
                    }
                } else {
                    if (parent_td.hasClass('wish_active')) {
                        $(this).closest('td').removeClass('wish_active').addClass('wish');
                    } else {
                        $(this).closest('td').removeClass('wish').addClass('wish_active');
                    }
                }
            },
            dataType: 'json'
        });
    });
    $('.vapiti_vote_action').click(function() {
        $.post('/jelol_vapiti', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            vapiti_id: $(this).closest('.vapiti_nominee_block').data('vapiti-id'),
            vapiti_type: $(this).closest('.vapiti_nominee_block').data('vapiti-type'),
            vapiti_yes: $(this).closest('.vapiti_nominee_block').find('.vapiti_button').length?'0':'1'
        }, function(data) {
            if (data.success) {
                document.location.reload();
            }
        }, 'json');
    });
    $('.show_comment_edit_form').click(function() {
        $(this).closest('.comment_block').find('.comment_content').hide();
        $(this).closest('.comment_block').find('.comment_edit_form').show();
        $(this).closest('.comment_block').find('.comment_edit_form').find('textarea').focus();
    });
    $('.hide_comment_edit_form').click(function() {
        $(this).closest('.comment_block').find('.comment_edit_form').hide();
        $(this).closest('.comment_block').find('.comment_content').show().focus();
    });
    $('.show_addon_edit_form').click(function() {
        $(this).closest('.film_addon').find('.film_addon_content').hide();
        $(this).closest('.film_addon').find('.addon_edit_form').show();
        $(this).closest('.film_addon').find('.addon_edit_form').find('textarea').focus();
    });
    $('.hide_addon_edit_form').click(function() {
        $(this).closest('.film_addon').find('.addon_edit_form').hide();
        $(this).closest('.film_addon').find('.film_addon_content').show().focus();
    });
    $('.confirm_required').click(function() {
        return confirm('Biztos vagy benne?');
    });
    $('form').submit(function() {
        $(this).find('input:submit').prop('disabled', true);
    });
    $('.toggle_delete').click(function() {
        $(this).closest('.delete_area').find('.delete_confirm').toggle();
    });
    $('table.sortable thead tr th input').click(function(event) {
        event.stopPropagation();
    });
    var sortable_table = $('table.sortable').stupidtable();
    sortable_table.on("aftertablesort", function (event, data) {
        var th = $(this).find("th");
        var th_arr = th.find('.arrow_holder');
        if (th_arr.length > 0) {
            th = th_arr;
        }
        th.find(".arrow").remove();
        var dir = $.fn.stupidtable.dir;
        var arrow = data.direction === dir.ASC ? "&uarr;" : "&darr;";
        th.eq(data.column).append('<span class="arrow">' + arrow +'</span>');
        $(this).find('tr:nth-child(odd)').removeClass('odd');
        $(this).find('tr:nth-child(even)').addClass('odd');
    });
    $('.insert_bbcode').click(function() {
        var target_textarea = $('.insert_bbcode_b').closest('.form_container').find('textarea');
        var selected_text = target_textarea.getSelection().text;
        if ($(this).hasClass('insert_bbcode_b')) {
            target_textarea.replaceSelectedText('[b]' + selected_text + '[/b]');
        }
        if ($(this).hasClass('insert_bbcode_i')) {
            target_textarea.replaceSelectedText('[i]' + selected_text + '[/i]');
        }
        if ($(this).hasClass('insert_bbcode_u')) {
            target_textarea.replaceSelectedText('[u]' + selected_text + '[/u]');
        }
        if ($(this).hasClass('insert_bbcode_del')) {
            target_textarea.replaceSelectedText('[del]' + selected_text + '[/del]');
        }
        if ($(this).hasClass('insert_bbcode_img')) {
            target_textarea.replaceSelectedText('[img]' + selected_text + '[/img]');
        }
        if ($(this).hasClass('insert_bbcode_link')) {
            target_textarea.replaceSelectedText('[link=]' + selected_text + '[/link]');
        }
        if ($(this).hasClass('insert_bbcode_spoiler')) {
            target_textarea.replaceSelectedText('[spoiler]' + selected_text + '[/spoiler]');
        }
    });
    $('.show_bbcode_help_button').click(function () {
        $('.bbcode_help').toggle();
    });
    $('.toggle_form_button').click(function() {
        $(this).closest('.form_outer_block').find('.form_block').toggle();
    });
    $('.toggle_link_edit_form_button').click(function() {
        $(this).closest('.link_edit_block').find('form').toggle();
    });
    $('#show_artist_edit_form_button').click(function () {
        $('#artist_edit_form').toggle();
    });
    $('#show_role_edit_form_button').click(function () {
        $('#role_edit_form').toggle();
    });
    $('#show_role_delete_form_button').click(function () {
        $('#role_delete_form').toggle();
    });
    $('#show_rating_details_button').click(function () {
        $('#show_rating_details_button').hide();
        $('#hide_rating_details_button').show();
        $('.rating_details').show();
    });
    $('#hide_rating_details_button').click(function () {
        $('#hide_rating_details_button').hide();
        $('#show_rating_details_button').show();
        $('.rating_details').hide();
    });
    $('#show_wish_details_button').click(function () {
        $('#show_wish_details_button').hide();
        $('#hide_wish_details_button').show();
        $('.wish_details').show();
    });
    $('#hide_wish_details_button').click(function () {
        $('#hide_wish_details_button').hide();
        $('#show_wish_details_button').show();
        $('.wish_details').hide();
    });
    $('#show_picture_edit_button').click(function () {
        $('.picture_edit_block').toggle();
    });
    $('#show_picture_delete_button').click(function () {
        $('.picture_delete_block').toggle();
    });
    $('#show_new_role_form').click(function () {
        $('#new_role_form').toggle();
        if ($('#new_role_form').is(':visible')) $('#new_role_artist').focus();
    });
    $('#show_table_of_roles_aux').click(function () {
        $('#table_of_roles_aux').toggle();
    });
    $('#show_plot_edit_form').click(function () {
        $('#plot_text').toggle();
        $('#plot_edit_form').toggle();
        $('#id_plot').focus();
    });
    $('#hide_plot_edit_form').click(function () {
        $('#plot_edit_form').toggle();
        $('#plot_text').toggle().focus();
    });
    $('#show_film_edit_form').click(function () {
        $('#film_edit_form').toggle();
        $('#id_film_orig_title').focus();
    });
    $('#hide_film_edit_form').click(function () {
        $('#film_edit_form').toggle();
    });
    $('#show_premier_form').click(function () {
        $('#premier_form').toggle();
        if ($('#premier_form').is(':visible')) $('#id_main_premier').focus();
    });
    $('#hide_premier_form').click(function () {
        $('#premier_form').toggle();
    });
    $('#show_keyword_form').click(function () {
        $('#keyword_form').toggle();
        if ($('#keyword_form').is(':visible')) $('#id_countries').focus();
    });
    $('#hide_keyword_form').click(function () {
        $('#keyword_form').toggle();
    });
    $('#show_sequel_form').click(function () {
        $('#sequel_form').toggle();
        if ($('#sequel_form').is(':visible')) $('#id_countries').focus();
    });
    $('#hide_sequel_form').click(function () {
        $('#sequel_form').toggle();
    });

    function split(val) {
        return val.split(/,\s*/);
    }
    function extractLast(term) {
        return split(term).pop();
    }
    $('#recipients')
        .bind('keydown', function(event) {
            if (event.keyCode === $.ui.keyCode.TAB &&
                $(this).autocomplete('instance').menu.active) {
                event.preventDefault();
            }
        })
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/users/', {
                    q: extractLast(request.term)
                }, response);
            },
            search: function() {
                var term = extractLast(this.value);
                if (term.length < 2) {
                    return false;
                }
            },
            focus: function() {
                return false;
            },
            select: function(event, ui) {
                var terms = split(this.value);
                terms.pop();
                terms.push(ui.item.value);
                terms.push('');
                this.value = terms.join(', ');
                return false;
            }
        });

    $('#new_role_artist')
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/artists/', {
                    q: request.term
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                    $('#new_role_gender').val(ui.item.gender);
                }
            }
        });

    $('#submit_new_role').click(function() {
        if ($('#new_role_gender').val() === 'U') {
            $('#new_role_gender').focus();
        } else {
            $.post('/uj_szereplo', {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                film_id: $('#new_role_film').val(),
                role_name: $('#new_role_name').val(),
                is_main_role: $('#new_is_main_role').val(),
                role_type: $('#new_role_type').val(),
                role_artist: $('#new_role_artist').val(),
                role_gender: $('#new_role_gender').val()
            }, function(data) {
                if (data.success) {
                    var role_name = $('#new_role_name').val();
                    if ($('#new_role_type').val() === 'V') role_name += ' (hangja)';
                    var artist_name = $('#new_role_artist').val();
                    if ($('#new_is_main_role').val() == 1) {
                        $('#table_of_roles').append('<tr><td>' + artist_name + '</td><td>' + role_name + '</td></tr>');
                    } else {
                        $('#table_of_roles_aux').show();
                        $('#table_of_roles_aux').append('<tr><td>' + artist_name + '</td><td>' + role_name + '</td></tr>');
                    }
                    $('#new_role_name').val('');
                    $('#new_role_artist').val('');
                    $('#new_role_gender').val('U');
                }
                $('#new_role_artist').focus();
            }, 'json');
        }
    });

    $('.edit_is_main_role').click(function() {
        $.post('/szerk_szereplo', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            role_id: $(this).data('role-id')
        }, function(data) {
            if (data.success) {
                document.location.reload();
            }
        }, 'json');
    });

    $('.checkbox_is_main_role').prop('checked', false);
    $('.multi_edit_is_main_role').click(function() {
        var role_ids = $.map($('.checkbox_is_main_role:checked'), function(elem) {
            return $(elem).data('role-id');
        });
        $.post('/szerk_szereplok', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            film_id: $(this).data('film-id'),
            role_ids: role_ids.join(',')
        }, function(data) {
            if (data.success) {
                document.location.reload();
            }
        }, 'json');
    });

    $('#confirm_main_roles').click(function() {
        $.post('/jovahagy_foszereplok', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            film_id: $(this).data('film-id')
        }, function(data) {
            if (data.success) {
                document.location.reload();
            }
        }, 'json');
    });

    $('.delete_award_button').click(function() {
        if (! confirm('Biztosan törölni akarod ezt a díjat?')) {
          return;
        }
        $.post('/torol_dij', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            award_id: $(this).data('id')
        }, function(data) {
            if (data.success) {
                document.location.reload();
            }
        }, 'json');
    });

    $('.input_for_artists')
        .bind('keydown', function(event) {
            if (event.keyCode === $.ui.keyCode.TAB &&
                $(this).autocomplete('instance').menu.active) {
                event.preventDefault();
            }
        })
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/artists/', {
                    q: extractLast(request.term)
                }, response);
            },
            search: function() {
                var term = extractLast(this.value);
                if (term.length < 2) {
                    return false;
                }
            },
            focus: function() {
                return false;
            },
            select: function(event, ui) {
                var terms = split(this.value);
                terms.pop();
                terms.push(ui.item.value);
                terms.push('');
                this.value = terms.join(', ');
                return false;
            }
        });

    var keyword_type = 'C';
    $('.input_for_keywords')
        .focus(function() {
            if ($(this).attr('id') === 'id_countries') keyword_type = 'C';
            else if ($(this).attr('id') === 'id_genres') keyword_type = 'G';
            else if ($(this).attr('id') === 'id_major_keywords') keyword_type = 'M';
            else if ($(this).attr('id') === 'id_keywords') keyword_type = 'MO';
            else keyword_type = 'O';
        })
        .bind('keydown', function(event) {
            if (event.keyCode === $.ui.keyCode.TAB &&
                $(this).autocomplete('instance').menu.active) {
                event.preventDefault();
            }
        })
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/keywords/', {
                    q: extractLast(request.term),
                    t: keyword_type
                }, response);
            },
            search: function() {
                var term = extractLast(this.value);
                if (term.length < 2) {
                    return false;
                }
            },
            focus: function() {
                return false;
            },
            select: function(event, ui) {
                var terms = split(this.value);
                terms.pop();
                terms.push(ui.item.value);
                terms.push('');
                this.value = terms.join(', ');
                return false;
            }
        });

    $('#id_film_imdb_link').blur(function() {
        var imdb_link = $(this).val().trim();
        if (imdb_link === '') {
            $('#similar_films_imdb').html('');
            return;
        }
        var valid_imdb_link = false;
        if (imdb_link.substr(0, 2) === 'tt') {
            if (imdb_link.length === 9 || imdb_link.length === 10) {
                valid_imdb_link = true;
            }
        } else {
            if (imdb_link.indexOf('imdb.com') !== -1 && imdb_link.indexOf('/tt') !== -1) {
                tt_part = imdb_link.substr(imdb_link.indexOf('/tt') + 1);
                if (tt_part.indexOf('/') !== -1) {
                    tt_part = tt_part.substr(0, tt_part.indexOf('/'));
                }
                if ((tt_part.length === 9 || tt_part.length === 10) && tt_part.indexOf('/') === -1) {
                    valid_imdb_link = true;
                }
            }
        }
        if (valid_imdb_link) {
            $.getJSON('/api/autocomplete/films-imdb/', {
                q: imdb_link
            }, function(data) {
                if (data.length) {
                    var similar_films = '';
                    for (var i=0; i < data.length; i++) {
                        var title = data[i].orig_title;
                        if (data[i].second_title) {
                            title = title + ' / ' + data[i].second_title;
                        }
                        if (data[i].year) title = title + ' (' + data[i].year + ')';
                        else title = title + ' (???)';
                        similar_films += '<li><a href="film/' + data[i].id + '/' + data[i].slug + '">' + title + '</a></li>';
                    }
                    $('#similar_films_imdb').html('<p>Már van film ugyanezzel az IMDB linkkel:</p><ul>' + similar_films + '</ul>');
                } else {
                    $('#similar_films_imdb').html('');
                }
            }, 'json');
        } else {
            $('#similar_films_imdb').html('<p><b>Ide biztos, hogy egy IMDB linket írtál be? Nem úgy néz ki.</b></p>');
        }
    });

    $('#id_film_orig_title').blur(function() {
        $.getJSON('/api/autocomplete/films/', {
            q: $(this).val()
        }, function(data) {
            if (data.length) {
                var similar_films = '';
                for (var i=0; i < data.length; i++) {
                    var title = data[i].orig_title;
                    if (data[i].second_title) {
                        title = title + ' / ' + data[i].second_title;
                    }
                    if (data[i].year) title = title + ' (' + data[i].year + ')';
                    else title = title + ' (???)';
                    similar_films += '<li><a href="film/' + data[i].id + '/' + data[i].slug + '">' + title + '</a></li>';
                }
                $('#similar_films').html('<p>Hasonló filmek</p><ul>' + similar_films + '</ul>');
            } else {
                $('#similar_films').html('');
            }
        }, 'json');
    });

    $('.input_for_sequel')
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/sequels/', {
                    q: request.term
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                }
            }
        });

    $('.input_for_user')
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/users/', {
                    q: request.term
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                }
            }
        });

    $('#id_toplist_type').change(function() {
        var toplist_type = $('#id_toplist_type').val();
        if (toplist_type == 'F') {
            $('.input_for_artist').hide();
            $('.input_for_film').show();
        } else {
            $('.input_for_film').hide();
            $('.input_for_artist').show();
        }
    });
    $('#id_ordered').change(function() {
        if ($('#id_ordered').val() == '1') {
            $('.toplist_serial_number').show();
        } else {
            $('.toplist_serial_number').hide();
        }
    });
    $('.input_for_film')
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/films/', {
                    q: request.term,
                    f: 'plain'
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                }
            }
        });
    $('.input_for_artist')
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/artists/', {
                    q: request.term
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                }
            }
        });
    $('.input_for_vapiti_film')
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/vapiti_films/', {
                    q: request.term
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                }
            }
        });
    $('.input_for_vapiti_artist')
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/vapiti_artists/', {
                    g: $('#id_vapiti_type').val(),
                    q: request.term
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                }
            }
        });

    var award_type = 'N';
    $('.input_for_award')
        .focus(function() {
            if ($(this).attr('id') === 'id_name') award_type = 'N';
            else if ($(this).attr('id') === 'id_year') award_type = 'Y';
            else award_type = 'C';
        })
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/awards/', {
                    q: request.term,
                    t: award_type
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                }
            }
        });

    var film_id = '';
    $('.input_for_artist_in_film')
        .focus(function() {
            film_id = $(this).closest('form').find('[name="film_id"]').val();
        })
        .autocomplete({
            source: function(request, response) {
                $.getJSON('/api/autocomplete/artists/', {
                    q: request.term,
                    f: film_id
                }, response);
            },
            minLength: 2,
            select: function(event, ui) {
                if (ui.item) {
                    this.value = ui.item.value;
                }
            }
        });

    $('.banner_closer').click(function() {
        $.post('/bezar_banner', {
            csrfmiddlewaretoken: $.cookie('csrftoken'),
            banner_id: $(this).attr('id').substring(7)
        });
        $(this).closest('.banner').slideUp();
    });

    $('#carousel-premiers').on('slide.bs.carousel', function (e) {
        $.cookie('kt-carousel-premiers-index', $(e.relatedTarget).data('slide-index'), {
            expires: 365,
            path: '/',
            domain: '.kritikustomeg.org'
        });
    });

    $('#carousel-vapiti').on('slide.bs.carousel', function (e) {
        $.cookie('kt-carousel-vapiti-index', $(e.relatedTarget).data('slide-index'), {
            expires: 365,
            path: '/',
            domain: '.kritikustomeg.org'
        });
    });

    $('ul.nav li.dropdown').hover(function() {
        $(this).find('.dropdown-menu').stop(true, true).show();
    }, function() {
        $(this).find('.dropdown-menu').stop(true, true).hide();
    });

    $('.focus_this').focus();

    $('.comment_block_content .spoiler').each(function() {
        $('.show_spoilers_section').css('visibility', 'visible');
    });

});
