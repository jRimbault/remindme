# TODO

Issues identified during tech lead review, organized by priority.

## Critical (Must Fix Before 1.0)

- [x] **#7**: Add comprehensive test suite
  - Unit tests for `parse_duration()`, `parse_when()`, `format_systemd_duration()`
  - Backend availability tests (mock `shutil.which()`)
  - `parse_backend()` tests for error cases
  - Integration tests with mocked `subprocess.run()`
  - **DONE**: 66 tests, 85% code coverage

- [x] **#11**: Add test execution to CI pipeline
  - Configure pytest in CI workflow
  - Add coverage reporting
  - Fail builds on test failures
  - **DONE**: Separate test job in GitHub Actions with coverage artifacts

## Major (Should Fix Soon)

- [x] **#13**: Add smoke tests to CI
  - Test `--help` works
  - Test subcommand help works
  - Verify basic argument parsing
  - **DONE**: Integration tests in pytest via subprocess (73 tests total, 85% coverage)

## Minor (Nice to Have)

- [x] **#1**: Simplify AutoBackend initialization
  - Remove lazy evaluation complexity
  - Initialize delegate in `__init__` directly
  - **DONE**: Refactored to use @property for safer lazy initialization
  - Delegate selected on first access, more explicit and type-safe

- [ ] **#4**: Improve time-only parsing robustness
  - Better heuristics or explicit date detection
  - Document edge cases in docstring

- [x] **#5**: Add duration sanity limits
  - Max duration validation (e.g., 365 days)
  - Prevent unrealistic values like `999999999d`
  - **DONE**: Maximum duration of 365 days enforced with helpful error message

- [ ] **#17**: Document timezone handling
  - Clarify all times are local timezone
  - Note UTC/timezone-aware inputs not supported
  - Document DST behavior

- [ ] **#20**: Handle 'at' queue full scenario
  - Check stderr for queue full errors
  - Provide helpful error message

- [x] **#23**: Sanitize messages in log output
  - Prevent log injection via newlines in messages
  - Truncate or escape message content in logs
  - **DONE**: Removed user-provided content from logs entirely
  - Only log operational metadata (timestamps, backend selection, etc.)

## Long-term (Future Enhancements)

- [x] **#25**: Consider multi-file structure
  - Split into `cli.py`, `backends/`, `parsers.py`, `utils.py`
  - **DECISION**: Not needed at 587 lines with stable feature set
  - Current single-file structure is clear and maintainable
  - Revisit if adding features like config files (#26), plugins, or exceeding ~1000 lines

- [ ] **#26**: Add configuration file support
  - Support `~/.config/remindme/config.toml`
  - Allow setting default backend, title, etc.
  - Optional feature, request-driven

## Completed ✅

- [x] **#10**: Add LICENSE file (MIT)
- [x] **#2**: Fix inconsistent subprocess error handling in AtBackend
- [x] **#16**: Add notify-send availability check
- [x] **#3**: Document DISPLAY environment requirements
- [x] **#6**: Add security comment on shell command building
- [x] **#8**: Add docstrings to utility functions
- [x] **#15**: Fix unit name collision with microseconds
