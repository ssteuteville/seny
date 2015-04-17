'use strict';

angular.module('SENY.response', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/response/:id', {
            templateUrl: 'response/create.html',
            controller: 'ResponseCreateController'
        })
            .when('/responses', {
                templateUrl: 'response/pending.html',
                controller: 'pendingResponseController'
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
.controller('pendingResponseController', ['$scope', 'SenyData', '$location', function($scope, SenyData, $location){
        $scope.responses = {};
        function getResponses(){
            SenyData.senyRequest('advertisement-responses/pending/', 'GET', {})
                .success(function(data){
                    $scope.responses = data;
                })
        }
        $scope.accept = function(response)
        {
            if(confirm("Are you sure you want to accept this request?"))
            {
                SenyData.senyRequest('advertisement-responses/' + response.id + '/accept/', 'GET', {})
                    .success(function(data){
                        getResponses();
                    })
            }
        };
        getResponses();

        $scope.convertDate = function(date){
            var d = new Date(date);

            return d.toDateString() + " " + d.toLocaleTimeString();
        };
    }])