'use strict';

// Declare app level module which depends on views, and components
angular.module('SENY', [
  'ngRoute',
  'ngAnimate',
  'SENY.LoginView',
  'SENY.home',
  'SENY.signup',
  'SENY.advertisement',
  'SENY.image',
  'SENY.product',
  'SENY.profile',
  'SENY.response',
  'SENY.review',
  'SENY.message',
  'SENY.version',
  'SenyData',
  'ui.bootstrap',
  'angularFileUpload',
  'angularjs-dropdown-multiselect',
  'infinite-scroll'

])

.config(['$routeProvider', '$httpProvider', '$locationProvider', 'localStorageServiceProvider',
    function($routeProvider, $httpProvider, $locationProvider, localStorageServiceProvider){
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $routeProvider.when('/LoginView', {
            templateUrl: 'LoginView/LoginView.html'
        });
        localStorageServiceProvider.setPrefix('SENY');
    }
])

.controller('statusController', ['$scope', 'StatusService', function($scope, StatusService){
    $scope.statusService = StatusService
}])

.animation('.slide', [function() {
    return {
        // make note that other events (like addClass/removeClass)
        // have different function input parameters
        enter: function(element, doneFn) {
            jQuery(element).fadeIn(1000, doneFn);
        },

        leave: function(element, doneFn) {
            jQuery(element).fadeOut(500, doneFn);
        }
    }
}])

function swapActive(element)
{
    var old = $('.btn-success')
    old.removeClass('btn-success')
    old.addClass('btn-primary');
    element.className = element.className.replace(/\bbtn-primary\b/, 'btn-success');
}