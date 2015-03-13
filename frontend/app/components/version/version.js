'use strict';

angular.module('SENY.version', [
  'SENY.version.interpolate-filter',
  'SENY.version.version-directive'
])

.value('version', '0.1');
