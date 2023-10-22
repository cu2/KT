$('#image').cropper({
    aspectRatio: 1,
    viewMode: 1,
    crop: function (e) {
        $('#picture_x').val(e.x);
        $('#picture_y').val(e.y);
        $('#picture_w').val(e.width);
        $('#picture_h').val(e.height);
    },
    preview: '#crop_preview'
});
