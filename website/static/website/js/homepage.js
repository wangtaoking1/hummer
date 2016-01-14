$(document).ready(function() {
    $('[data-toggle=offcanvas]').click(function() {
        $('.row-offcanvas').toggleClass('active');
    });

    $('.nav-login').click(function(){
        $('.center-box').addClass('notshow');
        $('.login-area').removeClass('notshow');
        return false;
    });

    $('.nav-register').click(function() {
        $('.center-box').addClass('notshow');
        $('.register-area').removeClass('notshow');
        return false;
    });

    $('.go-login').click(function(){
        $('.center-box').addClass('notshow');
        $('.login-area').removeClass('notshow');
        return false;
    });

    $('.go-register').click(function(){
        $('.center-box').addClass('notshow');
        $('.register-area').removeClass('notshow');
        return false;
    });

    $('.login-body button').click(function(){
        $('.login-body form').submit();
    });

    $('.box-body').click(function(){
        return false;
    });

    $('body').click(function(){
        $('.center-box').addClass('notshow');
    });
});

$(document).on('ready', function() {
    $("#input-6").fileinput({
        showUpload: false,
        maxFileCount: 10,
        mainClass: "input-group-lg"
    });
});
