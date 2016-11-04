/**
 * Created by MSArabi on 11/4/16.
 */
angular.module("ei.utils", [])

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
}]);