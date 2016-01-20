$(document).ready(function(){
    $('tbody btn').click(function(){
        $(this).parent().submit();
    });

  	$('.action a').click(function(){
		var createPart = $('.create-project');
	    if($(createPart).hasClass('notshow'))
			$(createPart).removeClass('notshow');
	  	else
			$(createPart).addClass('notshow');
  	});

  	$('.form-group btn').click(function(){
		$('.create-project form').submit();
  	});


});

function show_project(element) {
    var id = $(element).find("input").first().val();
    window.location.href = "/projects/" + id + "/images/";
}
