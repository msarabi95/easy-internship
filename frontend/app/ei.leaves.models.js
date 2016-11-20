/**
 * Created by MSArabi on 11/17/16.
 */
angular.module("ei.leaves.models", ["ngResource"])

.factory("LeaveType", ["$resource", function($resource) {
    return $resource('/api/leave_types/:id', {id: '@id'});
}])

.factory("LeaveSetting", ["$resource", function($resource) {
    return $resource('/api/leave_settings/:id', {id: '@id'});
}])

.factory("LeaveRequest", ["$resource", function($resource) {
    return $resource('/api/leave_requests/:id', {id: '@id'});
}])

.factory("LeaveRequestResponse", ["$resource", function($resource) {
    return $resource('/api/leave_request_responses/:id', {id: '@id'});
}])

.factory("Leave", ["$resource", function($resource) {
    return $resource('/api/leaves/:id', {id: '@id'});
}])

.factory("LeaveCancelRequest", ["$resource", function($resource) {
    return $resource('/api/leave_cancel_requests/:id', {id: '@id'});
}])

.factory("LeaveCancelRequestResponse", ["$resource", function($resource) {
    return $resource('/api/leave_cancel_request_responses/:id', {id: '@id'});
}]);