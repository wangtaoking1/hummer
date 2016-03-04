$(document).ready(function(){
    $('.volume-space').addClass('active');

    $('.volume-create .submit').click(function() {
        $('.volume-create .submit').val("创建中...");
        var form = $(this).parents("form");
        var url = window.location.href.split("#")[0];
        var create_url = url.replace("volumes", "create-volume");
        var data = form.serialize();

        $.ajax({
            cache: true,
            type: "POST",
            url: create_url,
            data: data,
            async: false,
            success: function(data) {
                if (data.hasOwnProperty("success")) {
                    form[0].reset();
                    window.location.href = url;
                }
                else {
                    $('.volume-create .submit').val(" 创　建 ");
                    $('.volume-create .submit-notice').html("创建失败！");
                }
            },
            error: function(request) {
                $('.volume-create .submit').val(" 创　建 ");
                $('.volume-create .submit-notice').html("创建失败！");
            }
        });
    });

    $('.volume-upload .fileupload').fileupload({
        dataType: 'json',
        add: function(e, data) {
            $('.volume-upload .upload').click(function() {
                $('.volume-upload .progress').css('display', 'block');
                $('.volume-upload .submit-notice').html("");
                data.submit();
            });
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100 - 1);
            $('.volume-upload .progress .progress-bar').css(
                'width',
                progress + '%'
            );
            $('.volume-upload .progress .progress-bar').text(progress + '%');
        },
        done: function(e, data) {
            $('.volume-upload .progress .progress-bar').css('width', '100%');
            $('.volume-upload .progress .progress-bar').text("finished");
            $('.volume-upload .progress').css('display', 'none');
            // window.location.reload();
            $('.volume-upload .submit-notice').html("导入成功！");
        }
    });

    $('.volume-clear a').click(function(){
        var clear_url = window.location.href + "clear/";

        $.ajax({
            cache: true,
            type: "GET",
            url: clear_url,
            async: false,
            success: function(data) {
                if (data.hasOwnProperty("success")) {
                    $('.volume-clear .submit-notice').html("格式化完成！");
                }
                else {
                     $('.volume-clear .submit-notice').html("格式化失败！");
                }
            },
            error: function(request) {
                $('.volume-clear .submit-notice').html("格式化失败！");
            }
        });
    });
});


function show_volume(element) {
    var id = $(element).find("input").first().val();
    var new_url = window.location.href + id + "/";
    window.location.href = new_url;
}
