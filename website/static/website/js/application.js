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

    $('#logs select').change(function() {
        var pod_name = $('#logs .pod-name').val();
        var tail = $('#logs .tail-number').val();
        var url = window.location.href.split("applications")[0] + "pods/" +
            pod_name + "/logs/";

        params = {'tail': tail};

        $.ajax({
            cache: true,
            type: "GET",
            url: url,
            data: params,
            async: false,
            success: function(data) {
                $('#logs .logs-show').val(data);
            },
            error: function(request) {
                $('#logs .logs-show').val("获取日志失败！");
            }
        });
    });

    $('#monitor .pod-name').change(function() {
        var pod_name = $('#monitor .pod-name').val();

        reload_iframe_to_new_pod($('#monitor .mem-show'), pod_name);
        reload_iframe_to_new_pod($('#monitor .cpu-show'), pod_name);
    });

    $('#monitor .refresh').click(function() {
        reload_iframe($('#monitor .mem-show'));
        reload_iframe($('#monitor .cpu-show'));
    })
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

function reload_iframe(element) {
    var src = element.attr('src');
    element.attr('src', src);
}

function reload_iframe_to_new_pod(element, pod_name) {
    var urls = element.attr('src').split('&');
    urls[3] = "var-pod=" + pod_name;
    url = urls.join('&');
    element.attr('src', url);
}
