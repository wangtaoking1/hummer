$(document).ready(function(){
    $('.volume-space').addClass('active');
});


function show_volume(element) {
    var id = $(element).find("input").first().val();
    var new_url = window.location.href + id + "/";
    window.location.href = new_url;
}
