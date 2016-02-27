$(document).ready(function() {
    $('.application-space').addClass('active');

    $('.application-details ul li').click(function() {
        $('.image-create ul li').removeClass('active');
        $(this).addClass('active');
        $('.image-create .tab-pane').removeClass('in');
        $('.image-create .tab-pane').removeClass('active');
        var id = $(this).children('a')[0].getAttribute('data-id');
        $('#' + id).addClass('in');
        $('#' + id).addClass('active');
    });
});


function show_application(element) {
    var id = $(element).find("input").first().val();
    var new_url = window.location.href + id + "/";
    window.location.href = new_url;
}
