'use strict';

angular.module('SENY.product', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/products', {
            templateUrl: 'product/list.html',
            controller: 'ProductListController'
        });
    }])

    .controller('ProductListController', ['$scope', 'SenyData', '$rootScope', function($scope, SenyData, $rootScope){
        $scope.products = [];
        $scope.update = function () {
            SenyData.senyRequest('products/user/', 'get', {}).then(function(promise){
                $scope.products = promise.data;
            })
        }
        $scope.update()
    }])
