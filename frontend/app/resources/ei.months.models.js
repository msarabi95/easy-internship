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