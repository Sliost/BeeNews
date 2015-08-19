angular.module('starter.controllers', [])

.controller('loginCtrl', function($scope, $state) {
  $scope.login = function(email, pass, remember) {
    alert(email, pass, remember);
    // Lancer un appel ajax vers le serveur et mettre un spinner
    $state.go('about');
  };
});