$(document).ready(function () {
    var onLightboxOpen = function () {
        $('.submenu').hide();
    };

    // Add dashboard plugin.
    $('.container').on('click', '.add-plugin', function () {
        var url = $(this).attr('href');
        let list_of_plugins = $('#list_of_plugins');
        let progress_bar = list_of_plugins.find('.progress');
        progress_bar.show();
        $.get(url, function (data) {
            $(window).scrollTop(0);
            list_of_plugins.find('.content').html(data);
            list_of_plugins.show();
            progress_bar.hide();
        });
        return false;
    });

    $('#close_list_of_plugins').click(function () {
        let list_of_plugins = $('#list_of_plugins');
        let progress_bar = list_of_plugins.find('.progress');
        progress_bar.show();
        $(this).closest(list_of_plugins).hide();
    });

    // Show all workspaces.
    $('.menu-dashboard-workspaces').colorbox({
        'width': '576px',
        'height': '400px',
        'opacity': '0.5',
        'onComplete': onLightboxOpen
    });

    // Handling AJAX delete plugin widget requests.
    $('.remove-plugin').bind('click', function () {
        var el = $(this);
        $.getJSON($(this).attr('href'), function (data) {
            if (data.success) {
                el.closest('.plugin').replaceWith(data.cell);
            }
        });
        return false;
    });

    // Create dashboard workspace.
    $('.container').on('click', '.menu-dashboard-create-workspace', function () {
        var url = $(this).attr('href');
        let list_of_plugins = $('#list_of_plugins');
        let progress_bar = list_of_plugins.find('.progress');
        progress_bar.show();
        $.get(url, function (data) {
            $(window).scrollTop(0);
            list_of_plugins.find('.content').html(data);
            list_of_plugins.show();
            progress_bar.hide();
        });
        return false;
    });

    // Edit dashboard workspace.

    $('.container').on('click', '.menu-dashboard-edit-workspace', function () {
        var url = $(this).attr('href');
        let list_of_plugins = $('#list_of_plugins');
        let progress_bar = list_of_plugins.find('.progress');
        progress_bar.show();
        $.get(url, function (data) {
            $(window).scrollTop(0);
            list_of_plugins.find('.content').html(data);
            list_of_plugins.show();
            progress_bar.hide();
        });
        return false;
    });

    // Edit dashboard settings
    $('.container').on('click', '.menu-dashboard-edit-settings', function () {
        var url = $(this).attr('href');
        let list_of_plugins = $('#list_of_plugins');
        let progress_bar = list_of_plugins.find('.progress');
        progress_bar.show();
        $.get(url, function (data) {
            $(window).scrollTop(0);
            list_of_plugins.find('.content').html(data);
            list_of_plugins.show();
            progress_bar.hide();
        });
        return false;
    });

    // Delete dashboard workspace.

    $('.container').on('click', '.menu-dashboard-delete-workspace', function () {
        var url = $(this).attr('href');
        let list_of_plugins = $('#list_of_plugins');
        let progress_bar = list_of_plugins.find('.progress');
        progress_bar.show();
        $.get(url, function (data) {
            $(window).scrollTop(0);
            list_of_plugins.find('.content').html(data);
            list_of_plugins.show();
            progress_bar.hide();
        });
        return false;
    });

});
