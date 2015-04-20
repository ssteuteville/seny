angular.module('SENY.profile', ['ngRoute', 'SenyData'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/profile-new', {
            templateUrl: 'profile/profile-new.html',
            controller: 'newProfileController'
        })
            .when('/user/:username', {
                templateUrl: 'profile/profile.html',
                controller: 'profileController'
            });
    }])
    .controller('profileController', ['$scope', 'SenyData', '$rootScope', '$location', '$routeParams',
        function($scope, SenyData, $rootScope, $location, $routeParams){
            $scope.max_rating = 5.0;
            (function getProfile(){
                SenyData.senyRequest('user-profiles/', 'GET', {owner: $routeParams.username})
                    .success(function(data){
                        $scope.model = data[0];
                        var query = {'active': 1, start: new Date().toISOString(), 'product__owner': $scope.model.owner};
                        SenyData.senyRequest('advertisements/', 'get', query)
                            .success(function(data){
                                $scope.model.advertisements = data;
                            })
                    })
            }())

        }])

    .controller('newProfileController', ['$scope', 'SenyData', '$rootScope', '$location', function($scope, SenyData, $rootScope, $location)
    {
        $scope.zip = "";
        $scope.title = "";
        $scope.description = "";

        $scope.update = function()
        {
            $scope.lat = null;
            $scope.long = null;
            getGeoAndMakeRequest()
        }

        function getGeoAndMakeRequest()
        {
            if (navigator.geolocation)
                navigator.geolocation.getCurrentPosition(setGeo, noGeo);
        }

        function setGeo(position)
        {
            $scope.long = position.coords.longitude;
            $scope.lat = position.coords.latitude;
            data = {zip: $scope.zip, title: $scope.title, description: $scope.description, lat: $scope.lat, long: $scope.long};
            SenyData.senyRequest('user-profiles/' + $rootScope.user.id + "/", 'PUT', {}, data).then(function(promise){
                $location.path('/home')})
        }

        function noGeo()
        {
            data = {zip: $scope.zip, title: $scope.title, description: $scope.description, lat: 0.0, long: 0.0};
            SenyData.senyRequest('user-profiles/' + $rootScope.user.id + "/", 'PUT', {}, data).then(function(promise){
                $location.path('/home')})
        }
    }])