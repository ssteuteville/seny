'use strict';

angular.module('SENY.LoginView', ['ngRoute', 'SenyData'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/LoginView', {
    templateUrl: 'LoginView/LoginView.html',
    controller: 'loginController'
  });
}])


.controller('loginController', ['$window', '$scope', '$location', 'SenyData', 'StatusService',
        function($window, $scope, $location, SenyData, StatusService) {
            $scope.username = "";
            $scope.password = "";
            $scope.login = function()
            {
                SenyData.login($scope.username, $scope.password)
                    .success(function(){
                        $location.path('/home');
                    })
                    .error(function(){
                        StatusService.update('danger', 'Invalid Username or Password..')
                    })
            }
        }
    ])
.controller('logoutController', ['$scope', 'SenyData', function ($scope, SenyData) {
        $scope.logout = function () {
            SenyData.logout();
        }
    }])
