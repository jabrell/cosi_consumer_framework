<img width="1462" height="527" alt="overview_of_model_framework" src="https://github.com/user-attachments/assets/d5df0b31-3afd-45cb-a3fd-3f565c2baac9" /># COSI Consumer Framework

An agent-based modeling framework for consumer behavior simulation, implementing the SWEET COSI Framework in Python.

## Overview

The COSI Consumer Framework provides a structured approach to building agent-based models where:
- **Agents** perceive and act upon their environment
- **Environment** contains assets and maintains world state
- **ConsumerModel** model implementation
- Agents make choices based on perceptions, preferences, and environmental conditions

The architecture of this frame:
<img width="1462" height="527" alt="overview_of_model_framework" src="https://github.com/user-attachments/assets/67e9b6cf-0bd4-46e5-9d51-c6e5623dbc34" />

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for Python package management.

### Install uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install the framework

```bash
# Clone the repository
git clone https://github.com/jabrell/cosi_consumer_framework.git
cd cosi_consumer_framework

# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

## Examples

See the `examples/` directory for complete working examples:

- `0_basic_usage.ipynb` - Basic agent-based model with temperature and drink choices


## Running Tests
Running tests using `uv`.

### Run all tests

```bash
uv run pytest
```

### Run with coverage

```bash
uv run pytest --cov=cosi_consumer_framework --cov-report=html
```

## Examples

See the `illustrations/` directory for complete working examples:

- `0_basic_usage.ipynb` - Basic agent-based model with temperature and drink choices


## Contact

For questions or issues, please open an issue on GitHub.
