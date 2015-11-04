angular.module('starter.controllers')

.controller('newsCtrl', function($scope, $ionicLoading, $http, $window, $state, $stateParams, $filter, $ionicPopup) {
	var addZeroBefore = function(n) {
	  return (n < 10 ? '0' : '') + n;
	};
	$scope.convertTimestamp = function(news){
		converted = news
		len = news.length
		for (i = 0; i < len; i++) {
			var a = new Date(converted[i].time * 1000);
			var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
			var year = a.getFullYear();
			var month = months[a.getMonth()];
			var date = a.getDate();
			var hour = addZeroBefore(a.getHours());
			var min = addZeroBefore(a.getMinutes());
			var sec = addZeroBefore(a.getSeconds());
			var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
			converted[i].time = time;
			converted[i].snip = $filter('limitTo')(news[i].data.text, 50, 0) + '...';
		}
		return converted;
	};

	$scope.getNews = function(){
		$ionicLoading.show({
	      template: '<ion-spinner icon="spiral"></ion-spinner>'
	    });
		$scope.userData = JSON.parse($window.localStorage['refs'] || '{}');
     	if ($scope.userData != {}) {
		    $http({
			  method: 'GET',
			  url: 'http://178.62.61.89/get_beedoc',
			  headers: {
			    'Content-Type': 'application/json',
			    'X-BeenewsAPI-Token': $scope.userData.token
			  },
			  params: {
			  	'username' : $scope.userData.username,
			  	'category' : 'news',
			  	'alias': $stateParams.alias ||'all'
			  }
			}).then(function successCallback(response) {
				$ionicLoading.hide();
				if (response.data.success == 'yes') {
					$scope.news = $scope.convertTimestamp(response.data.more);
					$window.localStorage['news'] = JSON.stringify($scope.news);
			    } else {
			    	$ionicLoading.show({ template: 'Fetch news failed: ' + response.data.more, noBackdrop: true, duration: 2000 });
			    	$state.go('menu.news', {alias: 'all'});
			    }
			}, function errorCallback(response) {
				$ionicLoading.hide();
			    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 2000 });
			});
		} else {
			$ionicLoading.hide();
			$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 2000 });
		}
	};

	$scope.getNews();

    $scope.doRefresh = function() {
	    $scope.getNews();
	    $scope.$broadcast('scroll.refreshComplete');
	    $scope.$apply();
    };

	$scope.showArticle = function(id) {
		$state.go('menu.article', {id: id});
	}
});
