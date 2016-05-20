$(document).ready(function(){
    $('.user-permission').addClass('active');

    $('.add button').click(function() {
        var form = $('.all-div form');
        var data = form.serialize();
        var url = window.location.href.split("#")[0];
        var create_url = url.replace("permission", "add_memebers");

        $.ajax({
            cache: true,
            type: "POST",
            url: create_url,
            data: data,
            async: false,
            success: function(data) {
                form[0].reset();
                window.location.href = url;
            },
            error: function(request) {
                window.location.href = url;
            }
        });
    });

    $('.remove button').click(function() {
        var form = $('.selected-div form');
        var data = form.serialize();
        var url = window.location.href.split("#")[0];
        var create_url = url.replace("permission", "remove_memebers");

        $.ajax({
            cache: true,
            type: "POST",
            url: create_url,
            data: data,
            async: false,
            success: function(data) {
                form[0].reset();
                window.location.href = url;
            },
            error: function(request) {
                window.location.href = url;
            }
        });
    });
});


