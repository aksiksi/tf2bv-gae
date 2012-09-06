// Simple piece of JS that allows for font-size modification on a webpage.
// Requires jQuery

$(document).ready(function() {
	var fontSize = parseInt($('body').css('font-size')); // Get current font size

	// Restore default font
	$('.defaultFont').click(function() {
		$('body').css('font-size', 14);
	});
	
	// Increase font by 1 px
	$('.increaseFont').click(function() {
		var maxSize = 24;
		if (fontSize <= maxSize) {
			fontSize = fontSize + 1;
			$('body').css('font-size', fontSize + "px");
		}
		else {
			alert('Maximum font size (' + maxSize + ') reached.');
		}
	});

	// Decrease font by 1 px
	$('.decreaseFont').click(function() {
		var minSize = 10;
		if (fontSize >= minSize) {
			fontSize = fontSize - 1;
			$('body').css('font-size', fontSize + "px");
		}
		else {
			alert('Minimum font size (' + minSize + ') reached.');
		}
	});
});