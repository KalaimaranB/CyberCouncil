# CyberCouncil Test Suite

Comprehensive test coverage for the CyberCouncil application.

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_attack_graph.py -v
```

### Run specific test:
```bash
pytest tests/test_attack_graph.py::TestAttackGraph::test_add_node -v
```

## Test Organization

- `conftest.py` - Pytest configuration and shared fixtures
- `test_attack_graph.py` - Attack graph module tests (20+ tests)
- `test_graph_visualizer.py` - Graph visualization tests (12+ tests)
- `test_discovery_parser.py` - Entity extraction tests (25+ tests)
- `test_router.py` - Query routing tests (15+ tests)
- `test_tools.py` - Utility function tests (15+ tests)

## Test Coverage

Tests cover:
- ✅ Entity extraction (IPs, services, ports, vulnerabilities, credentials)
- ✅ Graph building and relationship inference
- ✅ ASCII visualization and statistics
- ✅ Query routing (strategic vs tactical)
- ✅ Project management and file operations
- ✅ Sanitization and security
- ✅ Edge cases and error handling

## Fixtures

Common fixtures available in all tests:
- `temp_project_dir` - Temporary project directory with active_record.md
- `sample_active_record` - Pre-populated active record for testing
- `mock_config` - Mocked configuration with temporary paths

## Requirements

```bash
pip install pytest pytest-cov
```
