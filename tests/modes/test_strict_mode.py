from __future__ import annotations

from textwrap import dedent

from pytest import Pytester


def test_strict_mode_cmdline(pytester: Pytester):
    pytester.makeini("[pytest]\nasyncio_default_fixture_loop_scope = function")
    pytester.makepyfile(
        dedent(
            """\
        import asyncio
        import pytest

        pytest_plugins = 'pytest_asyncio'

        @pytest.mark.asyncio
        async def test_a():
            await asyncio.sleep(0)
        """
        )
    )
    result = pytester.runpytest("--asyncio-mode=strict")
    result.assert_outcomes(passed=1)


def test_strict_mode_cfg(pytester: Pytester):
    pytester.makeini(
        dedent(
            """\
            [pytest]
            asyncio_default_fixture_loop_scope = function
            asyncio_mode = strict
            """
        )
    )
    pytester.makepyfile(
        dedent(
            """\
        import asyncio
        import pytest

        pytest_plugins = 'pytest_asyncio'

        @pytest.mark.asyncio
        async def test_a():
            await asyncio.sleep(0)
        """
        )
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_strict_mode_method_fixture(pytester: Pytester):
    pytester.makeini("[pytest]\nasyncio_default_fixture_loop_scope = function")
    pytester.makepyfile(
        dedent(
            """\
        import asyncio
        import pytest
        import pytest_asyncio

        pytest_plugins = 'pytest_asyncio'

        class TestA:

            @pytest_asyncio.fixture
            async def fixture_a(self):
                await asyncio.sleep(0)
                return 1

            @pytest.mark.asyncio
            async def test_a(self, fixture_a):
                await asyncio.sleep(0)
                assert fixture_a == 1
        """
        )
    )
    result = pytester.runpytest("--asyncio-mode=auto")
    result.assert_outcomes(passed=1)


def test_strict_mode_ignores_unmarked_coroutine(pytester: Pytester):
    pytester.makeini("[pytest]\nasyncio_default_fixture_loop_scope = function")
    pytester.makepyfile(
        dedent(
            """\
        import pytest

        async def test_anything():
            pass
        """
        )
    )
    result = pytester.runpytest_subprocess("--asyncio-mode=strict", "-W default")
    result.assert_outcomes(skipped=1, warnings=1)
    result.stdout.fnmatch_lines(["*async def functions are not natively supported*"])


def test_strict_mode_ignores_unmarked_fixture(pytester: Pytester):
    pytester.makeini("[pytest]\nasyncio_default_fixture_loop_scope = function")
    pytester.makepyfile(
        dedent(
            """\
        import pytest

        # Not using pytest_asyncio.fixture
        @pytest.fixture()
        async def any_fixture():
            raise RuntimeError()

        async def test_anything(any_fixture):
            pass
        """
        )
    )
    result = pytester.runpytest_subprocess("--asyncio-mode=strict", "-W default")
    result.assert_outcomes(skipped=1, warnings=2)
    result.stdout.fnmatch_lines(
        [
            "*async def functions are not natively supported*",
            "*coroutine 'any_fixture' was never awaited*",
        ],
    )
