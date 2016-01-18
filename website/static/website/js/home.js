$(document).ready(function(){
  	$('#project').click(function(){
		$('.project-part').removeClass('notshow');
		$('.image-part').addClass('notshow');
		$('.nav-item').removeClass('nav-item-active');
		$(this).addClass('nav-item-active');
  	});

  	$('#image').click(function(){
		$('.project-part').addClass('notshow');
		$('.image-part').removeClass('notshow');
		$('.nav-item').removeClass('nav-item-active');
		$(this).addClass('nav-item-active');
  	});

  	$('tbody tr').click(function(){
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
  	})
});
