/**
 * Created by MSArabi on 12/18/16.
 */
angular.module("ei.rotations.directives", ["ei.utils", "ui.bootstrap"])

.directive("rotationRequestCard", ["$timeout", function ($timeout) {
    return {
        restrict: 'E',
        scope: {
            request: "=rotationRequest",
            moveToPastRequests: "&onResponse",
            moveToForwardedRequests: "&onForward"
        },
        templateUrl: "/static/directive-templates/staff/rotations/rotation-request-card.html",
        link: function (scope, element, attrs) {
            scope.flag = function (flagName) {
                scope.flags = {};  // reset all flags
                scope.flags[flagName] = true;
    
                $timeout(function () {try {scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
            };
    
            scope.respond = function (request, response, comments) {
                request.$respond({is_approved: response, comments: comments}, function (data) {
                    scope.moveToPastRequests({request: request});
                }, function (error) {
                    toastr.error(error);
                });
            };
    
            scope.forward = function (request) {
                request.$forward({}, function (data) {
                    scope.moveToForwardedRequests({request: request});
                }, function (error) {
                    toastr.error(error);
                });
            };
        }
    }
}])

.directive("acceptanceList", ["$uibModal", function ($uibModal) {
    return {
        restrict: 'E',
        scope: {
            list: "=list",
            removeFromList: "&onResponse"
        },
        templateUrl: "/static/directive-templates/staff/rotations/acceptance-list.html?v=0002",
        link: function (scope, element, attrs) {
            var CommentModalCtrl = ["$scope", "$uibModalInstance", "request", "options", function ($scope, $uibModalInstance, request, options) {
                $scope.request = request;
                $scope.options = options;

                if (!!request.response) {
                    $scope.comment = request.response.comments;
                }

                $scope.cancel = function () {
                    $uibModalInstance.dismiss('cancel');
                };

                $scope.ok = function () {
                    var commentProvided = !!$scope.comment && $scope.comment.replace(/\s/g, "").length > 0;
                    var commentOptional = $scope.options.hasOwnProperty('mandatoryComment') && $scope.options.mandatoryComment == false;

                    if (commentProvided || commentOptional) {
                        $uibModalInstance.close($scope.comment);
                    } else {
                        toastr.warning("Please provide a comment.")
                    }

                }
            }];

            scope.openCommentModal = function (request, options) {
                return $uibModal.open({
                    animation: true,
                    templateUrl: 'comment-modal.html',
                    controller: CommentModalCtrl,
                    resolve: {
                        request: request,
                        options: options == undefined ? {} : options
                    }
                });
            };

            scope.comment = function (request) {

                var isInAutoList = scope.list.auto_accepted.indexOf(request) !== -1 || scope.list.auto_declined.indexOf(request) !== -1;
                var options = {mandatoryComment: !isInAutoList};

                scope.openCommentModal(request, options).result.then(function (comment) {
                    request.response = {comments: comment};
                });
            };

            scope.moveRequest = function (request, from, to) {
                var validListNames = ['auto_accepted', 'auto_declined', 'manual_accepted', 'manual_declined'];

                var validOverrideCombinations = [
                    ['auto_accepted', 'manual_declined'],
                    ['auto_declined', 'manual_accepted']
                ];
                var validRevertCombinations = [
                    ['manual_accepted', 'auto_declined'],
                    ['manual_declined', 'auto_accepted']
                ];

                function isValidCombination (combination, reference) {
                    if (!Array.isArray(combination) || !combination.length == 2) {
                        throw "Unexpected combination format."
                    }
                    for (var item in reference) {
                        item = reference[item];
                        if (combination[0] == item[0] && combination[1] == item[1]) {
                            return true;
                        }
                    }
                    return false;
                }

                // (1) Verify that each of `from` and `to` is valid
                if (validListNames.indexOf(from) == -1 || validListNames.indexOf(to) == -1) {
                    throw "Both `from` and `to` should be valid list names. (One of 'auto_accepted', 'auto_declined', 'manual_accepted', or 'manual_declined')"
                }
                // (2) Verify that the combination is valid
                var combination = [from, to];
                var isOverride = isValidCombination(combination, validOverrideCombinations);
                var isRevert = isValidCombination(combination, validRevertCombinations);

                if (!(isOverride || isRevert)) {
                    throw "The combination of `from` and `to` should be a valid combination.";
                }

                function moveActual(request, from, to) {
                    var index = scope.list[from].indexOf(request);
                    if (index !== -1) {
                        scope.list[from].splice(index, 1);
                        scope.list[to].push(request);
                    } else {
                        throw "Request not found in `from` list."
                    }
                }

                if (isOverride) {
                    var options = {
                        message: "Please provide the reason for this change.",
                        buttonText: "Move request",
                        mandatoryComment: true
                    };
                    scope.openCommentModal(request, options).result.then(function (comment) {
                        request.response = {comments: comment};
                        moveActual(request, from, to);
                    });
                } else {
                    request.response = {comments: undefined};
                    toastr.info("Comment has been cleared.");
                    moveActual(request, from, to);
                }
            };

            scope.respondAll = function () {
                scope.loading = true;
                scope.list.$respond({}, function () {
                    scope.loading = false;
                    scope.removeFromList({list: scope.list});
                }, function (error) {
                    scope.loading = false;
                    toastr.error(error.statusText);
                });
            };
        }
    }
}]);