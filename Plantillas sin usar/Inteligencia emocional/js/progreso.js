 window.onload = function onLoad() {
    var circle = new ProgressBar.Circle('#progress', {
        color: 'rgb(250,108,108)',
        duration: 1000,
        easing: 'easeInOut',
        text: {
        	value: '0'
        },
        step: function(state, bar) {
        	bar.setText((bar.value()*100).toFixed(0));
        }

    });

    circle.animate(1);
};
