/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.months.models", ["ngResource"])

.factory("InternshipMonth", ["$resource", function($resource) {
    return $resource('/api/internship_months/:month_id', {month_id: '@month'}, {
        cancel_rotation: {
            method: 'post',
            url: '/api/internship_months/:month_id/cancel_rotation/',
            params: {
                month_id: '@month'
            }
        },
        get_by_internship_and_id: {
            method: 'get',
            url: '/api/internship_months/:internship_id/:month_id'
        }
    });
}])

.factory("Internship", ["$resource", function($resource) {
    return $resource('/api/internships/:id', {id: '@id'}, {
        with_unreviewed_requests: {
            method: 'get',
            url: '/api/internships/with_unreviewed_requests/',
            isArray: true
        }
    });
}]);