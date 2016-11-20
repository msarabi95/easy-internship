/**
 * Created by MSArabi on 11/4/16.
 */
angular.module("ei.utils", ["ngRoute", "ngResource"])


.config(["$httpProvider", "$routeProvider", "$resourceProvider",
    function ($httpProvider, $routeProvider, $resourceProvider) {

    // These settings enable Django to receive Angular requests properly.
    // Check:
    // http://django-angular.readthedocs.io/en/latest/integration.html#xmlhttprequest
    // http://django-angular.readthedocs.io/en/latest/csrf-protection.html#cross-site-request-forgery-protection
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    // Check for messages with each response
    $httpProvider.interceptors.push(function ($q, $rootScope) {
       return {
           'response': function (response) {
               if ( $rootScope.fetchingMessages != true ) {
                   $rootScope.fetchingMessages = true;
                   $rootScope.$broadcast("fetchMessages");
               }
               return response;
           },
           'responseError': function (rejection) {
               if ( $rootScope.fetchingMessages != true ) {
                   $rootScope.fetchingMessages = true;
                   $rootScope.$broadcast("fetchMessages");
               }
               return $q.reject(rejection);
           }
       };
    });

    $resourceProvider.defaults.stripTrailingSlashes = false;
}])

.run(function ($rootScope, $resource) {
    toastr.options.positionClass = "toast-top-center";
    $rootScope.$on("fetchMessages", getMessages);

    function getMessages(event, eventData) {
        var messages = $resource("messages").query(function (messages) {
            $rootScope.fetchingMessages = false;
            for (var i = 0; i < messages.length; i++) {
                toastr[messages[i].level_tag](messages[i].message);
            }
        });
    }

    $rootScope.fetchingMessages = true;
    getMessages("", {});
})

.controller("MenuCtrl", ["$scope", "$route", "$location", function ($scope, $route, $location) {
    //$scope.currentTab = $route.current.currentTab;

    $scope.isActive = function (viewLocation) {
        return viewLocation == "#" + $location.path();
    }
}])

.controller("NotificationCtrl", ["$scope", "$http", "$filter", "$timeout", "$location", function ($scope, $http, $filter, $timeout, $location) {
    // An angularized version of http://django-nyt.readthedocs.io/en/latest/javascript.html#example-ui-js
    $scope.nyt_update_timeout = 30000;
    $scope.nyt_update_timout_adjust = 1.2;  // factor to adjust between each timeout.
    $scope.notifications = [];

    function nyt_update() {
        $http.get(URL_NYT_GET_NEW+'0/').then(function (response) {

            $scope.total_count = response.data.total_count;
            $scope.notifications = response.data.objects;

        }, function (error) {
            toastr.error("An error occurred during fetching notifications.")
        });
    }

    function update_timeout() {
        $timeout(nyt_update, $scope.nyt_update_timeout);
        $timeout(update_timeout, $scope.nyt_update_timeout);
        $scope.nyt_update_timeout *= $scope.nyt_update_timout_adjust;
    }

    $scope.nyt_read_notification = function (notification) {
        $location.path(notification.url);
        $http.get(URL_NYT_MARK_READ + notification.pk + '/' + notification.pk + '/').then(function (response) {
            $scope.nyt_oldest_id = 0;
            $scope.nyt_latest_id = 0;
            nyt_update();
        })
    };

    $scope.nyt_mark_all_read = function () {
        var nyt_oldest_id = 0;
        var nyt_latest_id = 0;

        if ($scope.notifications.length > 0) {
            var sorted = $filter('orderBy')($scope.notifications, 'pk');
            nyt_oldest_id = sorted[0].pk;
            nyt_latest_id = sorted[sorted.length - 1].pk;
        }

        $http.get(URL_NYT_MARK_READ + nyt_latest_id + '/' + nyt_oldest_id + '/').then(function (response) {
            nyt_update();
        })
    };

    update_timeout();
    nyt_update();
}])

.factory("loadWithRelated", function ($q) {
    return function loadWithRelated(id, resourceFactory, relatedFields, wait) {
        /*
            id: the identifier by which to fetch the object; could be a single ID, or an array of ID's
            resourceFactory: the ngResource factory to be used
            relatedFields: an optional argument. Is an array of fields. Each field definition takes one of 2 formats:
                - {fieldName: resourceFactory} -> just load the field
                - [{fieldName: resourceFactory}, relatedFields] -> load the field with additional extra fields
            wait: a boolean specifying whether to wait for the loading all of the subFields before resolving the
                  returned promise. Defaults to `false`.
         */

        // Default `wait` to false if not specified or no related fields are specified
        if (typeof wait == 'undefined' || typeof relatedFields == 'undefined') {
            wait = false;
        }

        // *********************************
        // **1** Load the resource object(s)
        // *********************************

        var isArray = Array.isArray(id),
            hasRelatedFields = (typeof relatedFields !== 'undefined'),
            loaded;

        if (isArray) {
            // **********************************************************************************************
            // *a* Array is passed: load the resource objects and then load related objects (if any) for each
            // **********************************************************************************************
            loaded = new Array(id.length);
            var promises = [];
            angular.forEach(id, function (id, index) {
                loaded[index] = resourceFactory.get({id: id});

                var promise = loaded[index].$promise.then(function (object) {
                    if (hasRelatedFields) {
                        return loadRelatedFields(object); // loadRelatedFields returns a promise
                    }
                });

                // If wait is true, then replace the promise of `loaded` with the promise returned from `then` (which
                // essentially returns the promise from `loadRelatedFields`)
                if (wait) {
                    promises.push(promise);
                } else {
                    promises.push(loaded[index].$promise);
                }
            });

            // Add a promise to the array, which resolves when all of the objects are loaded
            loaded.$promise = $q.all(promises);

        } else {
            // *************************************************************************************************
            // *b* Single integer is passed: load the resource object and then load its related objects (if any)
            // *************************************************************************************************
            loaded = resourceFactory.get({id: id});

            var promise = loaded.$promise.then(function (object) {
                if (hasRelatedFields) {
                    return loadRelatedFields(object); // loadRelatedFields returns a promise
                }
            });

            // If wait is true, then replace the promise of `loaded` with the promise returned from `then` (which
            // essentially returns the promise from `loadRelatedFields`)
            if (wait) {
                loaded.$promise = promise;
            }
        }

        /*
         * ****************************************
         *  Helper function to load related objects
         * ****************************************
         */
        function loadRelatedFields(object) {
            var promises = [];
            angular.forEach(relatedFields, function (fieldDefinition) {
                var relatedRelatedFields;
                if (Array.isArray(fieldDefinition)) {
                    relatedRelatedFields = fieldDefinition[1];
                    fieldDefinition = fieldDefinition[0];
                }
                //
                //console.log(relatedRelatedFields);
                //console.log(fieldDefinition);

                var fieldName = Object.keys(fieldDefinition)[0],
                    fieldResource = fieldDefinition[fieldName];

                object[fieldName] = loadWithRelated(object[fieldName], fieldResource, relatedRelatedFields, wait);
                promises.push(object[fieldName].$promise);
            });
            return $q.all(promises);
        }

        return loaded;
    }
});