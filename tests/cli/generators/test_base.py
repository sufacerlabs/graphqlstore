"""Tests for the BaseSchemaGenerator abstract base class."""

from typing import Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

from source.cli.generators.base import BaseSchemaGenerator
from source.cli.graphql.configuracion_y_constantes import (
    DatabaseType,
    InfoEnum,
    InfoRelacion,
    InfoTabla,
    TipoRelacion,
)


class ConcreteSchemaGenerator(BaseSchemaGenerator):
    """Concrete implementation of BaseSchemaGenerator for testing."""

    def get_type_mapping(self) -> Dict[str, str]:
        return {
            "ID": "VARCHAR(25)",
            "String": "VARCHAR(255)",
            "Int": "INTEGER",
            "Float": "FLOAT",
            "Boolean": "BOOLEAN",
        }

    def get_engine_specific_settings(self) -> str:
        return "TEST_ENGINE_SETTINGS"

    def get_table_creation_template(self) -> str:
        return "CREATE TABLE {table_name} ({columns}) {engine_settings};"

    def get_foreign_key_template(
        self,
        table_fk: str,
        field_fk: str,
        unique: str,
        constraint: str,
        table_ref: str,
        on_delete: str,
        is_null: str,
    ) -> str:
        return (
            f"ALTER TABLE `{table_fk}`\n"
            f" ADD COLUMN `{field_fk}`{unique}{is_null},\n"
            f"ADD CONSTRAINT `{constraint}` FOREIGN KEY (`{field_fk}`) "
            f"REFERENCES `{table_ref}`(id) {on_delete};"
        )

    def get_unique_constraint_template(self) -> str:
        return "UNIQUE ({column})"

    def get_primary_key_column(self) -> str:
        return "id VARCHAR(25) PRIMARY KEY"

    def format_enum_values(self, valores: List[str]) -> str:
        return f"ENUM({', '.join(valores)})"

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.MYSQL

    def _generate_tables(
        self,
        tables: Dict[str, InfoTabla],
        enums: Dict[str, InfoEnum],
        print_output: bool = True,
        print_sql: bool = True,
    ) -> str:
        return "MOCK_TABLES_SQL"

    def _generate_table(
        self,
        table_name: str,
        table_info: InfoTabla,
        enums: Dict[str, InfoEnum],
    ) -> str:
        return f"CREATE TABLE {table_name} (id VARCHAR(25) PRIMARY KEY);"

    def _generate_relationships(
        self,
        tables: Dict[str, InfoTabla],
        relationships: List[InfoRelacion],
    ) -> str:
        return "MOCK_RELATIONSHIPS_SQL"

    def _generate_relationship(
        self,
        relationship: InfoRelacion,
        tables: Dict[str, InfoTabla],
    ) -> Optional[str]:
        return "MOCK_RELATIONSHIP_SQL"


class TestBaseSchemaGenerator:
    """Tests for BaseSchemaGenerator abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseSchemaGenerator cannot be instantiated directly."""
        with pytest.raises(TypeError) as excinfo:
            # pylint: disable=abstract-class-instantiated
            BaseSchemaGenerator()
            # pylint: enable=abstract-class-instantiated
        assert "abstract class" in str(excinfo.value)

    def test_concrete_class_can_be_instantiated(self):
        """Test that a concrete subclass can be instantiated."""
        generator = ConcreteSchemaGenerator()
        assert isinstance(generator, BaseSchemaGenerator)
        assert isinstance(generator, ConcreteSchemaGenerator)

    def test_abstract_methods_must_be_implemented(self):
        """Test that all abstract methods must be implemented."""

        # This is an example of what happens if we try to create a subclass
        # that doesn't implement all required methods
        class IncompleteGenerator(BaseSchemaGenerator):
            """A subclass that doesn't implement all abstract methods."""

            def get_type_mapping(self):
                return {}

        with pytest.raises(TypeError) as excinfo:
            # pylint: disable=abstract-class-instantiated
            IncompleteGenerator()
            # pylint: enable=abstract-class-instantiated
        assert "abstract methods" in str(excinfo.value)

    def test_generate_schema_calls_required_methods(self):
        """Test that generate_schema calls the required methods."""
        generator = ConcreteSchemaGenerator()

        # Create spy methods
        # pylint: disable=protected-access
        generator._generate_tables = MagicMock(return_value="TABLES")
        generator._generate_relationships = MagicMock(
            return_value="RELATIONSHIPS",
        )

        mock_tables = {"Table1": MagicMock()}
        mock_enums = {"Enum1": MagicMock()}
        mock_relationships = [MagicMock()]

        result = generator.generate_schema(
            mock_tables, mock_enums, mock_relationships, True, True
        )

        # Check that methods were called with correct arguments
        generator._generate_tables.assert_called_once_with(
            mock_tables, mock_enums, True, True
        )
        generator._generate_relationships.assert_called_once_with(
            mock_tables, mock_relationships
        )

        # Check the result combines the outputs correctly
        assert result == "TABLES\n\nRELATIONSHIPS"

        # pylint: enable=protected-access

    def test_get_schema_sql(self):
        """Test the get_schema_sql method."""
        generator = ConcreteSchemaGenerator()
        generator.schema_sql = ["SQL1", "SQL2", "SQL3"]

        assert generator.get_schema_sql() == "SQL1\n\nSQL2\n\nSQL3"

    def test_print_output_tables(self):
        """Test the _print_output_tables method."""
        generator = ConcreteSchemaGenerator()
        generator.console = MagicMock()

        mock_table_info = MagicMock()
        mock_table_info.campos = {
            "field1": MagicMock(tipo_campo="String"),
            "field2": MagicMock(tipo_campo="Int"),
        }

        with (
            patch("source.cli.generators.base.Tree") as mock_tree,
            patch("source.cli.generators.base.Syntax") as mock_syntax,
            patch("source.cli.generators.base.Panel") as mock_panel,
        ):

            mock_tree_instance = mock_tree.return_value
            mock_panel_instance = mock_panel.return_value

            # pylint: disable=protected-access
            generator._print_output_tables(
                "TestTable", mock_table_info, "CREATE TABLE SQL", True
            )
            # pylint: enable=protected-access

            # Verify Tree was created
            mock_tree.assert_called_once()
            assert "TestTable" in str(mock_tree.call_args)

            # Verify console.print was called with Tree instance
            generator.console.print.assert_any_call(mock_tree_instance)

            # Verify Syntax and Panel were created for SQL
            mock_syntax.assert_called_once_with(
                "CREATE TABLE SQL", "sql", theme="monokai", line_numbers=True
            )
            mock_panel.assert_called_once()

            # Verify console.print was called with Panel instance
            generator.console.print.assert_any_call(mock_panel_instance)

            # Verify success message
            assert generator.console.print.call_count == 3
            assert "TestTable" in str(
                generator.console.print.call_args_list[2],
            )
            assert "successfully" in str(
                generator.console.print.call_args_list[2],
            )

    def test_print_output_relationships(self):
        """Test the _print_output_relationships method."""
        generator = ConcreteSchemaGenerator()
        generator.console = MagicMock()

        mock_relationship = MagicMock()
        mock_relationship.fuente.tabla_fuente = "SourceTable"
        mock_relationship.objetivo.tabla_objetivo = "TargetTable"
        mock_relationship.tipo_relation = TipoRelacion.ONE_TO_MANY.value

        with (
            patch("source.cli.generators.base.Tree") as mock_tree,
            patch("source.cli.generators.base.Syntax") as mock_syntax,
            patch("source.cli.generators.base.Panel") as mock_panel,
        ):

            mock_tree_instance = mock_tree.return_value
            mock_panel_instance = mock_panel.return_value

            # pylint: disable=protected-access
            generator._print_output_relationships(
                mock_relationship,
                "ALTER TABLE SQL",
                True,
                True,
                "TestRelationship",
            )
            # pylint: enable=protected-access

            # Verify Tree was created
            mock_tree.assert_called_once()
            assert "SourceTable" in str(
                mock_tree.call_args,
            ) or "TargetTable" in str(mock_tree.call_args)

            # Verify console.print was called with Tree instance
            generator.console.print.assert_any_call(mock_tree_instance)

            # Verify Syntax and Panel were created for SQL
            mock_syntax.assert_called_once_with(
                "ALTER TABLE SQL", "sql", theme="monokai", line_numbers=True
            )
            mock_panel.assert_called_once()

            # Verify console.print was called with Panel instance
            generator.console.print.assert_any_call(mock_panel_instance)

            # Verify success message
            assert generator.console.print.call_count == 3
            assert "SourceTable" in str(
                generator.console.print.call_args_list[2],
            )
            assert "TargetTable" in str(
                generator.console.print.call_args_list[2],
            )
            assert "successfull" in str(
                generator.console.print.call_args_list[2],
            )

    def test_different_relationship_types_output(self):
        """Test that different relationship types output correctly."""
        generator = ConcreteSchemaGenerator()
        generator.console = MagicMock()

        # Create different relationship types
        relationship_types = [
            (TipoRelacion.MANY_TO_MANY.value, "junction table"),
            (TipoRelacion.ONE_TO_ONE.value, "one-to-one"),
            (TipoRelacion.MANY_TO_ONE.value, "many-to-one"),
            (TipoRelacion.ONE_TO_MANY.value, "one-to-many"),
        ]

        for rel_type, expected_text in relationship_types:
            mock_relationship = MagicMock()
            mock_relationship.fuente.tabla_fuente = "SourceTable"
            mock_relationship.objetivo.tabla_objetivo = "TargetTable"
            mock_relationship.tipo_relation = rel_type

            with (
                patch("source.cli.generators.base.Tree"),
                patch("source.cli.generators.base.Syntax"),
                patch("source.cli.generators.base.Panel"),
            ):

                # Use different print options to test both branches
                # pylint: disable=protected-access
                generator._print_output_relationships(
                    mock_relationship,
                    f"SQL for {expected_text}",
                    True,
                    True,
                    "TestRel",
                )
                # pylint: enable=protected-access
