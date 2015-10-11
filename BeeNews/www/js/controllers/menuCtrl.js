angular.module('starter.controllers')

.controller('menuCtrl', function($scope, $ionicPopup, $ionicSideMenuDelegate, $http, $window, $ionicLoading, $state) {
	$scope.showConfirm = function() {
	   var confirmPopup = $ionicPopup.confirm({
	     title: 'Deconnexion',
	     template: 'Vous allez être déconnecté: Veuillez confirmer'
	   });
	   confirmPopup.then(function(res) {
	   	 $ionicLoading.show({
		    template: '<ion-spinner icon="spiral"></ion-spinner>'
		 });
	     if(res) {
	     	$scope.userData = JSON.parse(window.localStorage['refs'] || '{}');
	     	if ($scope.userData != {}) {
		       $http({
				  method: 'POST',
				  url: 'http://localhost:5000/logout',
				  headers: {
				    'Content-Type': 'application/json',
				    'X-BeenewsAPI-Token': $scope.userData.token
				  },
				  data: {
				    "username": $scope.userData.username
				  },
				}).then(function successCallback(response) {
					$ionicLoading.hide();
					if (response.data.success == 'yes') {
						$ionicLoading.show({ template: 'Log out successful', noBackdrop: true, duration: 1000 });
						$state.go('login');
				    } else {
				    	$ionicLoading.show({ template: 'Log out failed: ' + response.data.more, noBackdrop: true, duration: 1000 });
				    }
				  }, function errorCallback(response) {
				    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 1000 });
				  });
			} else {
				$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 1000 });
			}
	     } else {
	     	$ionicLoading.show({ template: 'Log out cancelled', noBackdrop: true, duration: 1000 });
	     }
	   });
 	};

 	$scope.fetchNews = function(author) {
 		$state.go('menu.news', {author: author});
 	};
	
})
