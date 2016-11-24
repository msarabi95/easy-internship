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
        },
        request_freeze: {
            method: 'post',
            url: '/api/internship_months/:month_id/request_freeze/'
        },
        request_freeze_cancel: {
            method: 'post',
            url: '/api/internship_months/:month_id/request_freeze_cancel/'
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
}])

.factory("Freeze", ["$resource", function($resource) {
    return $resource('/api/freezes/:id', {id: '@id'});
}])

.factory("FreezeRequest", ["$resource", function($resource) {
    return $resource('/api/freeze_requests/:id', {id: '@id'});
}])

.factory("FreezeRequestResponse", ["$resource", function($resource) {
    return $resource('/api/freeze_request_responses/:id', {id: '@id'});
}])

.factory("FreezeCancelRequest", ["$resource", function($resource) {
    return $resource('/api/freeze_cancel_requests/:id', {id: '@id'});
}])

.factory("FreezeCancelRequestResponse", ["$resource", function($resource) {
    return $resource('/api/freeze_cancel_request_reponses/:id', {id: '@id'});
}]);