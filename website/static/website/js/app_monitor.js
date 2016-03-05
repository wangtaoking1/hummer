$(document).ready(function(){
    $('.app-monitor').addClass('active');

    $('#user-option').change(function() {
        hide_monitor_show();
        if ($(this).val() == "0") {
            clear_project_option();
            clear_app_option();
            clear_container_option();
        }
        else {
            data = {
                'user': $(this).val()
            };
            alert(data);
        }
    });
});

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
