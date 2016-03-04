$(document).ready(function(){
    $('.resource-module').addClass('active');

    $('.module-create .submit').click(function() {
        $('.module-create .submit').val("创建中...");
        var form = $(this).parents("form");
        var url = window.location.href.split("#")[0];
        var create_url = url.replace("resource-module", "create-module");
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
});
