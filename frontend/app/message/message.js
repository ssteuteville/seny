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

.controller('inboxController', ['$scope', 'SenyData', '$location', '$rootScope', function($scope, SenyData, $location, $rootScope){
        $scope.threads = [];
        $scope.search_query = "";
        $scope.convertDate = function(date){
            var d = new Date(date);

            return d.toDateString() + " " + d.toLocaleTimeString();
        };

        $scope.update = function(){
            console.log('calling update');
            SenyData.senyRequest('threads/user/', 'GET', {search:$scope.search_query})
                .success(function(data){
                    $scope.threads = data;
                });
        };

        $scope.update();


        $scope.opened = function(index){
            var thread = $scope.threads[index];
            if(thread.messages[thread.messages.length - 1].source != $rootScope.user.owner)
            {
                SenyData.senyRequest('threads/' + thread.id + '/read/', 'GET', {})
                    .success(function(data){
                        $scope.threads[index].messages = data.messages;
                        $scope.threads[index].new_messages = 0;
                    });
            }
        };

        $scope.view_ad = function(id){
            $location.path('/advertisement/' + id);
        };

        $scope.accept_response = function(message) {
            if(confirm("Are you sure you want to accept this response?"))
            {
                SenyData.senyRequest('advertisement-responses/' + message.response.id + '/accept/', 'GET', {})
                    .success(function(data){
                        $scope.reply(message.thread);
                    })
            }
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
    .controller('inboxPollController', ['SenyData', '$interval', '$rootScope',
        function(SenyData, $interval, $rootScope){
            $rootScope.new_messages = false;
            function update_inbox (){
                SenyData.check_inbox();
            }

            (function wait(){
                if($rootScope.user)
                {
                    console.log('owner initialized');
                    SenyData.check_inbox().then($interval(update_inbox, 60000));
                }
                else
                {
                    console.log('owner not initialized');
                    setTimeout(wait, 100);
                }
            }());

    }])