angular.module('postApp', [])
  .controller('postController', function($scope, $http, $window) {
    var defaultArticleData = {
      category : 'news',
      type : 'article',
      data: {
        title: '',
        alias: '',
        text: ''
      }
    };

    var defaultUserData = {
      email : '',
      password: ''
    };

    $scope.userData = defaultUserData;
    $scope.articleData = defaultArticleData;

    $scope.post = function() {
        $http({
		    method: 'POST',
		    url: 'http://178.62.61.89/web/post',
		    headers: {
                'Content-Type': 'application/json'
            },
		    data: {
		        userData: $scope.userData,
		        articleData: $scope.articleData
		    }
        }).then(function successCallback(response) {
		    if (response.data.success == 'yes') {
		        $scope.articleData = defaultArticleData;
		        $scope.userData = defaultUserData;
		        $scope.form.$setPristine();
		        $window.location.href = 'http://178.62.61.89/web/confirm';
		    } else {
		        alert(response.data.more);
		    }
        }, function errorCallback(response) {
		    alert('An error occured. Retry later');
		});
    };
  });