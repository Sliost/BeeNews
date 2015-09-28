angular.module('starter.controllers')

.controller('newsCtrl', function($scope,$state) {
	$scope.heure = function() {
		var d = new Date();
		return d.getHours()+':'+d.getMinutes();
	};
	$scope.row = {};
	$scope.row.id=1;
	$scope.afficheArticle = function(id) {
		$state.go('menu.article',{id:id});
	}
});
