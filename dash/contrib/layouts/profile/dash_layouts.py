from dash.base import BaseDashboardLayout, BaseDashboardPlaceholder
from dash.base import layout_registry


class ProfileMainPlaceholder(BaseDashboardPlaceholder):
    """Main placeholder."""

    uid = 'main'
    cols = 1
    rows = 4
    cell_width = 90
    cell_height = 100


class ProfileShortcutsPlaceholder(BaseDashboardPlaceholder):
    """Shortcuts placeholder."""

    uid = 'shortcuts'
    cols = 1
    rows = 10
    cell_width = 60
    cell_height = 55


class ProfileLayout(BaseDashboardLayout):
    """Profile layout."""

    uid = 'profile'
    name = 'Profile'
    view_template_name = 'profile/view_layout.html'
    edit_template_name = 'profile/edit_layout.html'
    placeholders = [ProfileMainPlaceholder]
    cell_units = '%'
    media_css = (
        'css/dash_dotted_borders.css',
        'css/dash_layout_profile.css',
    )
    # media_js = ('js/dash_layout_android.js',)


layout_registry.register(ProfileLayout)
