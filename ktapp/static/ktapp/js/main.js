$(function() {
    $('#show_rating_details_button').click(function () {
        $('.rating_details').toggle();
    });
    $('#show_change_vote_button').click(function () {
        $('.change_vote').toggle();
    });
    $('#show_picture_edit_button').click(function () {
        $('.picture_edit_block').toggle();
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
                $.getJSON('api/autocomplete/users', {
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
                $.getJSON('api/autocomplete/artists', {
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

    $('.focus_this').focus();

});
