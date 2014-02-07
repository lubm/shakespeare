$(window).load(function() {
    $("#shakespeare-image").css('display', 'none');
    $("#cs-academy").css('display', 'none');
    var easter_egg = new Konami(function() { 
        $("#shakespeare-image").css('display', 'block');
        $("#shakespeare-image").animate({left: "+=500"}, 1000);
        $("#cs-academy").delay(1000).fadeIn(300);
        $("#shakespeare-image").animate({left: "+=300"}, 500);
        $("#cs-academy").delay(1500).fadeOut(300);
        $("#shakespeare-image").animate({left: "-=800"}, 1000);
        $("#shakespeare-image").delay(3000).fadeOut(300);
    })
});