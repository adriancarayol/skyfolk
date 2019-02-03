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

    // Handling AJAX delete plugin widget requests.
    $('.remove-plugin').bind('click', function () {
        var el = $(this);
        $.getJSON($(this).attr('href'), function (data) {
            if (data.success) {
                if (data.add_button) {
                    let placeholder = el.closest('.placeholder');
                    let add_plugin = placeholder.find('.add-plugin');
                    if (!add_plugin.length) {
                        placeholder.prepend(data.add_button);
                    }
                    el.closest('.plugin').remove();
                }
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
    
    $(this).on('click', '.plugin .service-pin a', function(e) {
        e.preventDefault();
        let serviceId = $(this).closest('.plugin').attr('data-entry-id');
        let page = $(this).attr('href');
        let wrapper = $(this).closest('#api-results-' + serviceId);
        
        $.ajax({
            url: '/dashboard/pin/service/' + serviceId + '/' + page,
            type: 'GET',

            success: function (data) {
                wrapper.html(data.content);
            }
        });
    });

    $(this).on('click', '.plugin .follow-pin a', function(e) {
        e.preventDefault();
        let pinId = $(this).closest('.plugin').attr('data-entry-id');
        let page = $(this).attr('href');
        let wrapper = $(this).closest('.infinite-following');

        $.ajax({
            url: '/dashboard/pin/follows/' + pinId + '/' + page,
            type: 'GET',

            success: function (data) {
                wrapper.replaceWith(data.content);
            }
        });
    });
});
