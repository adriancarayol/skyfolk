from mptt.managers import TreeManager


class PublicationManager(TreeManager):
	"""
	Manager para las publicaciones
	del skyline
	"""
	def get_queryset(self):
		return super().get_queryset().filter(author__is_active=True, deleted=False)

	def get_publications_by_board_owner(self, board_owner):
		return self.filter(board_owner=board_owner)

	def get_publications_by_author(self, author):
		return self.filter(author=author)