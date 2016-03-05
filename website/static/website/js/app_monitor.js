$(document).ready(function(){
    $('.app-monitor').addClass('active');

    // reset all select to value 0 when refresh the page.
    reset_option();

    $('#user-option').change(function() {
        hide_monitor_show();
        clear_project_option();
        clear_app_option();
        clear_container_option();

        if ($(this).val() != "0") {
            var params = {
                'user': $(this).val()
            };
            var url = window.location.href.replace("app-monitor",
                "list-projects");

            $.ajax({
                cache: true,
                type: "GET",
                url: url,
                data: params,
                async: false,
                success: function(data) {
                    for (var i = 0; i < data.length; i++) {
                        var option = $("<option>").val(data[i]['id']).text(data[i]['name']);
                        $('#project-option').append(option);
                    }
                },
                error: function(request) {
                    alert("error");
                }
            });
        }
    });

    $('#project-option').change(function() {
        hide_monitor_show();
        clear_app_option();
        clear_container_option();

        if ($(this).val() != "0") {
            var params = {
                'project': $(this).val()
            };
            var url = window.location.href.replace("app-monitor",
                "list-apps");

            $.ajax({
                cache: true,
                type: "GET",
                url: url,
                data: params,
                async: false,
                success: function(data) {
                    for (var i = 0; i < data.length; i++) {
                        var option = $("<option>").val(data[i]['id']).text(data[i]['name']);
                        $('#app-option').append(option);
                    }
                },
                error: function(request) {
                    alert("error");
                }
            });
        }
    });

    $('#app-option').change(function() {
        hide_monitor_show();
        clear_container_option();

        if ($(this).val() != "0") {
            var params = {
                'app': $(this).val()
            };
            var url = window.location.href.replace("app-monitor",
                "list-pods");

            $.ajax({
                cache: true,
                type: "GET",
                url: url,
                data: params,
                async: false,
                success: function(data) {
                    for (var i = 0; i < data.length; i++) {
                        var option = $("<option>").val(data[i]).text(data[i]);
                        $('#container-option').append(option);
                    }
                },
                error: function(request) {
                    alert("error");
                }
            });
        }
    });

    $('#container-option').change(function() {
        hide_monitor_show();

        if ($(this).val() != "0") {
            var user = $('#user-option').find("option:selected").text();
            var pod = $('#container-option').val();
            var type_ids = {'mem': 1, 'cpu': 14};

            var mem_url = get_monitor_url(type_ids['mem'], user, pod);
            var cpu_url = get_monitor_url(type_ids['cpu'], user, pod);

            $('.monitor-show .mem-show').attr('src', mem_url);
            $('.monitor-show .cpu-show').attr('src', cpu_url);
            show_monitor_show();
        }
    });
});

function reset_option() {
    $('#user-option').val('0');
    $('#project-option').val('0');
    $('#app-option').val('0');
    $('#container-option').val('0');
}

function clear_project_option() {
    $('#project-option').empty();
    $('#project-option').append($('<option value="0">-------------</option>'));
}

function clear_app_option() {
    $('#app-option').empty();
    $('#app-option').append($('<option value="0">-------------</option>'));
}

function clear_container_option() {
    $('#container-option').empty();
    $('#container-option').append($('<option value="0">-------------</option>'));
}

function hide_monitor_show() {
    $('#app-monitor .monitor-show').css('display', 'none');
}

function show_monitor_show() {
    $('#app-monitor .monitor-show').css('display', 'block');
}

function get_container_name(pod) {
    var items = pod.split('-');
    items.pop();
    return items.join('-');
}

function get_monitor_url(type_id, namespace, pod) {
    var container = get_container_name(pod);
    var base_url = $('.monitor-show input').val();

    return (base_url + "&panelId=" + type_id + "&var-namespace=" + namespace +
        "&var-pod=" + pod + "&var-container=" + container);
}
