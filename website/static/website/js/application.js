$(document).ready(function() {
    $('.application-space').addClass('active');

    $('#project').click(function(){
        $('.project-part').removeClass('notshow');
        $('.image-part').addClass('notshow');
        $('.nav-item').removeClass('nav-item-active');
        $(this).addClass('nav-item-active');
    });

    $('#image').click(function(){
        $('.project-part').addClass('notshow');
        $('.image-part').removeClass('notshow');
        $('.nav-item').removeClass('nav-item-active');
        $(this).addClass('nav-item-active');
    });

    $('.baseInfo a').click(function(){
        $('.baseInfo a').removeClass('btn-prim');
        $(this).addClass('btn-prim');
    });
});


function show_application(element) {
    var id = $(element).find("input").first().val();
    var new_url = window.location.href + id + "/";
    window.location.href = new_url;
}
