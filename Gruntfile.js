module.exports = function (grunt) {
    grunt.initConfig({
        uglify: {
            app: {
                files: [{
                    src: 'skyfolk/static/js/**/*.js',
                    dest: 'skyfolk/static/js/min/',
                    expand: true,    // allow dynamic building
                    ext: '.min.js'   // replace .js to .min.js
                }]
            }
        },
        sass: {
            dist: {
                options: {
                    sourceMap: true,
                    outputStyle: 'compressed'
                },
                files: [{
                    expand: true,
                    cwd: 'skyfolk/static/sass',
                    src: ['*.sass'],
                    dest: 'skyfolk/static/css',
                    ext: '.css'
                }]
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-sass');

    grunt.registerTask('default', ['sass', 'uglify']);
};
