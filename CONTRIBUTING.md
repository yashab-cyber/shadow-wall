# 🤝 Contributing to ShadowWall AI

Thank you for your interest in contributing to ShadowWall AI! This document provides guidelines and information for contributing to our cybersecurity platform.

## 🎯 Table of Contents

- [🎯 Getting Started](#-getting-started)
- [🛡️ Code of Conduct](#️-code-of-conduct)
- [🔄 Types of Contributions](#-types-of-contributions)
- [🚀 Development Setup](#-development-setup)
- [📝 Contribution Process](#-contribution-process)
- [🎨 Style Guidelines](#-style-guidelines)
- [🧪 Testing](#-testing)
- [📚 Documentation](#-documentation)
- [🏆 Recognition](#-recognition)

## 🎯 Getting Started

### 🌟 **Ways to Contribute**

We welcome contributions in many forms:

- **🐛 Bug Reports**: Help us identify and fix issues
- **💡 Feature Requests**: Suggest new capabilities
- **🔧 Code Contributions**: Submit pull requests
- **📖 Documentation**: Improve guides and tutorials
- **🧪 Testing**: Add tests and improve coverage
- **🌐 Translations**: Help internationalize the platform
- **🎨 UI/UX**: Enhance user interface and experience
- **🛡️ Security**: Report vulnerabilities and improve security

### 📋 **Before You Start**

1. **Read our [Code of Conduct](CODE_OF_CONDUCT.md)**
2. **Check existing [Issues](https://github.com/yashab-cyber/shadow-wall/issues)**
3. **Review our [Security Policy](SECURITY.md)**
4. **Join our community discussions**

## 🛡️ Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to yashabalam707@gmail.com.

## 🔄 Types of Contributions

### 🐛 **Bug Reports**

When filing an issue, make sure to answer these questions:

#### **Bug Report Template**
```markdown
**Describe the Bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
- OS: [e.g. Ubuntu 20.04, Windows 10, macOS 12.0]
- Python Version: [e.g. 3.8, 3.9, 3.10]
- ShadowWall Version: [e.g. 2.1.0]
- Installation Method: [e.g. pip, docker, source]

**Additional Context**
Add any other context about the problem here.
```

### 💡 **Feature Requests**

#### **Feature Request Template**
```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions.

**Use Cases**
Describe specific use cases for this feature.

**Additional Context**
Add any other context or screenshots about the feature request.
```

### 🔧 **Code Contributions**

#### **Good First Issues**
Look for issues labeled `good first issue` or `help wanted` to get started.

#### **Major Features**
For significant changes, please open an issue first to discuss your proposed changes.

## 🚀 Development Setup

### 📋 **Prerequisites**

- **Python 3.8+**
- **Git**
- **Docker** (optional but recommended)
- **Node.js 16+** (for frontend components)

### 🔧 **Local Development Setup**

#### 1. **Fork and Clone**
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/shadow-wall.git
cd shadow-wall

# Add upstream remote
git remote add upstream https://github.com/yashab-cyber/shadow-wall.git
```

#### 2. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### 3. **Configuration**
```bash
# Copy example configuration
cp config/config.example.yaml config/config.yaml

# Set environment variables
export SHADOWWALL_SECRET_KEY="$(openssl rand -hex 32)"
export SHADOWWALL_DB_PATH="data/shadowwall.db"
```

#### 4. **Database Setup**
```bash
# Initialize database
python -m src.database.connection --init

# Run migrations (if any)
alembic upgrade head
```

#### 5. **Verify Setup**
```bash
# Run tests
pytest

# Start development server
python run_integrated.py
```

### 🐳 **Docker Development**

```bash
# Build development image
docker-compose -f docker-compose.dev.yml build

# Start development environment
docker-compose -f docker-compose.dev.yml up

# Run tests in container
docker-compose -f docker-compose.dev.yml exec app pytest
```

## 📝 Contribution Process

### 🔄 **Workflow**

#### 1. **Create a Branch**
```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

#### 2. **Make Changes**
- Write clean, well-documented code
- Follow our style guidelines
- Add tests for new functionality
- Update documentation as needed

#### 3. **Test Your Changes**
```bash
# Run full test suite
pytest tests/ -v

# Run specific tests
pytest tests/test_your_module.py

# Check code coverage
pytest --cov=src --cov-report=html

# Lint your code
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

#### 4. **Commit Changes**
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new threat detection algorithm

- Implement advanced ML-based threat detection
- Add support for real-time analysis
- Include comprehensive test coverage
- Update documentation

Fixes #123"
```

#### 5. **Push and Create PR**
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Fill out the PR template completely
```

### 🎯 **Pull Request Guidelines**

#### **PR Title Format**
```
type(scope): description

Examples:
feat(ml): add new anomaly detection algorithm
fix(api): resolve authentication timeout issue
docs(readme): update installation instructions
test(core): add unit tests for network monitor
```

#### **PR Description Template**
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information that reviewers should know.
```

## 🎨 Style Guidelines

### 🐍 **Python Code Style**

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

#### **Formatting**
- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Sorted with isort

#### **Code Quality Tools**
```bash
# Auto-formatting
black src/ tests/

# Import sorting
isort src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Security linting
bandit -r src/
```

### 📝 **Documentation Style**

#### **Docstrings**
Use Google-style docstrings:

```python
def detect_threat(network_data: Dict[str, Any]) -> ThreatResult:
    """Detect potential threats in network data.
    
    Args:
        network_data: Dictionary containing network packet information
            with keys 'src_ip', 'dst_ip', 'protocol', 'payload'.
    
    Returns:
        ThreatResult object containing threat level, confidence score,
        and detailed analysis.
    
    Raises:
        ValueError: If network_data is missing required keys.
        NetworkError: If unable to process network data.
    
    Example:
        >>> data = {'src_ip': '192.168.1.1', 'dst_ip': '10.0.0.1'}
        >>> result = detect_threat(data)
        >>> print(result.threat_level)
        'HIGH'
    """
```

### 🎯 **Commit Message Guidelines**

#### **Format**
```
type(scope): subject

body (optional)

footer (optional)
```

#### **Types**
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### **Examples**
```bash
feat(ml): implement LSTM-based threat prediction

fix(api): resolve rate limiting bypass vulnerability

docs(security): update vulnerability reporting process

test(network): add integration tests for packet capture
```

## 🧪 Testing

### 📊 **Test Coverage**

We maintain high test coverage standards:
- **Minimum**: 80% overall coverage
- **New Code**: 90% coverage required
- **Critical Components**: 95% coverage

### 🔬 **Test Types**

#### **Unit Tests**
```bash
# Run unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=term-missing
```

#### **Integration Tests**
```bash
# Run integration tests
pytest tests/integration/ -v

# Run with Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

#### **Security Tests**
```bash
# Run security tests
pytest tests/security/ -v

# Static security analysis
bandit -r src/

# Dependency vulnerability check
safety check
```

### 🎯 **Writing Tests**

#### **Test Structure**
```python
import pytest
from unittest.mock import Mock, patch

class TestThreatDetector:
    """Test suite for ThreatDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ThreatDetector()
    
    def test_detect_threat_with_valid_data(self):
        """Test threat detection with valid network data."""
        # Given
        network_data = {
            'src_ip': '192.168.1.100',
            'dst_ip': '10.0.0.1',
            'protocol': 'TCP',
            'payload_size': 1024
        }
        
        # When
        result = self.detector.detect_threat(network_data)
        
        # Then
        assert result.threat_level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert 0.0 <= result.confidence <= 1.0
        assert result.analysis is not None
    
    @pytest.mark.parametrize("invalid_data", [
        {},
        {'src_ip': '192.168.1.1'},
        {'invalid_key': 'value'}
    ])
    def test_detect_threat_with_invalid_data(self, invalid_data):
        """Test threat detection with invalid data raises ValueError."""
        with pytest.raises(ValueError):
            self.detector.detect_threat(invalid_data)
```

## 📚 Documentation

### 📖 **Documentation Types**

#### **Code Documentation**
- Inline comments for complex logic
- Comprehensive docstrings
- Type hints for all functions
- API documentation

#### **User Documentation**
- Installation guides
- Configuration instructions
- API reference
- Tutorials and examples

#### **Developer Documentation**
- Architecture documentation
- Contribution guidelines
- Development setup
- Deployment guides

### ✍️ **Writing Guidelines**

- **Clear and Concise**: Use simple, direct language
- **Examples**: Include practical examples
- **Updates**: Keep documentation current with code changes
- **Structure**: Use consistent formatting and structure

## 🏆 Recognition

### 🌟 **Contributors**

All contributors are recognized in:
- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Major contributions highlighted
- **Social Media**: Contributor spotlights
- **Website**: Contributors page

### 🎯 **Contribution Levels**

#### **🥉 Bronze Contributor**
- First merged PR
- Listed in contributors
- Special Discord role

#### **🥈 Silver Contributor**
- 5+ merged PRs
- Significant feature contribution
- Community recognition

#### **🥇 Gold Contributor**
- 20+ merged PRs
- Major feature development
- Mentoring other contributors

#### **💎 Diamond Contributor**
- Long-term project maintainer
- Leadership in project direction
- Significant impact on project success

### 🎁 **Contributor Benefits**

- **Swag**: Stickers, t-shirts for active contributors
- **Early Access**: Beta features and releases
- **Networking**: Connect with cybersecurity professionals
- **Learning**: Gain experience in open-source development
- **Recognition**: Portfolio and resume enhancement

## 📞 Getting Help

### 💬 **Communication Channels**

- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Email**: yashabalam707@gmail.com
- **Discord**: Join our community server
- **Social Media**: Follow @_zehrasec

### 🆘 **Need Help?**

Don't hesitate to ask for help! We're here to support you:
- **New to Open Source?**: Check out [First Contributions](https://github.com/firstcontributions/first-contributions)
- **Git Help**: [Pro Git Book](https://git-scm.com/book)
- **Python Help**: [Python Documentation](https://docs.python.org/)
- **Cybersecurity**: [OWASP Resources](https://owasp.org/)

---

<div align="center">

**🤝 Thank You for Contributing! 🤝**

*Together, we're building the future of cybersecurity*

**Questions?** Reach out to yashabalam707@gmail.com

</div>
