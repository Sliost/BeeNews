angular.module('postApp', [])
  .controller('postController', function() {
    var defaultArticleData = {
      category : 'news',
      type : 'article',
      data: {
        title: 'Bip',
        author: 'Bop',
        text: 'Bap'
      }
    };

    var defaultUserData = {
      email : '',
      password: ''
    };

    var userData = defaultUserData;
    var articleData = defaultArticleData;

    post = function() {
        $http({
		    method: 'POST',
		    url: 'http://localhost:5000/web/post',
		    headers: {
                'Content-Type': 'application/json'
            },
		    data: {
		        userData: userData,
		        articleData: articleData
		    }
        }).then(function successCallback(response) {
		    if (response.data.success == 'yes') {
		        alert('Post Successful');
		        articleData = defaultArticleData;
		        userData = defaultUserData;
		    } else {
		        alert(response.data.more);
		    }
			$scope.onews = $scope.createSnip(response.data.onews);
        }, function errorCallback(response) {
		    alert('An error occured. Retry later');
		});
    };
  });