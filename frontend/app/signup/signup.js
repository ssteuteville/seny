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
        $scope.current = 0;
        $scope.username = "";
        $scope.password = "";
        $scope.email = "";
        $scope.num_panels = 2;
        $scope.signup = function()
        {
            SenyData.signup($scope.username, $scope.email, $scope.password).then(function(promise){
                $location.path('/profile-new');
            });
        }

        $scope.forward = function(){
            var old = $('#demo-' + $scope.current);
            var _new = $('#demo-' + ($scope.current+1));//old.addClass('demo-right');
            _new.removeClass('demo-hidden');
            _new.css("left", '-700px');
            old.animate(
                {"left":"5000px"},
                "slow");
            _new.animate(
                {"left":"25%"},
                "slow"
            );
            $scope.current += 1;
        };

        $scope.backward = function(){
            var old = $('#demo-' + $scope.current);
            var _new = $('#demo-' + ($scope.current-1));
            _
            _new.css("right", '-700px');
            _new.animate(
                {"left":"25%"},
                "slow"
            );
            old.animate(
                {"left":"-3000px"},
                "slow");
            $scope.current -= 1;
        };

        $scope.skip = function(){
            var old = $('#demo-' + $scope.current);
            var _new = $('#demo-' + $scope.num_panels);
            _new.removeClass('demo-hidden');
            _new.css("left", '-700px');
            old.animate(
                {"left":"5000px"},
                "slow");
            _new.animate(
                {"left":"25%"},
                "slow"
            );
            $scope.current = $scope.num_panels;
        }

    });
