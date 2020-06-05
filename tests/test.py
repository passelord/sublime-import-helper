import sublime
import sys
from unittest import TestCase

import_helper = sys.modules["ImportHelper.import_helper"]
utils = sys.modules["ImportHelper.utils"]


class TestDoInsertImport(TestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file()
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def getAll(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def test_smoke(self):
        setText(self.view, "")
        self.view.run_command(
            "paste_import",
            {
                "item": {
                    "filepath": "dinah_widdoes",
                    "name": "Lakia",
                    "isDefault": False,
                }
            },
        )
        first_row = self.getRow(0)
        self.assertTrue(first_row.startswith("import {"))
        self.assertIn("}", first_row)
        self.assertIn("Lakia", first_row)
        self.assertIn("dinah_widdoes", first_row)
        self.assertFalse(first_row.endswith(";"))

    def test_side_effect_import(self):
        setText(self.view, 'import "rxjs/operators/map"\n')
        self.view.run_command(
            "paste_import",
            {"item": {"filepath": "side/effect", "name": "effect", "isDefault": False}},
        )
        self.assertIn("./side/effect", self.getRow(1))

    def test_paste_import_if_imports_statements_in_the_middle(self):
        setText(self.view, ("\n" * 14) + 'import x from "x"\n')
        self.view.run_command(
            "paste_import",
            {"item": {"filepath": "filepath", "name": "name", "isDefault": False}},
        )
        self.assertNotIn("./filepath", self.getRow(0))
        self.assertNotIn("name", self.getRow(0))

    def test_add_specifier_to_default_import(self):
        setText(self.view, "import React from 'react'\n")
        self.view.run_command(
            "paste_import",
            {"item": {"name": "useCallback", "module": "react", "isDefault": False}},
        )
        self.assertIn("import React, { useCallback } from 'react", self.getRow(0))

    def test_add_specifier_to_mixed_import(self):
        setText(self.view, "import React, { useCallback } from 'react'\n")
        self.view.run_command(
            "paste_import",
            {"item": {"name": "useState", "module": "react", "isDefault": False}},
        )
        self.assertIn(
            "import React, { useCallback, useState } from 'react", self.getRow(0)
        )

    # These tests shows additional popup
    # def test_typescript_paths(self):
    #     typescript_paths = [
    #         {'path_to': '@Libs/*', 'path_value': './test_playground/lib/*', 'base_dir': '/base_dir'},
    #     ]
    #     setText(self.view, '')
    #     self.view.run_command('paste_import', {'item': {'filepath': '/base_dir/test_playground/lib/a/b/c.ts', 'name': 'name', 'isDefault': False }, 'typescript_paths': typescript_paths })
    #     self.assertIn('@Libs/a/b/c', self.getRow(0))

    # def test_typescript_paths_2(self):
    #     typescript_paths = [
    #         {'path_to': '@z_component', 'path_value': './app/components/z.ts', 'base_dir': '/base_dir'},
    #     ]
    #     setText(self.view, '')
    #     self.view.run_command('paste_import', {'item': {'filepath': '/base_dir/app/components/z.ts', 'name': 'zoo', 'isDefault': False }, 'typescript_paths': typescript_paths })
    #     self.assertIn("import {zoo} from '@z_component'", self.getRow(0))

    # def test_typescript_paths_3(self):
    #     typescript_paths = [
    #         {'path_to': '@components', 'path_value': './app/components', 'base_dir': '/base_dir'},
    #     ]
    #     setText(self.view, '')
    #     self.view.run_command('paste_import', {'item': {'filepath': '/base_dir/app/components/index.ts', 'name': 'koo', 'isDefault': False }, 'typescript_paths': typescript_paths })

    #     self.assertIn("import {koo} from '@components'", self.getRow(0))

    def test_remove_importpath_index(self):
        setText(self.view, "")
        self.view.run_command(
            "paste_import",
            {
                "item": {
                    "filepath": "./component/x/index",
                    "name": "x1",
                    "isDefault": False,
                }
            },
        )
        self.assertIn("import {x1} from './component/x'", self.getRow(0))
        self.view.run_command(
            "paste_import",
            {
                "item": {
                    "filepath": "./component/x/index",
                    "name": "x2",
                    "isDefault": False,
                }
            },
        )
        self.assertIn("import {x1, x2} from './component/x'", self.getRow(0))

    def test_paste_import_module(self):
        setText(self.view, "")
        self.view.run_command(
            "paste_import",
            {
                "item": {
                    "module": "@angular/core",
                    "specifier": "./debug/debug_node",
                    "isDefault": False,
                    "name": "Inject",
                }
            },
        )
        self.assertIn("import {Inject} from '@angular/core'", self.getRow(0))


class TestInitializeSetup(TestCase):
    def setUp(self):
        self.window = sublime.active_window()
        self.window.run_command("initialize_setup")

    def test_check_node_modules(self):
        yield 5000
        self.assertNotEqual(len(import_helper.node_modules), 0)

    def test_check_source_modules(self):
        yield 1000
        self.assertNotEqual(len(import_helper.source_modules), 0)

    def test_exclude_should_work(self):
        ignored = [
            item
            for item in import_helper.source_modules
            if "ignored" in item["filepath"]
        ]
        self.assertEqual(len(ignored), 0)


class TestUtilFunctions(TestCase):
    def test_debug_disabled(self):
        self.assertFalse(import_helper.DEBUG)

    def test_run_path_should_point_to_debug_version(self):
        run_path = import_helper.RUN_PATH
        self.assertIn("backend_run", run_path)

    def test_unixify(self):
        unixify = import_helper.unixify
        _ = "\\local\\some\\file"
        self.assertTrue(unixify(_) == "/local/some/file")

    def test_unixify_ts(self):
        unixify = import_helper.unixify
        _ = "some\\file.ts"
        self.assertTrue(unixify(_) == "some/file")

    def test_unixify_tsx(self):
        unixify = import_helper.unixify
        path = "d/file.tsx"
        self.assertTrue(unixify(path) == "d/file")

    def test_unixify_js(self):
        unixify = import_helper.unixify
        _ = "some\\file.js"
        self.assertTrue(unixify(_) == "some/file")

    def test_is_excluded_file(self):
        is_excluded_file = import_helper.is_excluded_file
        self.assertTrue(is_excluded_file("dir/file1.ts", ["*.ts"]))
        self.assertTrue(is_excluded_file("dir1/file1.ts", ["dir1"]))

    def test_get_setting(self):
        get_setting = import_helper.get_setting
        self.assertEqual(get_setting("insert_position", None), "end")
        self.assertEqual(get_setting("from_quote", None), "'")
        self.assertEqual(get_setting("space_around_braces", None), False)
        self.assertEqual(get_setting("from_semicolon", True), False)
        self.assertEqual(get_setting("unknown", "default_value"), "default_value")

    def test_find_executable(self):
        result = utils.find_executable("node")
        self.assertIn("node.exe", result)

    def test_get_import_root(self):
        get_import_root = import_helper.get_import_root
        result = get_import_root()
        self.assertTrue("ImportHelper" in result)

    def test_get_panel_item_negative_test(self):
        get_panel_item = import_helper.get_panel_item
        result = get_panel_item("/", {})
        self.assertTrue(result is None)

    def test_query_completions_modules(self):
        query_completions_modules = import_helper.query_completions_modules
        source_modules = [
            {"name": "good", "filepath": "/usr/home/good"},
            {"name": "ugly", "filepath": "/usr/home/ugly"},
        ]
        node_modules = [{"name": "Chicky", "module": "chicken"}]
        result = query_completions_modules("goo", source_modules, node_modules)
        self.assertListEqual(result, [["good\tsource_modules", "good"]])
        result = query_completions_modules("Chic", source_modules, node_modules)
        self.assertListEqual(result, [["Chicky\tnode_modules/chicken", "Chicky"]])

    def test_get_exclude_patterns_fault_tollerance(self):
        get_exclude_patterns = import_helper.get_exclude_patterns
        result = get_exclude_patterns({"folders": {}})
        self.assertDictEqual(result, {})

    def test_is_import_all(self):
        self.assertTrue(
            utils.is_import_all("import * as worker_threads from 'worker_threads'")
        )
        self.assertFalse(
            utils.is_import_all("import worker_threads from 'worker_threads'")
        )

    def test_is_import_default(self):
        self.assertFalse(
            utils.is_import_default("import * as worker_threads from 'worker_threads'")
        )
        self.assertTrue(
            utils.is_import_default("import worker_threads from 'worker_threads'")
        )
        self.assertTrue(utils.is_import_default("import React from 'react'"))
        self.assertFalse(
            utils.is_import_default("import React, { useState } from 'react'")
        )

    def test_is_import_mixed(self):
        self.assertFalse(utils.is_import_mixed("import React from 'react'"))
        self.assertTrue(
            utils.is_import_mixed("import React, { useState } from 'react'")
        )
        self.assertTrue(
            utils.is_import_mixed(
                "import React, { useState, useCallback } from 'react'"
            )
        )


class TestPasteImport(TestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file()
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def test_get_import_block(self):
        pass


class TestExample(TestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file()
        # make sure we have a window to work with
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def test_smoke(self):
        self.assertTrue(True)

    def test_hello_world(self):
        self.view.run_command("hello_world")
        first_row = self.getRow(0)


def setText(view, string):
    view.run_command("select_all")
    view.run_command("left_delete")
    view.run_command("insert", {"characters": string})
