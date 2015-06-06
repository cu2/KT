$(function() {
    var topmenu_max_height = 190;
    $('#topmenu_toggler').click(function() {
        if (parseInt($('#topmenu').css('height')) < topmenu_max_height) {
            $('#topmenu').css({
                height: topmenu_max_height + 'px'
            });
        } else {
            $('#topmenu').css({
                height: '32px'
            });
        }
    });
    $('#topmenu').mouseleave(function() {
        if (parseInt($('#topmenu').css('height')) == topmenu_max_height) {
            $('#topmenu').css({
                height: '32px'
            });
        }
    })
    $('#show_rating_details_button').click(function () {
        $('.rating_details').toggle();
    });
    $('#show_change_vote_button').click(function () {
        $('.change_vote').toggle();
    });
});
