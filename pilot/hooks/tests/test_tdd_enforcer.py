"""Tests for TDD enforcer hook."""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

from _checkers.tdd import (
    _find_dotnet_test_dirs,
    _find_test_dirs,
    _pascal_to_kebab,
    _search_test_dirs,
    has_go_test_file,
    has_python_test_file,
    has_test_importing_module,
    has_test_importing_module_ts,
    has_typescript_test_file,
    is_dotnet_logic_free,
    is_inside_dotnet_test_project,
    is_test_file,
    is_trivial_edit,
    run_tdd_enforcer,
    should_skip,
    warn,
)


class TestShouldSkip:
    def test_skips_markdown(self):
        assert should_skip("/project/README.md") is True

    def test_skips_json(self):
        assert should_skip("/project/package.json") is True

    def test_skips_excluded_dir(self):
        assert should_skip("/project/node_modules/foo.ts") is True
        assert should_skip("/project/dist/bundle.js") is True
        assert should_skip("/project/__pycache__/mod.pyc") is True

    def test_skips_migrations(self):
        assert should_skip("src/migrations/001_init.py") is True

    def test_does_not_skip_source_files(self):
        assert should_skip("/project/src/app.py") is False
        assert should_skip("/project/src/app.ts") is False
        assert should_skip("/project/main.go") is False

    def test_skips_dotnet_build_output_only_for_cs(self):
        assert should_skip("/project/obj/Debug/net8.0/App.AssemblyInfo.cs") is True
        assert should_skip("/project/bin/Release/net8.0/Foo.g.cs") is True

    def test_does_not_skip_non_dotnet_bin_source(self):
        assert should_skip("/project/bin/cli.py") is False
        assert should_skip("/project/src/bin/run.ts") is False


class TestIsTestFile:
    def test_python_test_prefix(self):
        assert is_test_file("test_foo.py") is True

    def test_python_test_suffix(self):
        assert is_test_file("foo_test.py") is True

    def test_python_impl(self):
        assert is_test_file("foo.py") is False

    def test_ts_test(self):
        assert is_test_file("Foo.test.ts") is True

    def test_ts_spec(self):
        assert is_test_file("Foo.spec.tsx") is True

    def test_ts_impl(self):
        assert is_test_file("Foo.ts") is False

    def test_go_test(self):
        assert is_test_file("foo_test.go") is True

    def test_go_impl(self):
        assert is_test_file("foo.go") is False


class TestFindTestDirs:
    def test_finds_tests_dir_in_parent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            tests = Path(tmpdir) / "tests"
            src.mkdir()
            tests.mkdir()

            dirs = _find_test_dirs(src)
            assert tests in dirs

    def test_finds_multiple_test_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src" / "lib"
            src.mkdir(parents=True)
            (Path(tmpdir) / "tests").mkdir()
            (Path(tmpdir) / "src" / "__tests__").mkdir()

            dirs = _find_test_dirs(src)
            assert len(dirs) >= 2

    def test_returns_empty_when_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            src.mkdir()

            dirs = _find_test_dirs(src)
            assert dirs == []


class TestPascalToKebab:
    def test_pascal_case(self):
        assert _pascal_to_kebab("VaultRoutes") == "vault-routes"

    def test_multi_word_pascal(self):
        assert _pascal_to_kebab("BaseRouteHandler") == "base-route-handler"

    def test_single_word(self):
        assert _pascal_to_kebab("App") == "app"

    def test_already_lowercase(self):
        assert _pascal_to_kebab("vault-routes") == "vault-routes"

    def test_camel_case(self):
        assert _pascal_to_kebab("vaultRoutes") == "vault-routes"

    def test_acronym_prefix(self):
        assert _pascal_to_kebab("APIClient") == "api-client"


class TestSearchTestDirs:
    def test_finds_matching_test_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tests = Path(tmpdir) / "tests"
            tests.mkdir()
            (tests / "Foo.test.ts").touch()

            assert _search_test_dirs([tests], "Foo", [".test.ts"]) is True

    def test_finds_nested_test_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tests = Path(tmpdir) / "tests" / "unit"
            tests.mkdir(parents=True)
            (tests / "Foo.test.ts").touch()

            assert _search_test_dirs([Path(tmpdir) / "tests"], "Foo", [".test.ts"]) is True

    def test_returns_false_when_no_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tests = Path(tmpdir) / "tests"
            tests.mkdir()
            (tests / "Bar.test.ts").touch()

            assert _search_test_dirs([tests], "Foo", [".test.ts"]) is False


class TestHasPythonTestFile:
    def test_finds_sibling_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "utils.py"
            impl.touch()
            (Path(tmpdir) / "test_utils.py").touch()

            assert has_python_test_file(str(impl)) is True

    def test_finds_sibling_test_suffix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "utils.py"
            impl.touch()
            (Path(tmpdir) / "utils_test.py").touch()

            assert has_python_test_file(str(impl)) is True

    def test_finds_test_in_tests_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            src.mkdir()
            impl = src / "utils.py"
            impl.touch()
            tests = Path(tmpdir) / "tests"
            tests.mkdir()
            (tests / "test_utils.py").touch()

            assert has_python_test_file(str(impl)) is True

    def test_finds_test_in_nested_tests_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            src.mkdir()
            impl = src / "utils.py"
            impl.touch()
            tests = Path(tmpdir) / "tests" / "unit"
            tests.mkdir(parents=True)
            (tests / "test_utils.py").touch()

            assert has_python_test_file(str(impl)) is True

    def test_returns_false_when_no_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "utils.py"
            impl.touch()

            assert has_python_test_file(str(impl)) is False


class TestHasTypescriptTestFile:
    def test_finds_sibling_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "Foo.ts"
            impl.touch()
            (Path(tmpdir) / "Foo.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_sibling_spec(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "Foo.ts"
            impl.touch()
            (Path(tmpdir) / "Foo.spec.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_tsx_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "App.tsx"
            impl.touch()
            (Path(tmpdir) / "App.test.tsx").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_test_in_tests_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            src.mkdir()
            impl = src / "Foo.ts"
            impl.touch()
            tests = Path(tmpdir) / "tests"
            tests.mkdir()
            (tests / "Foo.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_test_in_nested_tests_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src" / "services"
            src.mkdir(parents=True)
            impl = src / "Foo.ts"
            impl.touch()
            tests = Path(tmpdir) / "tests" / "services"
            tests.mkdir(parents=True)
            (tests / "Foo.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_test_in___tests___dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            src.mkdir()
            impl = src / "Foo.ts"
            impl.touch()
            tests = src / "__tests__"
            tests.mkdir()
            (tests / "Foo.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_kebab_case_test_in_tests_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src" / "services"
            src.mkdir(parents=True)
            impl = src / "VaultRoutes.ts"
            impl.touch()
            tests = Path(tmpdir) / "tests" / "worker"
            tests.mkdir(parents=True)
            (tests / "vault-routes.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_kebab_case_sibling_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "BaseRouteHandler.ts"
            impl.touch()
            (Path(tmpdir) / "base-route-handler.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_kebab_case_tsx_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "VaultStatus.tsx"
            impl.touch()
            (Path(tmpdir) / "vault-status.test.tsx").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_parent_dir_prefixed_test_in_tests_dir(self):
        """Test files inside a feature directory (e.g. views/Vault/VaultAssetDetail.tsx)
        are found when the test is named after the parent dir (e.g. vault-view.test.ts)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src" / "views" / "Vault"
            src.mkdir(parents=True)
            impl = src / "VaultAssetDetail.tsx"
            impl.touch()
            tests = Path(tmpdir) / "tests" / "ui"
            tests.mkdir(parents=True)
            (tests / "vault-view.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_parent_dir_prefixed_test_for_index(self):
        """index.tsx inside a feature dir is found via parent-dir-prefixed test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src" / "views" / "Usage"
            src.mkdir(parents=True)
            impl = src / "index.tsx"
            impl.touch()
            tests = Path(tmpdir) / "tests" / "ui"
            tests.mkdir(parents=True)
            (tests / "usage-view.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_finds_parent_dir_exact_test(self):
        """Parent dir exact match (e.g. vault.test.ts for files in Vault/)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src" / "views" / "Auth"
            src.mkdir(parents=True)
            impl = src / "LoginForm.tsx"
            impl.touch()
            tests = Path(tmpdir) / "tests"
            tests.mkdir()
            (tests / "auth.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is True

    def test_no_false_positive_from_unrelated_parent_prefix(self):
        """Don't match test files that happen to share a generic parent dir name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src" / "Foo"
            src.mkdir(parents=True)
            impl = src / "Bar.ts"
            impl.touch()
            tests = Path(tmpdir) / "tests"
            tests.mkdir()
            (tests / "baz.test.ts").touch()

            assert has_typescript_test_file(str(impl)) is False

    def test_returns_false_when_no_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "Foo.ts"
            impl.touch()

            assert has_typescript_test_file(str(impl)) is False

    def test_returns_false_for_non_ts(self):
        assert has_typescript_test_file("/project/foo.py") is False


class TestHasGoTestFile:
    def test_finds_sibling_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "handler.go"
            impl.touch()
            (Path(tmpdir) / "handler_test.go").touch()

            assert has_go_test_file(str(impl)) is True

    def test_finds_test_in_tests_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "pkg"
            src.mkdir()
            impl = src / "handler.go"
            impl.touch()
            tests = Path(tmpdir) / "tests"
            tests.mkdir()
            (tests / "handler_test.go").touch()

            assert has_go_test_file(str(impl)) is True

    def test_returns_false_when_no_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            impl = Path(tmpdir) / "handler.go"
            impl.touch()

            assert has_go_test_file(str(impl)) is False

    def test_returns_false_for_non_go(self):
        assert has_go_test_file("/project/foo.py") is False


class TestIsTrivialEdit:
    def test_import_only_edit(self):
        assert (
            is_trivial_edit(
                "Edit",
                {
                    "old_string": "import os",
                    "new_string": "import os\nimport sys",
                },
            )
            is True
        )

    def test_non_edit_tool(self):
        assert (
            is_trivial_edit(
                "Write",
                {
                    "old_string": "import os",
                    "new_string": "import sys",
                },
            )
            is False
        )

    def test_code_removal(self):
        assert (
            is_trivial_edit(
                "Edit",
                {
                    "old_string": "a = 1\nb = 2\nc = 3",
                    "new_string": "a = 1\nc = 3",
                },
            )
            is True
        )

    def test_constant_addition(self):
        assert (
            is_trivial_edit(
                "Edit",
                {
                    "old_string": "FOO = 1",
                    "new_string": "FOO = 1\nBAR = 2",
                },
            )
            is True
        )

    def test_non_trivial_edit(self):
        assert (
            is_trivial_edit(
                "Edit",
                {
                    "old_string": "return x + 1",
                    "new_string": "return x + 2",
                },
            )
            is False
        )


class TestWarn:
    def test_returns_0_and_outputs_suppressed_context(self, capsys):
        result = warn("No test file", "Create test_foo.py first.")
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["continue"] is True
        assert data["suppressOutput"] is True
        assert "decision" not in data
        context = data["hookSpecificOutput"]["additionalContext"]
        assert "No test file" in context
        assert "Create test_foo.py first." in context
        assert captured.err == ""


class TestHasTestImportingModule:
    def test_detects_from_import_flat_layout(self, tmp_path: Path):
        impl = tmp_path / "src" / "auth.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("def authenticate(): pass\n")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_login_flow.py").write_text("from src.auth import authenticate\n")
        assert has_test_importing_module(str(impl)) is True

    def test_detects_from_import_sibling_of_parent_layout(self, tmp_path: Path):
        impl = tmp_path / "hooks" / "_checkers" / "auth.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("def authenticate(): pass\n")
        tests = tmp_path / "hooks" / "tests"
        tests.mkdir(parents=True)
        (tests / "test_auth_hook.py").write_text("from _checkers.auth import authenticate\n")
        assert has_test_importing_module(str(impl)) is True

    def test_detects_plain_import(self, tmp_path: Path):
        impl = tmp_path / "src" / "auth.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("def authenticate(): pass\n")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_login_flow.py").write_text("import src.auth\n")
        assert has_test_importing_module(str(impl)) is True

    def test_detects_from_package_import_module(self, tmp_path: Path):
        impl = tmp_path / "src" / "auth.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("def authenticate(): pass\n")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_login_flow.py").write_text("from src import auth\n")
        assert has_test_importing_module(str(impl)) is True

    def test_detects_from_package_import_module_with_alias(self, tmp_path: Path):
        impl = tmp_path / "src" / "auth.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("def authenticate(): pass\n")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_login_flow.py").write_text("from src import auth as auth_module\n")
        assert has_test_importing_module(str(impl)) is True

    def test_returns_false_when_no_test_imports(self, tmp_path: Path):
        impl = tmp_path / "src" / "auth.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("def authenticate(): pass\n")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_unrelated.py").write_text("from src.other import foo\n")
        assert has_test_importing_module(str(impl)) is False

    def test_skips_when_module_is_dunder_init(self, tmp_path: Path):
        impl = tmp_path / "src" / "__init__.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("")
        assert has_test_importing_module(str(impl)) is False


class TestHasTestImportingModuleTs:
    def test_detects_import_in_ts_test(self, tmp_path: Path):
        impl = tmp_path / "src" / "auth.ts"
        impl.parent.mkdir(parents=True)
        impl.write_text("export function authenticate() {}\n")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "login-flow.test.ts").write_text('import { authenticate } from "../src/auth";\n')
        assert has_test_importing_module_ts(str(impl)) is True

    def test_returns_false_when_no_test_imports(self, tmp_path: Path):
        impl = tmp_path / "src" / "auth.ts"
        impl.parent.mkdir(parents=True)
        impl.write_text("export function authenticate() {}\n")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "unrelated.test.ts").write_text('import { other } from "../src/other";\n')
        assert has_test_importing_module_ts(str(impl)) is False

    def test_skips_non_typescript_files(self, tmp_path: Path):
        impl = tmp_path / "src" / "auth.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("def authenticate(): pass\n")
        assert has_test_importing_module_ts(str(impl)) is False


class TestSoftenedWarnText:
    def test_python_warning_references_parsimony_not_create_test_file(self, capsys, tmp_path: Path, monkeypatch):
        impl = tmp_path / "src" / "lonely.py"
        impl.parent.mkdir(parents=True)
        impl.write_text("def foo(): pass\n")
        # No sibling test, no importing test, no failing-test cache.
        hook_input = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(impl),
                "old_string": "def foo(): pass",
                "new_string": "def foo(): return 1",
            },
        }
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(hook_input)))
        assert run_tdd_enforcer() == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        context = data["hookSpecificOutput"]["additionalContext"]
        assert "Consider creating test_" not in context
        assert "Test Parsimony" in context


class TestIsDotnetLogicFree:
    """Conservative detector: True only for provably logic-free C# (skip TDD); enforce on any doubt."""

    def _write(self, tmp_path: Path, name: str, body: str) -> str:
        f = tmp_path / name
        f.write_text(body)
        return str(f)

    # --- True: provably logic-free (skip the TDD reminder) ---

    def test_interface_signatures_only_is_logic_free(self, tmp_path: Path):
        path = self._write(
            tmp_path,
            "IRepository.cs",
            "namespace App;\npublic interface IRepository\n{\n    Task<int> CountAsync();\n    string Name { get; }\n}\n",
        )
        assert is_dotnet_logic_free(path) is True

    def test_enum_only_is_logic_free(self, tmp_path: Path):
        path = self._write(tmp_path, "Status.cs", "namespace App;\npublic enum Status { Active, Disabled, Pending }\n")
        assert is_dotnet_logic_free(path) is True

    def test_positional_record_is_logic_free(self, tmp_path: Path):
        path = self._write(
            tmp_path, "PersonDto.cs", "namespace App;\npublic record PersonDto(string First, int Age);\n"
        )
        assert is_dotnet_logic_free(path) is True

    def test_poco_auto_properties_and_fields_is_logic_free(self, tmp_path: Path):
        body = (
            "namespace App;\n"
            "public class Order\n"
            "{\n"
            "    public const int MaxItems = 100;\n"
            "    public int Id { get; set; }\n"
            "    public string Name { get; init; }\n"
            "    private readonly string _tag;\n"
            "}\n"
        )
        path = self._write(tmp_path, "Order.cs", body)
        assert is_dotnet_logic_free(path) is True

    def test_poco_with_collection_initializer_is_logic_free(self, tmp_path: Path):
        """Field/property initializers (`= new()`, `= Factory()`) are not own-logic — DTO stays logic-free."""
        body = (
            "namespace App;\n"
            "public class Bag\n"
            "{\n"
            "    public List<string> Tags { get; set; } = new();\n"
            "    private static readonly int _max = Compute();\n"
            "}\n"
        )
        path = self._write(tmp_path, "Bag.cs", body)
        assert is_dotnet_logic_free(path) is True

    def test_poco_with_braced_initializer_is_logic_free(self, tmp_path: Path):
        """Braced collection/object initializers (`= new() { ... }`) are not own-logic.

        The `)` `{` of `new() {` must not be misread as a method body — these are the
        most common DTO initializer idioms and must stay logic-free.
        """
        body = (
            "namespace App;\n"
            "public class Bag\n"
            "{\n"
            "    public List<int> Xs { get; set; } = new() { 1, 2, 3 };\n"
            "    public List<int> Ys = new List<int>() { 4 };\n"
            "    public Inner I { get; } = new() { A = 1 };\n"
            "}\n"
        )
        path = self._write(tmp_path, "Bag.cs", body)
        assert is_dotnet_logic_free(path) is True

    def test_method_constructing_braced_initializer_still_enforces(self, tmp_path: Path):
        """A method body remains logic even when it assigns a braced initializer."""
        body = (
            "namespace App;\n"
            "public class Init\n"
            "{\n"
            "    public List<int> Items { get; set; }\n"
            "    public void Setup() { Items = new() { 1 }; }\n"
            "}\n"
        )
        path = self._write(tmp_path, "Init.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_xml_doc_comment_with_example_code_is_still_logic_free(self, tmp_path: Path):
        """Comment stripping: example code in /// must not force enforcement on a pure DTO."""
        body = (
            "namespace App;\n"
            "/// <summary>A point.</summary>\n"
            "/// <example>if (x) { return Foo(); } => bar</example>\n"
            "public record Point(int X, int Y);\n"
        )
        path = self._write(tmp_path, "Point.cs", body)
        assert is_dotnet_logic_free(path) is True

    def test_string_literal_does_not_force_skip_when_real_logic_present(self, tmp_path: Path):
        """A method body is real logic even if a string literal contains '}' — enforce."""
        body = 'namespace App;\npublic class Greeter\n{\n    public string Hi() { return "}"; }\n}\n'
        path = self._write(tmp_path, "Greeter.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_generic_class_with_new_constraint_is_logic_free(self, tmp_path: Path):
        """A `where T : new()` constraint introduces a bare `()` whose `)` must not be
        misread as a method body - a pure generic DTO stays logic-free."""
        body = "namespace App;\npublic class Repo<T> where T : new()\n{\n    public T Item { get; set; }\n}\n"
        path = self._write(tmp_path, "Repo.cs", body)
        assert is_dotnet_logic_free(path) is True

    def test_verbatim_interpolated_string_does_not_swallow_following_code(self, tmp_path: Path):
        r"""`@$"...\"` is a verbatim-interpolated string; mis-parsing it as a regular
        string would consume the closing quote (via `\"`) and swallow the trailing method
        body, hiding real logic. The stripper must close it correctly so logic is seen."""
        body = (
            "namespace App;\n"
            "public class Paths\n"
            "{\n"
            '    public string Root = @$"C:\\";\n'
            "    public int Calc(int x) { return x + 1; }\n"
            "}\n"
        )
        path = self._write(tmp_path, "Paths.cs", body)
        assert is_dotnet_logic_free(path) is False

    # --- False: any logic signal keeps enforcement ---

    def test_class_with_method_body_enforces(self, tmp_path: Path):
        body = "namespace App;\npublic class Calc\n{\n    public int Add(int a, int b)\n    {\n        return a + b;\n    }\n}\n"
        path = self._write(tmp_path, "Calc.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_expression_bodied_property_over_backing_field_enforces(self, tmp_path: Path):
        body = "namespace App;\npublic class Name\n{\n    private string _name;\n    public string Value => _name;\n}\n"
        path = self._write(tmp_path, "Name.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_manual_get_accessor_body_enforces(self, tmp_path: Path):
        body = (
            "namespace App;\n"
            "public class Temp\n"
            "{\n"
            "    private int _c;\n"
            "    public int Celsius { get { return _c; } set { _c = value; } }\n"
            "}\n"
        )
        path = self._write(tmp_path, "Temp.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_constructor_body_enforces(self, tmp_path: Path):
        body = (
            "namespace App;\n"
            "public class Widget\n"
            "{\n"
            "    public int Id { get; set; }\n"
            "    public Widget(int id)\n"
            "    {\n"
            "        Id = id;\n"
            "    }\n"
            "}\n"
        )
        path = self._write(tmp_path, "Widget.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_default_interface_method_with_body_enforces(self, tmp_path: Path):
        body = 'namespace App;\npublic interface IGreeter\n{\n    string Hello() => "hi";\n}\n'
        path = self._write(tmp_path, "IGreeter.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_generic_constrained_method_body_enforces(self, tmp_path: Path):
        """A generic method's `where` constraint sits between `)` and `{`; the body is still logic.

        The body uses no statement keyword and no `=>`, so only the `)`...`{` body check can
        catch it — the constraint must not let real logic slip through as logic-free.
        """
        body = (
            "namespace App;\n"
            "public class Registrar\n"
            "{\n"
            "    public void Register<T>(IServiceCollection services) where T : class\n"
            "    {\n"
            "        services.AddSingleton<T>();\n"
            "    }\n"
            "}\n"
        )
        path = self._write(tmp_path, "Registrar.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_event_accessor_body_enforces(self, tmp_path: Path):
        """Explicit event add/remove accessors carry executable logic — enforce."""
        body = (
            "namespace App;\n"
            "public class Publisher\n"
            "{\n"
            "    private EventHandler _handlers;\n"
            "    public event EventHandler Changed\n"
            "    {\n"
            "        add { _handlers += value; }\n"
            "        remove { _handlers -= value; }\n"
            "    }\n"
            "}\n"
        )
        path = self._write(tmp_path, "Publisher.cs", body)
        assert is_dotnet_logic_free(path) is False

    def test_razor_is_never_logic_free(self, tmp_path: Path):
        path = self._write(tmp_path, "Counter.razor", "<h1>Count</h1>\n")
        assert is_dotnet_logic_free(path) is False

    def test_missing_file_enforces(self, tmp_path: Path):
        assert is_dotnet_logic_free(str(tmp_path / "DoesNotExist.cs")) is False

    def test_no_type_declaration_enforces(self, tmp_path: Path):
        """A .cs file with only usings/attributes (no type) is ambiguous — enforce."""
        path = self._write(
            tmp_path, "AssemblyInfo.cs", 'using System;\n[assembly: System.Reflection.AssemblyVersion("1.0")]\n'
        )
        assert is_dotnet_logic_free(path) is False


class TestFindDotnetTestDirs:
    """Test-project detection must match .NET conventions without matching lookalike words."""

    def test_matches_test_projects_but_not_words_ending_in_test(self, tmp_path: Path):
        for name in (
            "MyApp.Tests",
            "MyApp.Test",
            "IntegrationTests",
            "FooTest",
            "tests",
            "latest",
            "contest",
            "greatest",
        ):
            (tmp_path / name).mkdir()
        src = tmp_path / "src"
        src.mkdir()

        found = {p.name for p in _find_dotnet_test_dirs(src)}

        assert {"MyApp.Tests", "MyApp.Test", "IntegrationTests", "FooTest", "tests"} <= found
        assert found & {"latest", "contest", "greatest"} == set()


class TestIsInsideDotnetTestProject:
    """is_inside_dotnet_test_project: name heuristic + .csproj guard."""

    def test_real_test_project_with_csproj_detected(self, tmp_path: Path) -> None:
        proj = tmp_path / "MyApp.Tests"
        proj.mkdir()
        (proj / "MyApp.Tests.csproj").write_text("")
        helper = proj / "TestHelpers.cs"
        helper.write_text("")
        assert is_inside_dotnet_test_project(str(helper)) is True

    def test_production_dir_named_context_test_without_csproj_not_detected(self, tmp_path: Path) -> None:
        """ContextTest ends with 'Test' in PascalCase but is a production domain folder."""
        ctx = tmp_path / "ContextTest"
        ctx.mkdir()
        impl = ctx / "MyService.cs"
        impl.write_text("")
        assert is_inside_dotnet_test_project(str(impl)) is False

    def test_integration_tests_dir_with_csproj_detected(self, tmp_path: Path) -> None:
        proj = tmp_path / "IntegrationTests"
        proj.mkdir()
        (proj / "IntegrationTests.csproj").write_text("")
        f = proj / "AuthTests.cs"
        f.write_text("")
        assert is_inside_dotnet_test_project(str(f)) is True

    def test_file_with_no_test_project_ancestor_not_detected(self, tmp_path: Path) -> None:
        src = tmp_path / "src" / "MyApp"
        src.mkdir(parents=True)
        impl = src / "OrderService.cs"
        impl.write_text("")
        assert is_inside_dotnet_test_project(str(impl)) is False
