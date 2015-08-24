angular.module('starter.controllers', [])

.controller('loginCtrl', function($scope, $state) {
  $scope.login = function(email, pass, remember) {
    // Lancer un appel ajax vers le serveur et mettre un spinner
    $state.go('accueil');
  };
})
.controller('accueilCtrl', function($scope, $ionicSideMenuDelegate) {
	$scope.openMenu = function() {
	    $ionicSideMenuDelegate.toggleLeft();
	};
	$scope.heure = function() {
		var d = new Date();
		return d.getHours()+':'+d.getMinutes();
	};
});
