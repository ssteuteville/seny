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
            .when('/review/create/:id', {
                templateUrl: 'review/create.html',
                controller: 'reviewCreateController'
            })
    }])
.controller('reviewableController', ['$scope', 'SenyData', '$location', function($scope, SenyData, $location){
        $scope.products = {};
        function getReviewable(){
            SenyData.senyRequest('products/reviewable/', 'GET', {})
                .success(function(data, status){
                   $scope.products = data;
                });
        }
        getReviewable();
        $scope.review = function(product){
            $location.path('/review/create/' + product.id);
        }

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
.controller('reviewCreateController', ['$scope', 'SenyData', '$routeParams', '$location',
        function($scope, SenyData, $routeParams, $location){
            $scope.product = {};
            $scope.model = {}
            SenyData.senyRequest('products/' + $routeParams.id + '/', 'GET', {})
                .success(function(data){
                    $scope.product = data;
                    $scope.model.product_id = $scope.product.id;
                });
            $scope.send = function(){
                SenyData.senyRequest('reviews/', 'POST', {}, $scope.model)
                    .success(function(){
                        $location.path('/products/reviewable')
                    })

            }
        }])