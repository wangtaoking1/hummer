$(document).ready(function() {
    $('.application-space').addClass('active');

    $('.application-details ul li').click(function() {
        $('.application-details ul li').removeClass('active');
        $(this).addClass('active');
        $('.application-details .tab-pane').removeClass('in');
        $('.application-details .tab-pane').removeClass('active');
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

function show_volume(element) {
    var vid = $(element).find("input").first().val();
    var new_url = window.location.href.split("application")[0] + "volumes/" +
        vid + "/";
    window.location.href = new_url;
}
