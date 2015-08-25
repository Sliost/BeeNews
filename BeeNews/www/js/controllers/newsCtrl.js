angular.module('starter.controllers')

.controller('newsCtrl', function($scope) {
	$scope.heure = function() {
		var d = new Date();
		return d.getHours()+':'+d.getMinutes();
	};
});
