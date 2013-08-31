var buttons = $('.apply-button');

buttons.next().slideToggle(0);
$('.slidedDown').next().slideToggle(0);

$(document).ready(function() {
	buttons.click(function(e) {
		$(this).next().slideToggle();
	});
	$('#sidebar-wrapper div.title').click(function() {
		$(this).next().slideToggle();
	});
});



//#### Counter ####

//var forumDate = new Date(2013, 3, 18, 10, 0);
//
//var now = new Date();
//var d = Math.floor((forumDate - now)/1000);
//var s = d % 60;
//d = (d - s) / 60;
//var m = d % 60;
//d = (d - m) / 60;
//var h = d % 24;
//d = (d - h) / 24;
//var j = d;
//if (s < 0) s = 0;
//if (m < 0) m = 0;
//if (h < 0) h = 0;
//if (j < 0) j = 0;
//
//var _jj = $('#jj'), _hh = $('#hh'), _mm = $('#mm'), _ss = $('#ss');
//dispDays(); dispHours(); dispMinutes(); dispSeconds();
//function decrDays() {
//	j--;
//	dispDays();
//}
//function decrHours() {
//	h--;
//	if (h == -1) {
//		h = 23;
//		decrDays();
//	}
//	dispHours();
//}
//function decrMinutes() {
//	m--;
//	if (m == -1) {
//		m = 59;
//		decrHours();
//	}
//	dispMinutes();
//}
//function decrSeconds() {
//	s--;
//	if (s == -1) {
//		s = 59;
//		decrMinutes();
//	}
//	dispSeconds();
//}
//function dispDays() {
//	_jj.html(j);
//}
//function dispHours() {
//	_hh.html(h >= 10 ? h : "0"+h);
//}
//function dispMinutes() {
//	_mm.html(m >= 10 ? m : "0"+m);
//}
//function dispSeconds() {
//	_ss.html(s >= 10 ? s : "0"+s);
//}
//
//
//function updateDateTime() {
//	if (j != 0 || h != 0 || m != 0 || s != 0) {
//		decrSeconds();
//		setTimeout(updateDateTime, 1000);
//	} else {
//		$('.date').html("&nbsp;");
//		$('.time').text($('.nowlabel').text());
//	}
//}
//updateDateTime();

//#### End counter ####