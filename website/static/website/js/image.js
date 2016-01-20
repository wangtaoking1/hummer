$(document).ready(function(){
  	$('#image-space').addClass('nav-item-active');

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
});

function show_image(element) {
    var id = $(element).find("input").first().val();
    var new_url = window.location.href + id + "/";
    window.location.href = new_url;
}
