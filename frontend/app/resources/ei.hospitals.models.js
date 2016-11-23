/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.hospitals.models", ["ngResource"])

.factory("Hospital", ["$resource", function($resource) {
    return $resource('/api/hospitals/:id', {id: '@id'});
}])

.factory("Specialty", ["$resource", function($resource) {
    return $resource('/api/specialties/:id', {id: '@id'});
}])

.factory("Department", ["$resource", function($resource) {
    return $resource('/api/departments/:id', {id: '@id'}, {
        get_by_specialty_and_hospital: {
            method: 'get',
            url: '/api/departments/:specialty/:hospital',
            isArray: true,
            params: {
                specialty: '@specialty',
                hospital: '@hospital'
            }
        }
    });
}])

.factory("AcceptanceSettings", ["$resource", function($resource) {
    return $resource('/api/acceptance_settings/:department_id/:month_id', {
        month_id: '@month',
        department_id: '@department'
    });
}])

.factory("GlobalSettings", ["$resource", function($resource) {
    // The resource itself does nothing (nothing at the endpoint). But the resource methods are what matter.
    return $resource('/api/global_settings/:id', {id: '@id'}, {
        get_acceptance_criterion: {
            method: 'get',
            url: '/api/global_settings/acceptance_criterion/'
        },
        set_acceptance_criterion: {
            method: 'post',
            url: '/api/global_settings/acceptance_criterion/'
        },
        get_acceptance_start_date_interval: {
            method: 'get',
            url: '/api/global_settings/acceptance_start_date_interval/'
        },
        set_acceptance_start_date_interval: {
            method: 'post',
            url: '/api/global_settings/acceptance_start_date_interval/'
        },
        get_acceptance_end_date_interval: {
            method: 'get',
            url: '/api/global_settings/acceptance_end_date_interval/'
        },
        set_acceptance_end_date_interval: {
            method: 'post',
            url: '/api/global_settings/acceptance_end_date_interval/'
        }
    });
}])

.factory("MonthSettings", ["$resource", function($resource) {
    return $resource('/api/month_settings/:id', {id: '@id'}, {
        update: {
            method: 'put'
        }
    });
}])

.factory("DepartmentSettings", ["$resource", function($resource) {
    return $resource('/api/department_settings/:id', {id: '@id'}, {
        update: {
            method: 'put'
        }
    });
}])

.factory("DepartmentMonthSettings", ["$resource", function($resource) {
    return $resource('/api/department_month_settings/:id/', {
        id: '@id'
    }, {
        get_display_starting_month: {
            method: 'get',
            url: '/api/department_month_settings/starting_month/'
        },
        update: {
            method: 'put'
        }
    });
}]);