class AwardRegister(object):
    def __init__(self):
        self.awards_recipes = []

    def register(self, *recipes):
        for recipe in recipes:
            self.awards_recipes.append(recipe)


award_register = AwardRegister()


class BaseAwardRecipe(object):
    name = None
    description = None
    reached_with = 0


class BronzeUserRank(BaseAwardRecipe):
    name = "Bronce"
    description = "Recién llegado"
    reached_with = 5


class SilverUserRank(BaseAwardRecipe):
    name = "Plata"
    description = "Cogiendo forma"
    reached_with = 25


class GoldUserRank(BaseAwardRecipe):
    name = "Oro"
    description = "¡Esto se te da bien!"
    reached_with = 65


class PlatinumUserRank(BaseAwardRecipe):
    name = "Platino"
    description = "Subiendo como la espuma"
    reached_with = 85


award_register.register(
    BaseAwardRecipe, BronzeUserRank, SilverUserRank, GoldUserRank, PlatinumUserRank
)
