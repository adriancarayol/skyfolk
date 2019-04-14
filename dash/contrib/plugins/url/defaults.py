from django.utils.translation import ugettext_lazy as _

__title__ = "dash.contrib.plugins.url.defaults"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2013-2017 Artur Barseghyan"
__license__ = "GPL 2.0/LGPL 2.1"
__all__ = (
    "BOOKMARK_IMAGE_CHOICES",
    "BOOKMARK_IMAGE_CHOICES_WITH_EMPTY_OPTION",
    "IMAGE_CHOICES",
    "IMAGE_CHOICES_WITH_EMPTY_OPTION",
)


IMAGE_CHOICES = (
    ("movie", _("Film")),
    ("free_breakfast", _("Coffee")),
    ("date_range", _("Calendar")),
    ("book", _("Book")),
    ("music_note", _("Music")),
    ("photo", _("Picture")),
    ("rss_feed", _("RSS")),
    ("star", _("Star")),
    ("thumb_up", _("Thumbs-up")),
    ("tag_faces", _("Smile")),
    ("videogame_asset", _("Gamepad")),
    ("airplanemode_active", _("Plane")),
    ("camera_alt", _("Camera")),
    ("file_download", _("Download")),
    ("kitchen", _("Food")),
    ("info", _("Info")),
    ("shopping_cart", _("Shopping cart")),
    ("settings", _("Wrench")),
    ("lock", _("Lock")),
    ("question_answer", _("Question")),
    ("headset", _("Headphones")),
    ("card_giftcard", _("Gift")),
    ("vpn_key", _("Key")),
    ("comment", _("Comment")),
    ("bug_report", _("Bug")),
    ("notifications", _("Bell")),
    ("search", _("Search")),
    ("add_location", _("Map marker")),
    ("edit", _("Pencil")),
    ("schedule", _("Tasks")),
)

IMAGE_CHOICES_WITH_EMPTY_OPTION = [("", "---------")] + list(IMAGE_CHOICES)

BOOKMARK_IMAGE_CHOICES = (
    # Icons that are also present in `URLPlugin`.
    ("icon-film", _("Film")),
    # ('icon-coffee', _("Coffee")),
    ("icon-calendar", _("Calendar")),
    ("icon-book", _("Book")),
    ("icon-music", _("Music")),
    ("icon-picture", _("Picture")),
    # ('icon-rss-sign', _("RSS")),
    ("icon-star", _("Star")),
    ("icon-thumbs-up", _("Thumbs-up")),
    # ('icon-smile', _("Smile")),
    # ('icon-gamepad', _("Gamepad")),
    ("icon-plane", _("Plane")),
    ("icon-road", _("Road")),
    ("icon-camera", _("Camera")),
    ("icon-download", _("Download")),
    # ('icon-food', _("Food")),
    ("icon-info-sign", _("Info")),
    ("icon-shopping-cart", _("Shopping cart")),
    # ('icon-truck', _("Truck")),
    ("icon-wrench", _("Wrench")),
    # ('icon-facebook', _("Facebook")),
    # ('icon-github', _("Github")),
    # ('icon-google-plus', _("Google plus")),
    # ('icon-linkedin', _("LinkedIn")),
    # ('icon-pinterest', _("Pinterest")),
    # ('icon-twitter', _("Twitter")),
    # ('icon-youtube', _("Youtube")),
    # ('icon-bitbucket', _("Bitbucket")),
    # ('icon-android', _("Android")),
    # ('icon-apple', _("Apple")),
    # ('icon-windows', _("Windows")),
    # ('icon-tumblr-sign', _("Tumblr")),
    # ('icon-instagram', _("Instagram")),
    # ('icon-dropbox', _("Dropbox")),
    # ('icon-trophy', _("Trophy")),
    # ('icon-legal', _("Legal")),
    ("icon-lock", _("Lock")),
    ("icon-heart", _("Heart")),
    ("icon-question-sign", _("Question")),
    ("icon-headphones", _("Headphones")),
    ("icon-gift", _("Gift")),
    # ('icon-key', _("Key")),
    # ('icon-female', _("Female")),
    # ('icon-male', _("Male")),
    ("icon-comment", _("Comment")),
    # ('icon-bug', _("Bug")),
    ("icon-bell", _("Bell")),
    ("icon-search", _("Search")),
    ("icon-map-marker", _("Map marker")),
    ("icon-globe", _("Globe")),
    ("icon-pencil", _("Pensil")),
    ("icon-tasks", _("Tasks")),
)

BOOKMARK_IMAGE_CHOICES_WITH_EMPTY_OPTION = [("", "---------")] + list(
    BOOKMARK_IMAGE_CHOICES
)
