price_metrics = {0: 'hour', 2: 'day', 4: 'week', 8: 'month'};

angular.module('SENY.advertisement', ['ngRoute', 'SenyData', 'ui.bootstrap'])
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/advertisement/:id', {
            templateUrl: 'advertisement/detail.html',
            controller: 'adDetailController'
        });
    }])
    .controller('adModalController', ['$scope', '$modalInstance', 'ad', '$location', function($scope, $modalInstance, ad, $location){
            $scope.ad = ad;
            $scope.interval = 5000;
            $scope.max_rating = 5.0;
            $scope.isReadOnly = true;
            $scope.slides = $scope.ad.product.images;
            $scope.rate = $scope.ad.product.rating;
            $scope.groups = getGroups($scope.ad);
            $scope.close = function () {
                $modalInstance.close();
            };

            $scope.cancel = function(){
                $modalInstance.dismiss('cancel')
            };
        $scope.share_url = $location.absUrl().split('#')[0] + '#/advertisement/';
        $scope.profile_url = $location.absUrl().split('#')[0] + '#/profile/';
        $scope.getMetric = function(ad){ return price_metrics[parseInt(ad.product.price_metric)]};
    }])

    .controller('adDetailController', ['$scope', '$routeParams', 'SenyData', '$location', function($scope, $routeParams, SenyData, $location){
        $scope.ad = {};
        $scope.ad.id = $routeParams.id;
        $scope.interval = 5000;
        $scope.max_rating = 5.0;
        $scope.isReadOnly = true;
        $scope.profile_url = $location.absUrl().split('#')[0] + '#/profile/';
        $scope.ratingStates = [
            {stateOn: 'glyphicon-star', stateOff: 'glyphicon-star-empty'},
        ];
        SenyData.senyRequest('advertisements/' + $scope.ad.id + '/', 'GET', {})
            .success(function(data, status, headers, config)
            {
                $scope.ad = data;
                $scope.slides = $scope.ad.product.images;
                $scope.rate = $scope.ad.product.rating;
                $scope.groups = getGroups($scope.ad);

            });
        $scope.getMetric = function(ad){ return price_metrics[parseInt(ad.price_metric)]};
    }]);

function getGroups(ad)
{
    if(ad.product.reviews.length >= 5)
    {
        return ad.product.reviews.slice(0, 4);
    }
    return ad.product.reviews.slice(0, ad.product.reviews.length)
}