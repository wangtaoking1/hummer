$(document).ready(function(){
    $('.public-image').addClass('active');

    $('.clone-public .submit').click(function() {
        $('.clone-public .submit').val("克隆中...");
        var form = $(this).parents("form");
        var url = window.location.href;
        var clone_url = url + 'clone/';
        var data = form.serialize();

        $.ajax({
            cache: true,
            type: "POST",
            url: clone_url,
            data: data,
            async: false,
            success: function(data) {
                if (data.hasOwnProperty("success")) {
                    form[0].reset();
                    $('.clone-public .submit').val(" 克　隆 ");
                    $('.clone-public .submit-notice').html("克隆成功！");
                }
                else {
                    $('.clone-public .submit').val(" 克　隆 ");
                    $('.clone-public .submit-notice').html("克隆失败！");
                }
            },
            error: function(request) {
                $('.clone-public .submit').val(" 克　隆 ");
                $('.clone-public .submit-notice').html("克隆失败！");
            }
        });
    });
});

function show_public_image(element) {
    var id = $(element).find("input").first().val();
    var new_url = window.location.href + id + "/";
    // alert(new_url);
    window.location.href = new_url;
}
