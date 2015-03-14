price_metrics = {0: 'hour', 2: 'day', 4: 'week', 8: 'month'};

angular.module('SENY.advertisement', ['ngRoute', 'SenyData', 'ui.bootstrap'])
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/advertisement/create', {
            templateUrl: 'advertisement/create.html',
            controller: 'AdvertisementCreateController'
        })
            .when('/advertisement/:id', {
            templateUrl: 'advertisement/detail.html',
            controller: 'adDetailController'
        })
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
    }])

    .controller('AdvertisementCreateController', ['$scope', 'SenyData', function($scope, SenyData){
        $scope.model = {};
        $scope.model.active = 1;
        $scope.ad_type = "individual";
        $scope.frequency = "";
        $scope.frequencys = ['daily', 'weekly', 'monthly'];
        $scope.duration_metrics = [{id:'day', label:'days'}, {id:'week', label:"weeks"}, {id:'month', label:"months"}];
        $scope.weekdays = [{id:'mo',label: 'Monday'}, {id:'tu',label: 'Tuesday'}, {id:'we',label: 'Wednesday'},
            {id:'th',label: 'Thursday'},{id:'fr',label: 'Friday'},{id:'sa',label: 'Saturday'},{id:'su',label: 'Sunday'}];
        $scope.month_choices = [{id:1,label:"January"}, {id:2,label:"February"}, {id:3,label:"March"}, {id:4,label:"April"},
            {id:5,label:"May"}, {id:6,label:"June"}, {id:7,label:"July"}, {id:8,label:"August"}, {id:9,label:"September"},
            {id:10,label:"October"}, {id:11,label:"November"}, {id:12,label:"December"}];
        $scope.hour_choices = [{id:0,label:"Midnight"}, {id:1, label:"1AM"}, {id:2,label:"2AM"}, {id:3,label:"3AM"}, {id:4,label:"4AM"},
            {id:5,label:"5AM"}, {id:6,label:"6AM"}, {id:7,label:"7AM"}, {id:8,label:"8AM"}, {id:9,label:"9AM"},
            {id:10,label:"10AM"}, {id:11,label:"11AM"}, {id:12,label:"12PM"}, {id:13,label:"1PM"}, {id:14,label:"2PM"},
            {id:15,label:"3PM"}, {id:16,label:"4PM"}, {id:17,label:"5PM"}, {id:18,label:"6PM"}, {id:19,label:"7PM"},
            {id:20,label:"8PM"}, {id:21,label:"9PM"}, {id:22,label:"10PM"}, {id:23,label:"11PM"}];
        $scope.date_choices = [];
        for (var i = 1; i <= 31; i++) {
            $scope.date_choices.push({id:i, label:i});
        }
        $scope.dates = [];
        $scope.hours = [];
        $scope.dow = [];
        $scope.months = [];
        $scope.duration = 0;
        $scope.settings = {
            buttonClasses:'btn btn-default select',
            scrollableHeight: '250px',
            scrollable: true
        }
    }])
;
function getGroups(ad)
{
    if(ad.product.reviews.length >= 5)
    {
        return ad.product.reviews.slice(0, 4);
    }
    return ad.product.reviews.slice(0, ad.product.reviews.length)
}