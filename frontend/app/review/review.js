'use strict';

angular.module('SENY.review', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/products/reviewable', {
            templateUrl: 'review/reviewable-products.html',
            controller: 'reviewableController'
        })
    }])
.controller('reviewableController', ['$scope', 'SenyData', function($scope, SenyData){
        $scope.products = {};
        function getReviewable(){
            SenyData.senyRequest('products/reviewable/', 'GET', {})
                .success(function(data, status){
                   $scope.products = data;
                });
        }
        getReviewable();

    }])