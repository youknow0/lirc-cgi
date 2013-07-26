$(document).bind('pageinit', function() {

	$('.sendcommand').on('click', function(e) {

		$.mobile.loading( 'show', {
			text: 'Befehl wird ausgeführt...',
			textVisible: true,
			theme: 'b'
		});

		$.ajax({

			url: $(this).attr('href'),
			complete: function() {
				$.mobile.loading('hide');
			},
			error: function() {
				alert("The command could not be executed!");
			}

		});

		return false;
		
	});
	
});
