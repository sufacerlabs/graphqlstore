"""Transform GraphQL schema to client schema."""

from graphql.error import GraphQLError
from graphql.language import parse
from graphql.language.ast import DirectiveNode, FieldDefinitionNode
from graphql.language.printer import print_ast
from graphql.language.visitor import IDLE, REMOVE, Visitor, visit


def transform_schema_graphql(schema: str) -> str:
    """Transform GraphQL schema to client schema."""
    try:
        ast = parse(schema)

        class RemoveDirectivesVisitor(Visitor):
            """Remove visitor directive from the AST and \
                protected fields."""

            def enter(self, node, *_):
                """Enter node in the traversal."""
                if isinstance(node, DirectiveNode):
                    return REMOVE

                if isinstance(node, FieldDefinitionNode):
                    for directive in node.directives:
                        if directive.name.value == "protected":
                            return REMOVE

                return IDLE

        new_ast = visit(ast, RemoveDirectivesVisitor())

        return print_ast(new_ast)
    except GraphQLError as e:
        raise ValueError(f"Error transforming schema: {str(e)}") from e
