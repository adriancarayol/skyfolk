$(document).ready(function() {
    var onLightboxOpen = function() {
        $('.submenu').hide();
    };

    var onLightboxAddPluginOpen = function() {
        $('.submenu').hide();
        $('select').material_select();
    };


    // Add dashboard plugin.
    $('.add-plugin').colorbox({
        'width': '576px',
        'height': '550px',
        'opacity': '0.5',
        'onComplete': onLightboxAddPluginOpen
    });

    // Show all workspaces.
    $('.menu-dashboard-workspaces').colorbox({
        'width': '576px',
        'height': '400px',
        'opacity': '0.5',
        'onComplete': onLightboxOpen
    });

    // Handling AJAX delete plugin widget requests.
    $('.remove-plugin').bind('click', function() {
        var el = $(this);
        $.getJSON($(this).attr('href'), function(data) {
            if (data.success) {
                el.closest('.plugin').replaceWith(data.cell);
                $('.add-plugin').colorbox({
                    'width': '576px',
                    'height': '550px',
                    'opacity': '0.5',
                    'onComplete': onLightboxAddPluginOpen
                });
            }
        });
        return false;
    });

    // Submenu.
    $('.menu-dashboard-settings').bind('click', function() {
        $('.submenu').toggle();
    });

    // Create dashboard workspace.
    $('a.menu-dashboard-create-workspace').colorbox({
        'width': '576px',
        'height': '420px',
        'opacity': '0.5',
        'onComplete': onLightboxOpen
    });

    // Edit dashboard workspace.
    $('a.menu-dashboard-edit-workspace').colorbox({
        'width': '576px',
        'height': '420px',
        'opacity': '0.5',
        'onComplete': onLightboxOpen
    });

    // Edit dashboard settings
    $('a.menu-dashboard-edit-settings').colorbox({
        'width': '576px',
        'height': '570px',
        'opacity': '0.5',
        'onComplete': onLightboxOpen
    });

    // Delete dashboard workspace.
    $('a.menu-dashboard-delete-workspace').colorbox({
        'width': '576px',
        'height': '300px',
        'opacity': '0.5',
        'onComplete': onLightboxOpen
    });
});
