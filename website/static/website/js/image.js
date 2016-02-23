$(document).ready(function(){
  	$('.image-space').addClass('active');

    $('tbody btn').click(function(){
        $(this).parent().submit();
    });

    $('.image-create ul li').click(function() {
        $('.image-create ul li').removeClass('active');
        $(this).addClass('active');
        $('.image-create .tab-pane').removeClass('in');
        $('.image-create .tab-pane').removeClass('active');
        var id = $(this).children('a')[0].href.split('#')[1];
        $('#' + id).addClass('in');
        $('#' + id).addClass('active');
    });

    $('#fileupload').fileupload({
        dataType: 'json',

        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100);
            $('.progress .progress-bar').css(
                'width',
                progress + '%'
            );
            $('.progress .progress-bar').text(progress + '%');
        },

        done: function(e, data) {
            $('.progress .progress-bar').text("Finished");
            $('.progress').removeClass('active');
        }
    });

    $('.image-create .submit').click(function() {
        var form = $(this).parents("form");
        var url = window.location.href.split("#")[0].replace("images",
            "create-image");

        $.ajax({
            cache: true,
            type: "POST",
            url: url,
            data: form.serialize(),
            async: false,
            success: function(data) {
                if (data.hasOwnProperty("success")) {
                    form[0].reset();
                    // $(this).next().css({"display": "inline", "color": "green"});
                }
                else {
                    alert("error");
                }
            },
            error: function(request) {
                alert("error");
            }
        });
    });
});

function show_image(element) {
    var id = $(element).find("input").first().val();
    var base_url = window.location.href.split("#")[0];
    var new_url = base_url + id + "/";
    window.location.href = new_url;
}

