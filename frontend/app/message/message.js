'use strict';

angular.module('SENY.message', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/inbox', {
            templateUrl: 'message/inbox.html',
            controller: 'inboxController'
        });
    }])

.controller('inboxController', ['$scope', 'SenyData', '$location', function($scope, SenyData, $location){
        $scope.threads = [];
        SenyData.senyRequest('threads/user/', 'GET', {})
            .success(function(data){
                $scope.threads = data;
            });

        $scope.opened = function(index){
            var thread = $scope.threads[index];
            SenyData.senyRequest('threads/' + thread.id + '/read/', 'GET', {})
                .success(function(data){
                    $scope.threads[index].messages = data.messages;
                    $scope.threads[index].new_messages = 0;
                })
        };

        $scope.view_ad = function(id){
            $location.path('/advertisement/' + id);
        };

        $scope.accept_response = function(id) {
            $location.path('/accept-response/' + id); //todo implement accept-response
        };

        $scope.reply = function(id){
            $location.path('/message-reply/' + id);
        }
        $scope.convertDate = function(date){
            var d = new Date(date);

            return d.toDateString() + " " + d.toLocaleTimeString();
        };
    }])