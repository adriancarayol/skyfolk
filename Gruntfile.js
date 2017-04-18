module.exports = function (grunt) {
    grunt.initConfig({
        uglify: {
            app: {
                files: [{
                    expand: true,    // allow dynamic building
                    ext: '.min.js',   // replace .js to .min.js
                    cwd : 'skyfolk/static/js',
                    src: '**/*.js',
                    dest: 'skyfolk/static/dist/js/',
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
        },
        imagemin: {                         
            dynamic: {                         
              files: [{
                expand: true,
                cwd: 'skyfolk/static/img/',   
                src: ['**/*.{png,jpg,gif}'],
                dest: 'skyfolk/static/dist/img'
            }]
        },
        users: {
            files: [{
                expand: true,
                cwd: 'skyfolk/media/',   
                src: ['**/*.{png,jpg,gif}'],
                dest: ''
            }]
        }
    },
});

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-contrib-imagemin');


    grunt.registerTask('default', ['sass', 'uglify', 'imagemin']);
};
