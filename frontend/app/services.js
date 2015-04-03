angular.module('SenyData', ['LocalStorageModule', 'ipCookie'])
    .service('SenyData', function ($http, $rootScope, localStorageService, ipCookie){
        $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
        var client_id = "";
        var client_secret = "";
        $rootScope.authorized = false;
        var baseURL = 'https://52.10.64.129/backend/';
        //var baseURL = 'http://127.0.0.1:8000/';
        var apiVersion = "alpha";
         var apiURL = baseURL + "api/" + apiVersion + "/";
        this.apiURL = apiURL;

        this.login = function (username, password){
            if(localStorageService.keys().indexOf('client_id') > -1
                && localStorageService.keys().indexOf('client_secret') > -1)
            {
                client_id = localStorageService.get('client_id');
                client_secret = localStorageService.get('client_secret');
                return getToken(username, password);
            }
            else
            {
                return $http.post(baseURL + "login/", "username=" + username + ";password=" + password + ";")
                    .success(function (data, status, headers, config) {
                        client_id = data['client_id']
                        client_secret = data['client_secret']
                        localStorageService.set('client_id', client_id)     // these will be in browser for 30 days
                        localStorageService.set('client_secret', client_secret)
                        return getToken(username, password);
                    })
                    .error(function (data, status, headers, config) {
                        return status;
                    })
            }
        };

        this.signup = function(username, email, password){
            return $http.post(baseURL + "sign_up/", encode({username: username, password: password, email: email}))
                .success(function (data, status, headers, config){
                    client_id = data['client_id'];
                    client_secret = data['client_secret'];
                    localStorageService.set('client_id', client_id);
                    localStorageService.set('client_secret', client_secret);
                    return getToken(username, password)
                })
        };

        this.senyRequest = function (endpoint, method, query_params, post_params) {
            if(method.toLowerCase()=="put" || method.toLowerCase() == "post")
                return $http({
                    method: method,
                    url: apiURL + endpoint,
                    data: encode(post_params),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            return $http({
                method: method,
                url: apiURL + endpoint + "?" + encode(query_params)
            });
        };

        this.authorize = function(){
            if($rootScope.authorized)
                return $rootScope.authorized;

            var access = ipCookie('SENY-access');
            var expiration = ipCookie('SENY-expiration');
            if(access && expiration )
            {
                var date = new Date();
                var exp = new Date(expiration);
                if(date < exp)
                {
                    $http.defaults.headers.common['Authorization'] = "Bearer " + access;
                    this.header = "Bearer " + access;
                    getUser();
                    $rootScope.authorized = true;
                }
            }
            return $rootScope.authorized;
        };

        this.logout = function () {
            localStorageService.clearAll();
            var tokens = ['access', 'expiration', 'refresh', 'scope'];
            for(i in tokens )
            {
                ipCookie.remove('SENY-' + tokens[i]);
            }
            $rootScope.user = null;
            $rootScope.authorized = null;
        };

        // HELPER FUNCTIONS \\

        function getToken(username, password)
        {
            var params = {username: username,
                password: password,
                client_id: client_id,
                client_secret: client_secret,
                grant_type: 'password'};

            return $http({
                url: baseURL + "o/token/",
                transformRequest: encode,
                data:params,
                method: 'POST'
            })
                .success(function (data, status, headers, config) {
                    ipCookie('SENY-access', data['access_token'], {expires: 1});    //these will be in browser for this session
                    ipCookie('SENY-refresh', data['refresh_token'], {expires: 1});
                    ipCookie('SENY-expiration', new Date(+(new Date()) + parseInt(data['expires_in'] * 1000)), {expires: 1});
                    ipCookie('SENY-scope', data['scope'], {expires: 1});
                    $http.defaults.headers.common['Authorization'] = "Bearer " + data['access_token'];
                    this.header = "Bearer " + data['access_token'];
                    $rootScope.authorized = true;
                    return getUser()

                })
                .error(function (data, status, headers, config){
                    return status;
                });
        }

        function getUser()
        {
            return $http({
                method: 'GET',
                url: apiURL + 'user-profiles/user/'
            })
                .success(function (data, status, headers, config) {
                    $rootScope.user = data[0];
                    return status;
                })
        }

        function encode(obj) {
            var str = [];
            for(var p in obj)
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
            return str.join("&");
        }

        this.get_metric = function(metric)
        {
            switch (metric){
                case 0:
                    return 'hour';
                    break;
                case 2:
                    return 'day';
                    break;
                case 4:
                    return 'week';
                    break;
                case 8:
                    return 'month';
                    break;
            }
        }

        this.get_deposit = function(deposit)
        {
            if(deposit)
                return '$' + deposit + ' deposit';
            return 'no deposit';
        };

        this.get_type = function(type){
                if(type==0)
                return 'supply';
            return 'demand'
        }
    });