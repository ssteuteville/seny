'use strict';

angular.module('SENY.signup', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/signup', {
            templateUrl: 'signup/signup.html',
            controller: 'signupController'
        });
    }])


    .controller('signupController', function($window, $scope, $location, SenyData) {
        if(SenyData.authorize())
            $location.path('/home');
        $scope.username = "";
        $scope.password = "";
        $scope.signup = function()
        {
            SenyData.signup($scope.username, $scope.password).then(function(promise){
                $location.path('/profile-new');
            });
        }
    });
