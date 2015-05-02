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
    $scope.page = 1;
    $scope.page_size = 10;
    $scope.advertisements = [];
    $scope.inProgress = false;
    $scope.more = true;
    $scope.openAdDetail = function (ad) {
        var modalInstance = $modal.open({
            templateUrl: 'advertisement/modal.html',
            controller: 'adModalController',
            backDropClass: 'seny-panel',
            size: 'lg',
            resolve: {
                ad: function(){
                    return ad;
                }
            }
        });
        modalInstance.result.then(function(result){
            if(result == 'delete')
                $scope.update();
        })
    };

    $scope.update = function(){
        var query = {'active': 1, start: new Date().toISOString(), page:$scope.page, page_size:$scope.page_size};
        if($scope.tag_query != "")
        {
            query.tags = $scope.tag_query.split(' ').join();
        }
        if($scope.type == 'all')
        {
            $scope.inProgress = true;
            SenyData.senyRequest('advertisements/', 'get', query)
                .success(function (data) {updateData(data);})
                .error(function(data){
                    $scope.inProgress = false;
                    $scope.more = false;
                })
        }
        else
        {
            query.product__type = $scope.type;
            $scope.inProgress = true;
            SenyData.senyRequest('advertisements/', 'get', query)
                .success(function (data) {updateData(data);})
                .error(function(data){
                    $scope.inProgress = false;
                    $scope.more = false;
                })
        }

    };

    $scope.filter = function(){
        reset();
        $scope.update();
    }

    $scope.setType = function(type)
    {
        $scope.type = type;
        reset();
        $scope.update();
    };

    function reset()
    {
        $scope.page = 1;
        $scope.advertisements = [];
    }

    $scope.hasImage = function(ad){
        if(ad.product.display_image)
            return true;
        return false;
    };

    $scope.convertDate = function(date){
        var d = new Date(date);

        return d.toDateString() + " " + d.toLocaleTimeString();
    };

    function updateData(data){
        $scope.advertisements.push.apply($scope.advertisements, data);
        $scope.page += 1;
        $scope.inProgress = false;
    }

}]);