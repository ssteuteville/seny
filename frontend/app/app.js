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
        //$routeProvider.otherwise({redirectTo: '/home'});
        //$locationProvider.hashPrefix('index.html#');
        localStorageServiceProvider.setPrefix('SENY');
    }
])

//.directive('infiniteScroll', function(){
//        return function(scope, elm, attr){
//            console.log("scrolled");
//            var raw = elm[0];
//            elm.bind('scroll', function(){
//                if(raw.scrollTop + raw.offsetHeight >= raw.scrollHeight){
//                    scope.$apply(attr.infiniteScroll);
//                }
//            })
//        }
//    });

//.directive('infiniteScroll', [function(){
//        return {
//            restrict: 'ACE',
//            link: function ($scope, element, attr, ctrl) {
//                var raw = element[0];
//                element.scroll(function(){
//                    console.log('scroll event');
//                    if(raw.scrollTop + raw.offsetHeight >= raw.scrollHeight){
//                        $scope.$apply(attr.infiniteScroll);
//                    }
//                })
//            }
//        }
//    }])


function swapActive(element)
{
    var old = $('.btn-success')
    old.removeClass('btn-success')
    old.addClass('btn-primary');
    element.className = element.className.replace(/\bbtn-primary\b/, 'btn-success');
}