/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.months.models", ["ngResource", "ei.interceptors"])

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
            url: '/api/internship_months/:internship_id/:month_id',
            transformResponse: [function (data, headersGetter) {
                var transformed = angular.fromJson(data);

                for (var i = 0; i < transformed.current_leave_requests; i++) {
                    // Convert start and end dates into moment
                    transformed.current_leave_requests[i].start_date = moment(transformed.start_date);
                    transformed.current_leave_requests[i].end_date = moment(transformed.end_date);
                    transformed.current_leave_requests[i].return_date = moment(transformed.return_date);

                    // Convert submission datetime into moment
                    transformed.current_leave_requests[i].submission_datetime = moment(transformed.submission_datetime);
                }

                return transformed;
            }]
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
        query: {
            method: 'get',
            isArray: true,
            transformResponse: [function (data, headersGetter) {
                var transformed = angular.fromJson(data);

                for (var i = 0; i < transformed.length; i++) {
                    var internship = transformed[i];

                    for (var j = 0; j < internship.months.length; j++) {
                        var month = internship.months[j];

                        for (var k = 0; k < month.current_leaves.length; k++) {
                            var currentLeave = month.current_leaves[k];

                            // Convert start and end dates into moment
                            currentLeave.start_date = moment(currentLeave.start_date);
                            currentLeave.end_date = moment(currentLeave.end_date);
                            currentLeave.return_date = moment(currentLeave.return_date);

                            // Convert submission datetime into moment
                            currentLeave.request.submission_datetime = moment(currentLeave.request.submission_datetime);
                            currentLeave.request.response.response_datetime = moment(currentLeave.request.response.response_datetime);


                            for (var x = 0; x < currentLeave.request.cancel_requests.length; x++) {
                                var cancelRequest = currentLeave.request.cancel_requests[x];
                                cancelRequest.submission_datetime = moment(cancelRequest.submission_datetime);
                            }
                        }

                        for (var l = 0; l < month.current_leave_requests.length; l++) {
                            var currentLeaveRequest = month.current_leave_requests[l];

                            // Convert start and end dates into moment
                            currentLeaveRequest.start_date = moment(currentLeaveRequest.start_date);
                            currentLeaveRequest.end_date = moment(currentLeaveRequest.end_date);
                            currentLeaveRequest.return_date = moment(currentLeaveRequest.return_date);

                            // Convert submission datetime into moment
                            currentLeaveRequest.submission_datetime = moment(currentLeaveRequest.submission_datetime);
                        }
                    }
                }

                return transformed;
            }]
        },
        get: {
            method: 'get',
            transformResponse: [function (data, headersGetter) {
                var transformed = angular.fromJson(data);

                var userLeaves = transformed.intern.profile.user.leaves;
                for (var i = 0; i < userLeaves.length; i++) {
                    userLeaves[i].start_date = moment(userLeaves[i].start_date);
                    userLeaves[i].end_date = moment(userLeaves[i].end_date);
                    userLeaves[i].request.submission_datetime = moment(userLeaves[i].request.submission_datetime);
                    userLeaves[i].request.response.response_datetime = moment(userLeaves[i].request.response_datetime);
                }
                
                var openLeaveRequests = transformed.intern.profile.user.open_leave_requests;
                for (var j = 0; j < openLeaveRequests.length; j++) {
                    openLeaveRequests[j].start_date = moment(openLeaveRequests[j].start_date);
                    openLeaveRequests[j].end_date = moment(openLeaveRequests[j].end_date);
                    openLeaveRequests[j].submission_datetime = moment(openLeaveRequests[j].submission_datetime);
                }
                
                var closedLeaveRequests = transformed.intern.profile.user.closed_leave_requests;
                for (var k = 0; k < closedLeaveRequests.length; k++) {
                    closedLeaveRequests[k].start_date = moment(closedLeaveRequests[k].start_date);
                    closedLeaveRequests[k].end_date = moment(closedLeaveRequests[k].end_date);
                    closedLeaveRequests[k].submission_datetime = moment(closedLeaveRequests[k].submission_datetime);
                    closedLeaveRequests[k].response.response_datetime = moment(closedLeaveRequests[k].response.response_datetime);
                }
                
                var openLeaveCancelRequests = transformed.intern.profile.user.open_leave_cancel_requests;
                for (var l = 0; l < openLeaveCancelRequests.length; l++) {
                    openLeaveCancelRequests[l].start_date = moment(openLeaveCancelRequests[l].start_date);
                    openLeaveCancelRequests[l].end_date = moment(openLeaveCancelRequests[l].end_date);
                    openLeaveCancelRequests[l].submission_datetime = moment(openLeaveCancelRequests[l].submission_datetime);
                }
                
                var closedLeaveCancelRequests = transformed.intern.profile.user.closed_leave_cancel_requests;
                for (var m = 0; m < closedLeaveCancelRequests.length; m++) {
                    closedLeaveCancelRequests[m].start_date = moment(closedLeaveCancelRequests[m].start_date);
                    closedLeaveCancelRequests[m].end_date = moment(closedLeaveCancelRequests[m].end_date);
                    closedLeaveCancelRequests[m].submission_datetime = moment(closedLeaveCancelRequests[m].submission_datetime);
                    closedLeaveCancelRequests[m].response.response_datetime = moment(closedLeaveCancelRequests[m].response.response_datetime);
                }

                return transformed;
            }]
        },
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

.factory("FreezeRequest", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/freeze_requests/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        open: {
            method: 'get',
            isArray: true,
            url: '/api/freeze_requests/open/',
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        }
    });
}])

.factory("FreezeRequestResponse", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/freeze_request_responses/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        }
    });
}])

.factory("FreezeCancelRequest", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/freeze_cancel_requests/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        open: {
            method: 'get',
            isArray: true,
            url: '/api/freeze_cancel_requests/open/',
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        }
    });
}])

.factory("FreezeCancelRequestResponse", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/freeze_cancel_request_responses/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        }
    });
}]);