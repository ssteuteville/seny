'use strict';

angular.module('SENY.image', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/images', {
            templateUrl: 'image/list.html',
            controller: 'imageListController'
        })
            .when('/image/create', {
                templateUrl: 'image/create.html',
                controller: 'imageCreateController'
            })
    }])

    .controller('imageListController', ['$scope', 'SenyData', '$rootScope', function($scope, SenyData, $rootScope){
        $scope.images = [];
        $scope.update = function () {
            SenyData.senyRequest('images/user/', 'get', {}).then(function(promise){
                $scope.images = promise.data;
            })
        }
        $scope.update()
    }])

    .controller('imageCreateController', ['$scope', 'SenyData', '$upload', function($scope, SenyData, $upload){
        $scope.file = null;
        $scope.title = "";
        $scope.upload  = function()
        {
            if($scope.file != null)
            {
                $upload.upload({
                    url: SenyData.apiURL + 'images/',
                    file: $scope.file,
                    fields: {'title': $scope.title},
                    headers: {'Authorization': SenyData.header},
                    fileFormDataName: 'image'

                }).success(function(data, status, headers, config){
                    console.log(data);
                })
            }
        }
    }])

    .controller('imageListController', ['$scope', 'SenyData', function($scope, SenyData){
        $scope.images = [];
        $scope.update = function () {
            SenyData.senyRequest('images/user/', 'get', {}).then(function(promise){
                $scope.images = promise.data;
            })
        }
        $scope.update()
    }])
