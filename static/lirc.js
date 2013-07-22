function generateUrl(device, cmd) {
	return "/cgi-bin/lirc/" + device + "?" + cmd;
}

$(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
	$.mobile.loading("hide");
	$("#ajaxError-message").text(
		thrownError +
		"\nURL was: " +
		ajaxSettings.url
	);
	$.mobile.changePage( "#ajaxError", { role: "dialog" } );
});

$(document).bind("pagebeforechange", function( event, data ) {

	if (typeof data.absUrl == 'string') {
		var url = $.mobile.path.parseUrl(data.absUrl);

		if (url.filename == 'device.html') {
			loadCommands(url.search);
		}
	}
});

function loadCommands(devices) {
	$.mobile.loading( "show", {
		text: "Lade Geräte und Befehle",
		textVisible: true,
		textonly: false
	});
	
	$.ajax({
		url: "/devices.json",
		dataType: "json",
		success: function(data) {

			if (typeof data[
			window.devices = data;
			var devList = $('<ul/>');

			$.each(window.devices, function(i, e) {
				var devPageId = 'dev-' + i;
				var devPage = $('<div/>').attr({
					'data-add-back-btn': true,
					'id': devPageId
				});

				$('<h1/>')
					.text(e.name)
					.wrap('<div/>')
					.parent()
					.attr('data-role', 'header')
					.appendTo(devPage);

				var cmdList = $('<ul/>');

				$.each(e.commands, function(j, c) {
					$('<a/>')
						.text(c.name)
						.attr('href', '#')
						.on('click', function() {
							$.mobile.loading( "show", {
								text: "Sende Befehl...",
								textVisible: true,
								textonly: false
							});
							var url = generateUrl(i, c.id);
							
							$.ajax({
								url: url,
								dataType: "json",
								success: function(data) {
									$.mobile.loading( "hide" );
								}
							});
							return false;
						})
						.wrap('<li/>')
						.parent()
						.appendTo(cmdList);
				});

				cmdList
					.wrap('<div/>')
					.parent()
					.attr('data-role', 'content')
					.appendTo(devPage);

				devPage.appendTo('body');
				devPage.page();
				cmdList.listview();

				var dev = $('<a/>');
				dev.attr("href", "#" + devPageId);
				dev.text(e.name);
				dev.wrap('<li/>').parent().appendTo(devList);
			});

			devList.appendTo('#selectDevice-content');
			devList.listview({
				filter: true
			});

			$.mobile.loading( "hide" );
		}
	});*/
});

$( document ).delegate("#selectDevice", "pagebeforecreate", function() {
	$.mobile.loading( "show", {
		text: "Lade Geräte und Befehle",
		textVisible: true,
		textonly: false
	});
	
	$.ajax({
		url: "/devices.json",
		dataType: "json",
		success: function(data) {
			window.devices = data;
			var devList = $('<ul/>');

			$.each(window.devices, function(i, e) {
				var dev = $('<a/>');
				dev.attr("href", "device.html?" + i);
				dev.text(e.name);
				dev.wrap('<li/>').parent().appendTo(devList);
			});

			devList.appendTo('#selectDevice-content');
			devList.listview({
				filter: true
			});

			$.mobile.loading( "hide" );
		}
	});
});
