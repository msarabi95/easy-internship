/**
 * Created by MSArabi on 3/3/17.
 */
angular.module("ei.months.directives", ["ei.months.models", "ui.bootstrap"])

.directive("internshipMonthBox", [function () {
    return {
        restrict: 'E',
        scope: {
            month: "=internshipMonth",
            size: "=?size",
            showMonthLabel: "=?showMonthLabel",
            showActionButtons: "=?showActionButtons",
            boxStyle: "=?boxStyle"
        },
        templateUrl: "/static/app/directives/templates/months/internship-month-box.html?v=0003",
        link: function (scope, element, attrs) {

            // Assert `size` is either 'lg' or 'sm'; default to 'lg' if not specified
            if (scope.size == undefined) {
                scope.size = "lg";
            } else if (scope.size !== 'lg' && scope.size !== 'sm') {
                throw "`size` must be equal to either 'lg' or 'sm'."
            }

            // If not specified, default `showActionButtons` to `true` if size is large, and to `false` if size is small
            // Otherwise assert buttons are shown only in large size
            if (scope.showActionButtons == undefined) {
                scope.showActionButtons = (scope.size == 'lg');
            } else if (scope.size == 'sm' && scope.showActionButtons == true) {
                throw "Action buttons can't be shown in small size."
            }

            // If not specified, default `showMonthLabel` to true
            if (scope.showMonthLabel == undefined) {
                scope.showMonthLabel = true;
            }

            // If not specified, default `boxStyle` to true
            // TODO: If boxStyle is false, showMonthLabel and showActionButtons can't be true
            if (scope.boxStyle == undefined) {
                scope.boxStyle = true;
            }

            scope.getBoxClass = function () {
                if (scope.month.disabled) {
                    return "default";
                } else if (scope.month.empty) {
                    if (scope.month.has_rotation_request || scope.month.has_freeze_request) {
                        return "warning";
                    }
                    return "default";
                } else if (scope.month.frozen) {
                    return "info";
                } else if (scope.month.occupied) {
                    return "primary";
                }
            };

            scope.getBodyHeight = function () {
                return scope.size == 'lg' ? '130px' : '80px';
            };

            scope.getForwardTooltipMessage = function () {
                if (!scope.month.current_request.is_forwarded) {
                    return "";
                }

                // Use a try-catch statement to account for async loading of month data
                try {
                    var memoHandedByIntern = scope.month.current_request.requested_department.department.memo_handed_by_intern;
                    if (memoHandedByIntern === true) {
                        return "Awaiting response from requested department or hospital (to be provided by intern)"
                    } else if (memoHandedByIntern === false) {
                        return "Awaiting response from requested department or hospital (to be provided by the medical internship unit)"
                    }
                } catch (e) {
                    return "...";
                }
            }

        }
    }
}])

.directive("boxActionButtons", [function() {
    return {
        restrict: 'E',
        scope: {
            buttons: "=buttons",
            params: "=params",
            color: "=?color",  // A bootstrap class color
            size: "=?size",
            dropup: "=?dropup"
        },
        template:
            '<div class="btn-group" ng-class="{dropup: dropup == true}">' +
            '  <a type="button" class="btn btn-{{ color }} btn-flat {{ getSizeClass() }}" href="{{ renderUrl(buttons[0]) }}">{{ renderLabel(buttons[0]) }}</a>' +
            '  <button type="button" class="btn btn-{{ color }} btn-flat dropdown-toggle {{ getSizeClass() }}" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' +
            '    <span class="caret"></span>' +
            '    <span class="sr-only">Toggle Dropdown</span>' +
            '  </button>' +
            '  <ul class="dropdown-menu">' +
            '    <li ng-repeat="button in buttons" ng-if="!$first" ng-class="{divider: button == DIVIDER}" ng-style="button == DIVIDER && {\'margin-top\': \'5px\', \'margin-bottom\': \'5px\'}">' +
            '       <a ng-if="button !== DIVIDER" href="{{ renderUrl(button) }}">{{ renderLabel(button) }}</a>' +
            '    </li>' +
            '  </ul>' +
            '</div>'
        ,  // For conditional styling, see: https://stackoverflow.com/a/18910653/6797938
        link: function (scope, element, attrs) {

            scope.DIVIDER = "$DIV$";

            scope.OPENING_BRACKET = "%(";
            scope.CLOSING_BRACKET = ")%";

            scope.REQUIRED_PARAMS = ["month_id"];

            scope.availableButtons = {
                // -------------------------
                // ---- Generic buttons ----
                // -------------------------
                info: {
                    label: "Get more info",
                    url: "#/planner/%(month_id)%/"
                },
                history: {
                    label: "See previous requests for this month",
                    url: "#/planner/%(month_id)%/history/"
                },
                // ---------------------------------
                // ---- State-changing requests ----
                // ---------------------------------
                'req-rota': {
                    label: "Request a rotation",
                    url: "#/planner/%(month_id)%/request-rota/"
                },
                'req-rota-change': {
                    label: "Request a different rotation",  // Only difference is label
                    url: "#/planner/%(month_id)%/request-rota/"
                },
                'req-rota-cancel': {
                    label: "Cancel this rotation",
                    url: "#/planner/%(month_id)%/cancel-rota/"
                },
                'req-freeze': {
                    label: "Request a freeze",
                    url: "#/planner/%(month_id)%/request-freeze/"
                },
                'req-freeze-cancel': {
                    label: "Cancel this freeze",
                    url: "#/planner/%(month_id)%/cancel-freeze/"
                },
                // ------------------------------
                // ---- Request cancellation ----
                // ------------------------------
                'delete-rota-req': {
                    label: "Delete my pending rotation request",
                    url: "#/planner/%(month_id)%/request-rota/delete/"
                },
                'delete-rota-cancel-req': {
                    label: "Delete my cancellation request",
                    url: "#/planner/%(month_id)%/cancel-rota/delete/"
                },
                'delete-freeze-req': {
                    label: "Delete my pending freeze request",
                    url: "#/planner/%(month_id)%/request-freeze/delete/"
                },
                'delete-freeze-cancel-req': {
                    label: "Delete my freeze cancellation request",
                    url: "#/planner/%(month_id)%/cancel-freeze/delete/"
                },
                // ----------------
                // ---- Leaves ----
                // ----------------
                'req-leave': {
                    label: "Request a leave",
                    url: "#/planner/%(month_id)%/request-leave/"
                },
                'manage-leaves': {
                    label: "Manage leaves during this month",
                    url: "#/planner/%(month_id)%/"
                }
            };

            // The `buttons` array is an array of button ID's as specified by the `availableButtons` object
            // It specifies which buttons will be displayed and in what order.
            // The first button in the array will be the main button of the button group that will be rendered.

            // If color class is not defined, default it to `default`
            if (scope.color === undefined) {
                scope.color = "default";
            }

            // If size is not defined, default it to `sm`
            if (scope.size === undefined) {
                scope.size = "sm";
            } else if (scope.size !== 'sm' && scope.size !== 'lg') {
                throw "`size` must be equal to either 'lg' or 'sm'."
            }

            // If dropup flag is not defined, default it to false
            if (scope.dropup === undefined) {
                scope.dropup = false;
            }

            // Verifications
            // (1) Verify buttons is an array and that at least one button is specified
            if ( !Array.isArray(scope.buttons) ) {
                throw "`buttons` should be an array."
            }
            if (scope.buttons.length < 1) {
                throw "At least 1 button is required to create a button group."
            }
            // (2) Verify all specified button ID's are valid (either one of the `availableButtons` or a `DIVIDER`)
            for (var i = 0; i < scope.buttons; i++) {
                var buttonId = scope.buttons[i];
                if ( !(buttonId in scope.availableButtons) && buttonId !== scope.DIVIDER) {
                    throw "Invalid button ID: " + buttonId + ".";
                }
            }
            // (3) Verify that all `REQUIRED_PARAMS` are included in the passed params
            for (var j = 0; j < scope.REQUIRED_PARAMS; j++) {
                var param = scope.REQUIRED_PARAMS[j];
                if ( !(param in scope.params)) {
                    throw "Required param " + param + " has not been passed."
                }
            }

            scope.getSizeClass = function() {
                if (scope.size === 'sm') {
                    return 'btn-xs';
                } else {
                    return '';
                }
            };

            scope.renderUrl = function(buttonId) {
                // Replace param placeholders with actual values
                var url = scope.availableButtons[buttonId].url;
                for (var p in scope.params) {
                    url = url.replace(
                        scope.OPENING_BRACKET + p + scope.CLOSING_BRACKET,
                        scope.params[p]
                    )
                }
                return url;
            };

            scope.renderLabel = function(buttonId) {
                return scope.availableButtons[buttonId].label;
            };
        }
    }
}])

.directive("freezeRequestResponseCard", ["$timeout", "FreezeRequestResponse", function ($timeout, FreezeRequestResponse) {
    return {
        restrict: 'E',
        scope: {
            request: "=freezeRequest",
            moveToPastRequests: "&onResponse"
        },
        templateUrl: "/static/app/directives/templates/months/freeze-request-response-card.html?v=0001",
        link: function (scope, element, attrs) {

            scope.response = {};

            scope.flag = function (flagName) {
                scope.flags = {};  // reset all flags
                scope.flags[flagName] = true;

                $timeout(function () {try {scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
            };

            scope.respond = function (request, is_approved, comments) {
                var response = new FreezeRequestResponse({
                    request: request.id,
                    is_approved: is_approved,
                    comments: comments
                });

                response.$save(function () {
                     scope.moveToPastRequests({request: request});
                }, function (error) {
                    toastr.error(error);
                });

            };

        }
    }
}])

.directive("freezeCancelRequestResponseCard", ["$timeout", "FreezeCancelRequestResponse", function ($timeout, FreezeCancelRequestResponse) {
    return {
        restrict: 'E',
        scope: {
            request: "=freezeCancelRequest",
            moveToPastRequests: "&onResponse"
        },
        templateUrl: "/static/app/directives/templates/months/freeze-cancel-request-response-card.html",
        link: function (scope, element, attrs) {

            scope.response = {};

            scope.flag = function (flagName) {
                scope.flags = {};  // reset all flags
                scope.flags[flagName] = true;

                $timeout(function () {try {scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
            };

            scope.respond = function (request, is_approved, comments) {
                var response = new FreezeCancelRequestResponse({
                    request: request.id,
                    is_approved: is_approved,
                    comments: comments
                });

                response.$save(function () {
                     scope.moveToPastRequests({request: request});
                }, function (error) {
                    toastr.error(error);
                });
            };

        }
    }
}]);