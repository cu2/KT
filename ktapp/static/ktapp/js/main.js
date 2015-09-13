$(function() {
    $('tr').on('click', 'td.wish span, td.wish_active span', function() {
        var parent_td = $(this).closest('td');
        if (parent_td.hasClass('wish')) {
            $(this).closest('td').removeClass('wish').addClass('wish_active');
        } else {
            $(this).closest('td').removeClass('wish_active').addClass('wish');
        }
        $.ajax({
            type: 'POST',
            url: 'kivan',
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
    $('.show_comment_edit_form').click(function() {
        $(this).closest('.comment_block').find('.comment_content').hide();
        $(this).closest('.comment_block').find('.comment_edit_form').show();
        $(this).closest('.comment_block').find('.comment_edit_form').find('textarea').focus();
    });
    $('.hide_comment_edit_form').click(function() {
        $(this).closest('.comment_block').find('.comment_edit_form').hide();
        $(this).closest('.comment_block').find('.comment_content').show().focus();
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
    $('#show_picture_edit_button').click(function () {
        $('.picture_edit_block').toggle();
    });
    $('#show_picture_delete_button').click(function () {
        $('.picture_delete_block').toggle();
    });
    $('#show_new_role_form').click(function () {
        $('#new_role_form').toggle();
        if ($('#new_role_form').is(':visible')) $('#new_role_name').focus();
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
                $.getJSON('api/autocomplete/users/', {
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
                $.getJSON('api/autocomplete/artists/', {
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
        if ($('#new_role_gender').val() == 'U') {
            $('#new_role_gender').focus();
        } else {
            $.post('uj_szereplo', {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                film_id: $('#new_role_film').val(),
                role_name: $('#new_role_name').val(),
                role_type: $('#new_role_type').val(),
                role_artist: $('#new_role_artist').val(),
                role_gender: $('#new_role_gender').val()
            }, function(data) {
                if (data.success) {
                    var role_name = $('#new_role_name').val();
                    if ($('#new_role_type').val() == 'V') role_name += ' (hangja)';
                    var artist_name = $('#new_role_artist').val();
                    $('#table_of_roles').append('<tr><td>' + role_name + '</td><td>' + artist_name + '</td></tr>');
                    $('#new_role_name').val('');
                    $('#new_role_artist').val('');
                    $('#new_role_gender').val('U');
                }
                $('#new_role_name').focus();
            }, 'json');
        }
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
                $.getJSON('api/autocomplete/artists/', {
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
            if ($(this).attr('id') == 'id_countries') keyword_type = 'C';
            else if ($(this).attr('id') == 'id_genres') keyword_type = 'G';
            else if ($(this).attr('id') == 'id_major_keywords') keyword_type = 'M';
            else if ($(this).attr('id') == 'id_keywords') keyword_type = 'MO';
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
                $.getJSON('api/autocomplete/keywords/', {
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

    $('#id_film_orig_title').blur(function() {
        $.getJSON('api/autocomplete/films/', {
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
                $.getJSON('api/autocomplete/sequels/', {
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
            if ($(this).attr('id') == 'id_name') award_type = 'N';
            else if ($(this).attr('id') == 'id_year') award_type = 'Y';
            else award_type = 'C';
        })
        .autocomplete({
            source: function(request, response) {
                $.getJSON('api/autocomplete/awards/', {
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
                $.getJSON('api/autocomplete/artists/', {
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

    $('.focus_this').focus();

});
