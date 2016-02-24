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
        $('.image-create .submit').val("上传中...");
        var form = $(this).parents("form");
        var url = window.location.href.split("#")[0]
        var create_url = url.replace("images", "create-image");

        $.ajax({
            cache: true,
            type: "POST",
            url: create_url,
            data: form.serialize(),
            async: false,
            success: function(data) {
                if (data.hasOwnProperty("success")) {
                    form[0].reset();
                    window.location.href = url;
                }
                else {
                    $('.image-create .submit').val(" 上 传 ");
                    $('.image-create .submit-notice').html("上传失败！");
                }
            },
            error: function(request) {
                $('.image-create .submit').val(" 上 传 ");
                $('.image-create .submit-notice').html("上传失败！");
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

