'use strict';

angular.module('SENY.home', ['ngRoute', 'SenyData'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/home', {
    templateUrl: 'home/home.html',
    controller: 'HomeController'
  });
}])

.controller('HomeController', ['$scope', '$modal', 'SenyData', function($scope, $modal, SenyData) {
    $scope.tag_query = "";
    $scope.type = "all";

    $scope.openAdDetail = function (ad) {
        var modalInstance = $modal.open({
            templateUrl: 'advertisement/modal.html',
            controller: 'adModalController',
            size: 'lg',
            resolve: {
                ad: function(){
                    return ad;
                }
            }
        });
        modalInstance.result.then(function(){

        })
    };

    $scope.update = function(){
        var query = {};
        if($scope.tag_query != "")
        {
            query.tags = $scope.tag_query.split(' ').join();
        }
        if($scope.type == 'all')
        {
            SenyData.senyRequest('advertisements/', 'get', query).then(function (promise) {
                $scope.advertisements = promise.data;
            })
        }
        else
        {
            query.product__type = $scope.type;
            SenyData.senyRequest('advertisements/', 'get', query)
                .then(function (promise) {
                $scope.advertisements = promise.data;
            })
        }

    };

    $scope.update("all");

    $scope.setType = function(type)
    {
        $scope.type = type;
        $scope.update();
    };

    //$scope.$watch("tag_query", function(old_val, new_val){
    //    $scope.tag_query = new_val;
    //    $scope.update();
    //});

    $scope.hasImage = function(ad){
        if(ad.product.display_image)
            return true;
        return false;
    };

    $scope.convertDate = function(date){
        var d = new Date(date);

        return d.toDateString() + " " + d.toLocaleTimeString();
    };

}]);