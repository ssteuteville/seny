'use strict';

angular.module('SENY.response', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/response/:id', {
            templateUrl: 'response/create.html',
            controller: 'ResponseCreateController'
        })
    }])
    .controller('ResponseCreateController', ['$scope', '$location', 'SenyData', '$routeParams',
        function($scope, $location, SenyData, $routeParams){
            $scope.model = {};
            SenyData.senyRequest('advertisements/' + $routeParams.id + "/", 'GET', {})
                .success(function(data){
                    $scope.model.advertisement = data.id;
                    $scope.model.destination = data.product.owner_id;
                    $scope.model.accepted = 0;
                    $scope.model.thread_title = "Response to: " + data.product.title;
                });

            $scope.send = function(){
                SenyData.senyRequest('messages/response/', 'POST', {}, $scope.model)
                    .success(function(data){
                        $location.path('inbox/');
                    })
            }

    }])