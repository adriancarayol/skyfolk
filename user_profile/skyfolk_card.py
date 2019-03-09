class SkyfolkCardIdentifier:
    def __init__(self):
        self.id = 0
        self.profile = None
        self.videos = 0
        self.photos = 0
        self.tags = None
        self.followers = 0
        self.likes = 0
        self.exp = 0

    def __repr__(self):
        return "<SkyfolkCardIdentifier id={} profile={} videos={} photos={} tags={} followers={} likes={} exp={}>".format(
            self.id, self.profile, self.videos, self.photos, self.tags, self.followers, self.likes, self.exp
        )
