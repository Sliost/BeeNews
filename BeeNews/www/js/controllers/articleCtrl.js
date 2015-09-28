angular.module('starter.controllers')

.controller('articleCtrl', function($scope,$stateParams) {
	$scope.article = {};
	$scope.article.titre="Et toi tu pars où en stage ?";
	$scope.article.id=$stateParams.id
	$scope.heure = function() {
		var d = new Date();
		return d.getHours()+':'+d.getMinutes();
	};
});
