
//#### Banner animation ####

// Parameters

// Images container. CSS Requirements: width: 2*bannerWidth; position: relative;
var imagesContainer = $('#header-wrapper');

var animationDuration = 1000; // in milliseconds

var durationBetweenSlides = 10000; // in milliseconds

var bannerImageClassName = "banner-img";

var root = "/static/img/";
var bannersURLs = [ root+"Forum_Horizon_Chine_2017_1.jpg"
                , root+"Forum_Horizon_Chine_2017_2.jpg"
                , root+"Forum_Horizon_Chine_2017_3.jpg"
                , root+"Forum_Horizon_Chine_2017_4.jpg"
                , root+"Forum_Horizon_Chine_2017_5.jpg"
                , root+"Forum_Horizon_Chine_2017_6.jpg"
                , root+"Forum_Horizon_Chine_2017_7.jpg"
                , root+"Forum_Horizon_Chine_2017_8.jpg"
                , root+"Forum_Horizon_Chine_2017_9.jpg"
                , root+"Forum_Horizon_Chine_2017_10.jpg"
                ,root+"Forum_Horizon_Chine_2017_0.jpg"
                ];


//Initialization
waitAndSlide();


// Public function

function waitAndSlide() {
	setTimeout(function() {
		slideImage();
	}, durationBetweenSlides);
}

function slideImage() {
	var newDiv = $('<div/>');
	var imgLoaded = $('<img/>');
	imgLoaded.load(function() {_startSlide(newDiv);});
	var newURL = _getRandomImageUrl();
	newDiv.css('background', "url('" + newURL + "') no-repeat center");
	newDiv.addClass(bannerImageClassName);
	_oldURL = newURL;
	imagesContainer.append(newDiv);
	imgLoaded[0].src = newURL;
}

// Private functions

var _oldImage = $('.'+bannerImageClassName);
var _oldURL = "";
var _imgWidth = _oldImage.width();

function _getRandomImageUrl() {
	var url, i=0;
	do {
		url = bannersURLs[Math.floor((Math.random()*bannersURLs.length))];
	} while (url == _oldURL && i++ < 10);
	return url;
}

function _startSlide(newimg) {
	imagesContainer.animate(
		{
			left : "-" + _imgWidth
		}
		, animationDuration
		, function() {
			_endSlide(newimg);
		}
	);
}
function _endSlide(newimg) {
	imagesContainer.css("left", "0px");
	_oldImage.remove();
	newimg.addClass(bannerImageClassName);
	_oldImage = newimg;
	waitAndSlide();
}

//#### End banner animation ####
