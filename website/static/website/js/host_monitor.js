$(document).ready(function(){
    $('.host-monitor').addClass('active');

    $('#host-monitor .monitor-option .refresh').click(function() {
        refresh_iframe($('#host-monitor .monitor-show iframe'));
    });

    $('#host-monitor .monitor-option .host-name').change(function() {
        reload_iframe_to_other();
    });

    $('#host-monitor .monitor-option .monitor-type').change(function() {
        reload_iframe_to_other();
    });
});

function refresh_iframe(element) {
    var src = element.attr('src');
    element.attr('src', src);
}

function reload_iframe_to_other() {
    var host = $('#host-monitor .monitor-option .host-name').val();
    var type = $('#host-monitor .monitor-option .monitor-type').val();

    var panel_ids = {
        "all": {
            "memory": 15,
            "cpu": 11,
            "disk": 19
        },
        "node": {
            "memory": 7,
            "disk": 10,
            "cpu": 16
        }
    };
    if (host == "All Hosts") {
        var type_id = panel_ids['all'][type];
    }
    else {
        var type_id = panel_ids['node'][type];
    }

    var url = $('#host-monitor .monitor-show iframe').attr('src').split('?')[0];
    url += ('?panelId=' + type_id + '&fullscreen');
    if (host != "All Hosts") {
        url += ('&var-node=' + host);
    }

    $('#host-monitor .monitor-show iframe').attr('src', url);
}
