module.exports = function(grunt) {
  'use strict';

  var _ = grunt.util._;

  grunt.registerTask(
    'expose', "Expose available tasks as JSON object.", function () {
      var tasks = grunt.task._tasks;
      _.each( tasks, function( value, key, list ) {
        var targets = Object.keys(grunt.config.getRaw( key ) || {});
        if ( targets.length > 0 ) {
            list[ key ].targets = targets;
        }
      });
      grunt.log.write("EXPOSE_BEGIN" + JSON.stringify(tasks) + "EXPOSE_END");
    }
  );

};