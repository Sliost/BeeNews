angular.module('starter.controllers')

.controller('articleCtrl', function($scope, $window, $stateParams, $ionicModal, $http, $ionicLoading) {
	$scope.comments = [];
	$scope.comment_text = {comment: ''}

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
		}
		return converted;
	};

	$scope.check_like = function(){
		$scope.userData = JSON.parse($window.localStorage['refs'] || '{}');
     	if ($scope.userData != {}) {
		    $http({
			  method: 'POST',
			  url: 'http://178.62.61.89/like_state',
			  headers: {
			    'Content-Type': 'application/json',
			    'X-BeenewsAPI-Token': $scope.userData.token
			  },
			  data: {
			  	'beedoc' : $scope.article.id,
			  	'username': $scope.userData.username
			  }
			}).then(function successCallback(response) {
				if (response.data.success == 'yes') {
					if (response.data.like == 0 && response.data.dislike == 1) {
						$scope.like_disable = false;
						$scope.dislike_disable = true;
						$scope.like_text = 'J\'sais Plus';
						$scope.dislike_text = 'J\'aime Pas';
					} else if (response.data.like == 1 && response.data.dislike == 0){
						$scope.like_disable = true;
						$scope.dislike_disable = false;
						$scope.like_text = 'J\'aime';
						$scope.dislike_text = 'J\'aime Plus';
					} else {
						$scope.like_disable = false;
						$scope.dislike_disable = false;
						$scope.like_text = 'J\'aime';
						$scope.dislike_text = 'J\'aime Pas';
					}
			    } else {
			    	$ionicLoading.show({ template: 'Fetch like_state failed: ' + response.data.more, noBackdrop: true, duration: 2000 });
			    }
			}, function errorCallback(response) {
			    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 2000 });
			});
		} else {
			$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 2000 });
		}
	};

	$scope.news = JSON.parse(window.localStorage['news'] || '[]');
	$scope.article = {};
	$scope.offset = 10000;
	if ($scope.news != []) {
		$scope.article = $scope.news[$stateParams.id];
		$scope.check_like();
	} else {
		$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 2000 });
	}

	$scope.getComment = function(){
		if ($scope.article.comments > 0) {
			$scope.userData = JSON.parse($window.localStorage['refs'] || '{}');
	     	if ($scope.userData != {}) {
			    $http({
				  method: 'GET',
				  url: 'http://178.62.61.89/get_comment',
				  headers: {
				    'Content-Type': 'application/json',
				    'X-BeenewsAPI-Token': $scope.userData.token
				  },
				  params: {
				  	'beedoc' : $scope.article.id,
				  	'offset': $scope.offset
				  }
				}).then(function successCallback(response) {
					if (response.data.success == 'yes') {
						$scope.comments = $scope.convertTimestamp(response.data.more);
						$scope.offset = response.data.offset;
				    } else {
				    	$ionicLoading.show({ template: 'Fetch comments failed: ' + response.data.more, noBackdrop: true, duration: 2000 });
				    }
				}, function errorCallback(response) {
				    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 2000 });
				});
			} else {
				$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 2000 });
			}
		} else {
			$scope.comments = [];
		}
	};

	$scope.doRefresh = function() {
	    $scope.getComment();
	    $scope.$broadcast('scroll.refreshComplete');
	    $scope.$apply();
    };

	$scope.addComment = function(comment_text){
		$scope.userData = JSON.parse($window.localStorage['refs'] || '{}');
     	if ($scope.userData != {}) {
		    $http({
			  method: 'POST',
			  url: 'http://178.62.61.89/add',
			  headers: {
			    'Content-Type': 'application/json',
			    'X-BeenewsAPI-Token': $scope.userData.token
			  },
			  data: {
			    "username": $scope.userData.username,
			    "category": "news",
			    "type": "comment",
			    "data": {"beedoc": $scope.article.id, "author": $scope.userData.pseudo, "text": comment_text.comment}
			  }
			}).then(function successCallback(response) {
				if (response.data.success == 'yes') {
					$scope.comment = $scope.convertTimestamp(response.data.more);
					$scope.article.comments += 1;
					$scope.getComment();
					$scope.comment_text.comment = '';
			    } else {
			    	$ionicLoading.show({ template: 'Add comment failed: ' + response.data.more, noBackdrop: true, duration: 2000 });
			    }
			}, function errorCallback(response) {
			    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 2000 });
			});
		} else {
			$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 2000 });
		}
	};

	$scope.like_or_dislike = function(action){
		$scope.userData = JSON.parse($window.localStorage['refs'] || '{}');
     	if ($scope.userData != {}) {
		    $http({
			  method: 'POST',
			  url: 'http://178.62.61.89/likes',
			  headers: {
			    'Content-Type': 'application/json',
			    'X-BeenewsAPI-Token': $scope.userData.token
			  },
			  data: {
			  	"username": $scope.userData.username,
			    "beedoc": $scope.article.id,
			    "action": action
			  }
			}).then(function successCallback(response) {
				if (response.data.success == 'yes') {
					if (action == 'like') {
						if ($scope.dislike_disable) {
							$scope.article.dislikes -= 1;
						} else {
							$scope.article.likes += 1;
						}
						$scope.check_like();
					} else {
						if ($scope.like_disable) {
							$scope.article.likes -= 1;
						} else {
							$scope.article.dislikes += 1;
						}
						$scope.check_like();
					}
			    } else {
			    	$ionicLoading.show({ template: 'Add action failed: ' + response.data.more, noBackdrop: true, duration: 2000 });
			    }
			}, function errorCallback(response) {
			    $ionicLoading.show({ template: 'An error occured. Retry later', noBackdrop: true, duration: 2000 });
			});
		} else {
			$ionicLoading.show({ template: 'Impossible to load data', noBackdrop: true, duration: 2000 });
		}
	};

	$ionicModal.fromTemplateUrl('templates/comment.html', {
		scope: $scope
	}).then(function(modal) {
		$scope.modal = modal;
	});

	// Triggered in the login modal to close it
	$scope.closeComment = function() {
		$scope.modal.hide();
	};

	// Open the login modal
	$scope.openComment = function() {
		$scope.getComment();
		$scope.modal.show();
	};
});
