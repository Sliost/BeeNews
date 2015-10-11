angular.module('starter.controllers')

.controller('newsCtrl', function($scope, $ionicLoading, $http, $window, $state, $stateParams, $filter) {
	$scope.convertTimestamp = function(news){
		converted = news
		len = news.length
		for (i = 0; i < len; i++) {
			var a = new Date(converted[i].time * 1000);
			var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
			var year = a.getFullYear();
			var month = months[a.getMonth()];
			var date = a.getDate();
			var hour = a.getHours();
			var min = a.getMinutes();
			var sec = a.getSeconds();
			var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
			converted[i].time = time;
			converted[i].snip = $filter('limitTo')(news[i].data.text, 50, 0) + '...';
		}
		return converted;
	};
	$scope.getNews = function(){
		$scope.userData = JSON.parse($window.localStorage['refs'] || '{}');
     	if ($scope.userData != {}) {
		    $http({
			  method: 'GET',
			  url: 'http://localhost:5000/get_beedoc',
			  headers: {
			    'Content-Type': 'application/json',
			    'X-BeenewsAPI-Token': $scope.userData.token
			  },
			  params: {
			  	'username' : $scope.userData.username,
			  	'category' : 'news',
			  	'author': $stateParams.author ||'all'
			  }
			}).then(function successCallback(response) {
				if (response.data.success == 'yes') {
					$scope.news = $scope.convertTimestamp(response.data.more);
					$window.localStorage['news'] = JSON.stringify($scope.news);
			    } else {
			    	$ionicLoading.show({ template: 'Fetch news failed: ' + response.data.more, noBackdrop: true, duration: 1000 });
			    	$state.go('menu.news', {author: 'all'});
			    }
			}, function errorCallback(response) {
			    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 1000 });
			});
		} else {
			$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 1000 });
		}
	};

	$ionicLoading.show({
      template: '<ion-spinner icon="spiral"></ion-spinner>'
    });

	$scope.getNews();

	$ionicLoading.hide();
  
    $scope.doRefresh = function() {
	    $scope.getNews();
	    $scope.$broadcast('scroll.refreshComplete');
	    $scope.$apply();
    };

	$scope.showArticle = function(id) {
		$state.go('menu.article', {id: id});
	}
});