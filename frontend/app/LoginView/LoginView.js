'use strict';

angular.module('SENY.LoginView', ['ngRoute', 'SenyData'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/LoginView', {
    templateUrl: 'LoginView/LoginView.html',
    controller: 'loginController'
  });
}])


.controller('loginController', ['$window', '$scope', '$location', 'SenyData', function($window, $scope, $location, SenyData) {
        $scope.username = "";
        $scope.password = "";
        $scope.login = function()
        {
            SenyData.login($scope.username, $scope.password)
                .success(function(){
                    $location.path('/home');
                });
        }
    }])
.controller('logoutController', ['$scope', 'SenyData', function ($scope, SenyData) {
        $scope.logout = function () {
            SenyData.logout();
        }
    }])
