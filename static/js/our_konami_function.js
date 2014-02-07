$(window).load(function() {
	var easter_egg = new Konami(function() { 
		$(document).ready(function() {
    		$("#shakespeare-image").animate({left: "+=500"}, 9000);
    		$("#shakespeare-image").animate({left: "-=300"}, 9000);
		});
	})
});