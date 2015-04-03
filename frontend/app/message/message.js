'use strict';

angular.module('SENY.message', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/inbox', {
            templateUrl: 'message/inbox.html',
            controller: 'inboxController'
        })
            .when('/message/new', {
                templateUrl: 'message/new.html',
                controller: 'newMessageController'
            })
            .when('/message/new/:id', {
                templateUrl: 'message/new.html',
                controller: 'newMessageWithDestController'
            })
            .when('/message/reply/:id', {
                templateUrl: 'message/reply.html',
                controller: 'messageReplyController'
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
            $location.path('/message/reply/' + id);
        };

        $scope.new_msg = function(){
            $location.path('/message/new');
        };
        $scope.convertDate = function(date){
            var d = new Date(date);

            return d.toDateString() + " " + d.toLocaleTimeString();
        };
    }])
    .controller('newMessageController', ['$scope', 'SenyData', '$location', function($scope, SenyData, $location){
            $scope.model = {};
            $scope.destination = "";
            $scope.send = function(){
                SenyData.senyRequest('user-profiles/', 'GET', {owner: $scope.destination})
                    .success(function(data){
                        $scope.model.destination = data[0].owner_id;
                        SenyData.senyRequest('messages/new/', 'POST', {}, $scope.model)
                            .success(function(){
                                $location.path('/inbox/');
                            })
                    })
            }
        }])
    .controller('newMessageWithDestController', ['$scope', 'SenyData', '$location', '$routeParams',
        function($scope, SenyData, $location, $routeParams){
            $scope.model = {destination: $routeParams.id};
            $scope.destination = $scope.model.destination;
            $scope.send = function(){
                SenyData.senyRequest('user-profiles/', 'GET', {owner: $scope.destination})
                    .success(function(data){
                        $scope.model.destination = data[0].owner_id;
                        SenyData.senyRequest('messages/new/', 'POST', {}, $scope.model)
                            .success(function(){
                                $location.path('/inbox/');
                            })
                    })
            }

    }])
    .controller('messageReplyController', ['$scope', 'SenyData', '$location', '$routeParams',
        function($scope, SenyData, $location, $routeParams){
            $scope.model = {thread: $routeParams.id}
            $scope.send = function () {
                SenyData.senyRequest('messages/', 'POST', {}, $scope.model)
                    .success(function(data){
                        $location.path('/inbox/');
                    })
            }
    }])