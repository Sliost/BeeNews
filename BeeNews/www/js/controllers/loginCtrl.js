angular.module('starter.controllers', [])

.controller('loginCtrl', function($scope, $state, $http, $ionicLoading, $window, $ionicModal, $sanitize) {
	$scope.defaultloginData = {
		email: "",
		password: "",
		remember: "no"
	};

	$scope.loginData = $scope.defaultloginData;

	var sanitizeCredentials = function(credentials) {
		return {
			email: $sanitize(credentials.email),
			password: $sanitize(credentials.password),
			remember: "no"
		};
	};

	$scope.loginWithToken = function() {
		$scope.userData = JSON.parse(window.localStorage['refs'] || '{}');
	 	if ($scope.userData != {}) {
	       $http({
			  method: 'POST',
			  url: 'http://178.62.61.89/login',
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
					var refs = {
						pseudo: response.data.pseudo,
						username: $scope.userData.username,
						token: response.data.token
					};

					$window.localStorage['refs'] = JSON.stringify(refs);
					$ionicLoading.show({ template: 'Connection successful', noBackdrop: true, duration: 1000 });

					$state.go('menu.about');
			    } else {
			    	$ionicLoading.show({ template: 'Login with token failed: ' + response.data.more, noBackdrop: true, duration: 2000 });
			    }
			  }, function errorCallback(response) {
			    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 2000 });
			  });
		} else {
			$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 2000 });
		}
	};

  $scope.login = function(loginData) {
    // Utiliser un hash pour le mot de passe
    if (loginData.remember == undefined)
    	loginData.remember = false
    $ionicLoading.show({
      template: '<ion-spinner icon="spiral"></ion-spinner>'
    });
    loginData = sanitizeCredentials(loginData);
    $http({
	  method: 'POST',
	  url: 'http://178.62.61.89/login',
	  headers: {
	    'Content-Type': 'application/json'
	  },
	  data: {
	    "username": loginData.email,
	    "password": loginData.password,
	    "remember": loginData.remember
	  },
	}).then(function successCallback(response) {
		$ionicLoading.hide();
		if (response.data.success == 'yes') {
			var refs = {
				pseudo: response.data.pseudo,
				username: loginData.email,
				token: response.data.token
			};

			$window.localStorage['refs'] = JSON.stringify(refs);
			$ionicLoading.show({ template: 'Connection successful', noBackdrop: true, duration: 1000 });

			$state.go('menu.about');
	    } else {
	    	$ionicLoading.show({ template: 'Connection failed: ' + response.data.more, noBackdrop: true, duration: 2000 });
	    }
	  }, function errorCallback(response) {
	    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 2000 });
	  });
  };

  $ionicModal.fromTemplateUrl('templates/lostpass.html', {
    scope: $scope
  }).then(function(modal) {
    $scope.modal = modal;
  });

  // Triggered in the login modal to close it
  $scope.closeLPass = function() {
    $scope.modal.hide();
  };

  // Open the login modal
  $scope.openLPass = function() {
    $scope.modal.show();
  };

  $scope.reinitpass = function(email) {
    $ionicLoading.show({
      template: '<ion-spinner icon="spiral"></ion-spinner>'
    });

    $scope.userData = JSON.parse(window.localStorage['refs'] || '{}');
 	if ($scope.userData != {}) {
       $http({
		  method: 'POST',
		  url: 'http://178.62.61.89/reinit_pass',
		  headers: {
		    'Content-Type': 'application/json',
		    'X-BeenewsAPI-Token': $scope.userData.token
		  },
		  data: {
		    "username": email
		  },
		}).then(function successCallback(response) {
			$ionicLoading.hide();
			if (response.data.success == 'yes') {
				$ionicLoading.show({ template: 'Password sent successfully', noBackdrop: true, duration: 1000 });
				$scope.closeLPass();
		    } else {
		    	$ionicLoading.show({ template: 'Password sending failed: ' + response.data.more, noBackdrop: true, duration: 2000 });
		    }
		  }, function errorCallback(response) {
		    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 2000 });
		  });
	} else {
		$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 2000 });
	}
  };
})