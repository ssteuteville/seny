'use strict';

// Declare app level module which depends on views, and components
angular.module('SENY', [
  'ngRoute',
  'SENY.LoginView',
  'SENY.home',
  'SENY.signup',
  'SENY.advertisement',
  'SENY.image',
  'SENY.product',
  'SENY.profile',
  'SENY.version',
  'SenyData',
  'ui.bootstrap',
  'angularFileUpload',
  'angularjs-dropdown-multiselect'

])

.config(['$routeProvider', '$httpProvider', '$locationProvider', 'localStorageServiceProvider',
    function($routeProvider, $httpProvider, $locationProvider, localStorageServiceProvider){
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $routeProvider.when('/LoginView', {
            templateUrl: 'LoginView/LoginView.html'
        });
        //$routeProvider.otherwise({redirectTo: '/home'});
        //$locationProvider.hashPrefix('index.html#');
        localStorageServiceProvider.setPrefix('SENY');
    }
])


function swapActive(element)
{
    var old = $('.btn-success')
    old.removeClass('btn-success')
    old.addClass('btn-primary');
    element.className = element.className.replace(/\bbtn-primary\b/, 'btn-success');
}