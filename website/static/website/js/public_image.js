$(document).ready(function(){
    $('.public-image').addClass('active');
});

function show_public_image(element) {
    var id = $(element).find("input").first().val();
    var new_url = window.location.href + id + "/";
    // alert(new_url);
    window.location.href = new_url;
}
