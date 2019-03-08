from user_profile.skyfolk_card import SkyfolkCardIdentifier


class FactorySkyfolkCardIdentifier(object):
    @staticmethod
    def create():
        skyfolk_card_identifier = SkyfolkCardIdentifier()
        skyfolk_card_identifier.id = 0
        skyfolk_card_identifier.likes = 0
        skyfolk_card_identifier.followers = 0
        skyfolk_card_identifier.profile = None
        skyfolk_card_identifier.exp = 0
        skyfolk_card_identifier.videos = 0
        skyfolk_card_identifier.photos = 0
        skyfolk_card_identifier.tags = []
        return skyfolk_card_identifier
