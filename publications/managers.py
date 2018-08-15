from mptt.managers import TreeManager


class PublicationManager(TreeManager):
    """
    Manager para las publicaciones
    del skyline
    """

    def get_queryset(self):
        return super().get_queryset()

    def get_publications_by_board_owner(self, board_owner):
        return self.get_active_and_not_deleted_publications().filter(board_owner=board_owner)

    def get_publications_by_author(self, author):
        return self.get_active_and_not_deleted_publications().filter(author=author)

    def get_active_and_not_deleted_publications(self):
        return super().get_queryset().filter(author__is_active=True, deleted=False, board_owner__is_active=True)
