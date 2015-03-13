'use strict';

angular.module('SENY.product', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/products', {
            templateUrl: 'product/list.html',
            controller: 'ProductListController'
        })
            .when('/product/create', {
                templateUrl: 'product/create.html',
                controller: 'ProductCreateController'
        })
            .when('/product/detail', {
                templateUrl: 'product/detail.html',
                controller: 'NewProductDetailController'
            })
            .when('/product/:id', {
                templateUrl: 'product/detail.html',
                controller: 'ProductDetailController'
            })
            .when('/product/edit/:id', {
                templateUrl: 'product/edit.html',
                controller: 'ProductEditController'
            })
    }])

    .controller('ProductListController', ['$scope', 'SenyData', '$rootScope', function($scope, SenyData, $rootScope, $){
        $scope.products = [];
        $scope.SenyData = SenyData;
        $scope.update = function () {
            SenyData.senyRequest('products/user/', 'get', {}).then(function(promise){
                $scope.products = promise.data;
            })
        }
        $scope.update()
    }])

    .controller('ProductCreateController', ['$scope', 'SenyData', '$upload', '$location', '$rootScope',
        function($scope, SenyData, $upload, $location, $rootScope){
        $scope.file = null;
        $scope.model = {
            title: "",
            price_metric: {name: "hour", val: 0},
            price: 0,
            description: "",
            type: {name: "supply", val: 0},
            display_image: null,
            deposit: 0
        };
        $scope.display_image_title = "";
        $scope.image_type = "upload";
        $scope.display_image = false;
        $scope.upload  = function()
        {
            if($scope.file != null) //todo figure out why $scope.file is null
            {
                $upload.upload({
                    method: 'PUT',
                    url: SenyData.apiURL + 'products/new/',
                    file: $scope.file,
                    fields: {
                        'title': $scope.model.title,
                        'price_metric': $scope.model.price_metric.val,
                        'price': $scope.model.price,
                        'description': $scope.model.description,
                        'type': $scope.model.type.val,
                        'display_image.title': $scope.display_image_title,
                        'deposit': $scope.model.deposit
                    },
                    headers: {'Authorization': SenyData.header},
                    fileFormDataName: 'display_image.image'

                })
                    .success(function(data, status, headers, config){
                        $scope.in_progress = false;
                        $rootScope.new_product = data;
                        $location.path('/product/detail/')
                    })

                    .progress(function(event){
                        $scope.in_progress = true;
                    })
            }
        }

        $scope.create = function(){
            if($scope.image_type=="none")
                delete $scope.model.display_image;
            SenyData.senyRequest('products/', 'POST', {}, $scope.model).success(function (data, status, headers, config) {
                $rootScope.new_product = data;
                $location.path('/product/detail/')
            })
        }

        $scope.metrics = [{name: "hour", val: 0}, {name: "day", val: 2}, {name: "week", val: 4}, {name: "month", val: 8}];
        $scope.types = [{name: "supply", val: 0}, {name: "demand", val: 2}];
    }])

    .controller('NewProductDetailController', ['$scope', '$rootScope', 'SenyData', function($scope, $rootScope, SenyData){
        $scope.model = $rootScope.new_product;
        $scope.SenyData = SenyData;
    }])

    .controller('ProductDetailController', ['$scope', 'SenyData', '$routeParams', '$rootScope',
        function($scope, SenyData, $routeParams, $rootScope){
        $scope.model = {};
        $scope.SenyData = SenyData;
        $scope.update = function(){
            SenyData.senyRequest('products/' + $routeParams.id + '/', 'GET', {owner: $rootScope.user.owner})
                .success(function(data, status, headers, config)
                {
                    $scope.model = data;
                    $scope.rate = data.rating;
                })
                .error(function (data, status, headers, config) {
                    $scope.error = true;
                })
        }
        $scope.update();

    }])

    .controller('ProductEditController', ['$scope', 'SenyData', '$routeParams', '$rootScope', '$location',
        function ($scope, SenyData, $routeParams, $rootScope, $location) {
            $scope.model = {};
            $scope.error = false;
            $scope.update = function(){
                SenyData.senyRequest('products/' + $routeParams.id + '/', 'GET', {})
                    .success(function (data, status, headers, config) {
                        if(data.owner == $rootScope.user.owner)
                            $scope.model = data;
                        else
                            $scope.error = true;
                    })
                    .error(function(data, status, headers, config){
                        $scope.error = true;
                    })
            }

            $scope.update();

            $scope.put = function(){
                var temp = $scope.model.display_image;
                if($scope.model.display_image != null)
                    $scope.model.display_image = $scope.model.display_image.id;
                else
                    delete $scope.model.display_image;
                SenyData.senyRequest('products/' + $routeParams.id + '/', 'put', {}, $scope.model)
                    .success(function(data, status, headers, config){
                        $location.path('/product/' + data.id)
                    })
                    .error(function(data, statu, headers, config){
                        $scope.model.display_image = temp;
                    })
            }

            $scope.metrics = [{name: "hour", val: 0}, {name: "day", val: 2}, {name: "week", val: 4}, {name: "month", val: 8}];
            $scope.types = [{name: "supply", val: 0}, {name: "demand", val: 2}];
    }])

    .controller('ProductDeleteController', ['$scope', 'SenyData', function($scope, SenyData){
        $scope.del = function(id){
            SenyData.senyRequest('products/' + id + '/', 'DELETE', {})
                .success(function(data, status, headers, config){
                    console.log('success');
                    $scope.$parent.update();
                })
                .error(function(data, status, headers, config){
                    console.log('ohhhhh')
                })
        }
    }])
