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
