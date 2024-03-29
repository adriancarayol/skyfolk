from ....base import BaseDashboardLayout, BaseDashboardPlaceholder, layout_registry

__title__ = "dash.contrib.layouts.skyspace.dash_layouts"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2013-2017 Artur Barseghyan"
__license__ = "GPL 2.0/LGPL 2.1"
__all__ = ("SkySpaceLayout",)


class SkySpaceMainPlaceholder(BaseDashboardPlaceholder):
    """Main placeholder."""

    uid = "main"
    cols = 6
    rows = 5
    cell_width = 150
    cell_height = 110


class SkySpaceShortcutsPlaceholder(BaseDashboardPlaceholder):
    """Shortcuts placeholder."""

    uid = "shortcuts"
    cols = 1
    rows = 10
    cell_width = 60
    cell_height = 55


class SkySpaceLayout(BaseDashboardLayout):
    """Skyspace layout."""

    uid = "skyspace"
    name = "Skyspace"
    view_template_name = "skyspace/view_layout.html"
    edit_template_name = "skyspace/edit_layout.html"
    placeholders = [SkySpaceMainPlaceholder]
    cell_units = "px"
    media_css = ("css/dash_dotted_borders.css", "skyspace/css/dash_layout_skyspace.css")
    # media_js = ('js/dash_layout_android.js',)


layout_registry.register(SkySpaceLayout)
