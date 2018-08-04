import graphene
import dash.schema


class Query(dash.schema.Query, graphene.ObjectType):
	pass


class Mutation(dash.schema.Mutation, graphene.ObjectType):
	pass


schema = graphene.Schema(query=Query, mutation=Mutation)
