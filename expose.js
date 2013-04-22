module.exports = function(grunt) {
  'use strict';

  var _ = grunt.util._;

  grunt.registerTask(
    'expose', "Expose available tasks as JSON object.", function () {
      grunt.log.write("EXPOSE_BEGIN" + JSON.stringify(grunt.task._tasks) + "EXPOSE_END");
    }
  );

};