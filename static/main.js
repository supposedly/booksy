angular.module("booksy", [])
  .filter('trustUrl', function ($sce) {
    return function(url) {                 // necessary for testing on my own comp
      return $sce.trustAsResourceUrl(url);
    };
  })
  .controller("LinkCtrl", ["$scope", function($scope) {
		this.show = function(nameFromDir) {
    	$scope.active = nameFromDir;
    };
  }])
  .directive("linkToggle", function() {
    return {
      scope: {
        "onClick": '&',
        "link": '=name'
      },
      template: '<a href="#" ng-click="localFunction(); vm.clicked()" ng-transclude>{{vm.link}}</a>',
      controllerAs: 'vm',
      bindToController: true,
      transclude: true,
      controller: function() {
        this.clicked = function() {
          this.onClick({nameFromDir: this.link});
        };
      },
      link: function(scope, element, attrs, ctrl) {
        scope.selected = "active"
      }
    }
  });
