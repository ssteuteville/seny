'use strict';

angular.module('SENY.review', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/products/reviewable', {
            templateUrl: 'review/reviewable-products.html',
            controller: 'reviewableController'
        })
            .when('/reviews', {
                templateUrl: 'review/reviews.html',
                controller: 'reviewListController'
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
.controller('reviewListController', ['$scope', 'SenyData', function($scope, SenyData){
        $scope.reviews = {};
        function getReviews(){
            SenyData.senyRequest('reviews/user/', 'GET', {})
                .success(function(data){
                    $scope.reviews = data;
                })
        }
        getReviews();
    }])