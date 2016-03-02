$(document).ready(function(){
    $(".nav-sidebar li").hover(
        function() {
            active_element = $(".nav-sidebar .active");
            $(".nav-sidebar li").removeClass("active");
        },
        function() {
            active_element.addClass("active");
        }
    );
});

function show_dashboard() {
    window.location.href = "/dashboard/";
    $('.dashboard').addClass('active');
}

function show_introduction() {
    var pid = window.location.href.split("//")[1].split("/")[2];
    window.location.href = "/projects/" + pid + "/introduction/";
    $('.project-intro').addClass('active');
}

function show_images() {
    var pid = window.location.href.split("//")[1].split("/")[2];
    window.location.href = "/projects/" + pid + "/images/";
    $('.image-space').addClass('active');
}

function show_applications() {
    var pid = window.location.href.split("//")[1].split("/")[2];
    window.location.href = "/projects/" + pid + "/applications/";
    $('.application-space').addClass('active');
}

function show_volumes() {
    var pid = window.location.href.split("//")[1].split("/")[2];
    window.location.href = "/projects/" + pid + "/volumes/";
    $('.volume-space').addClass('active');
}

function show_publics() {
    var urls = window.location.href.split('/', 3);
    var new_url = urls.join('/') + "/publics/";
    window.location.href = new_url;
    $('.public-image').addClass('active');
}
