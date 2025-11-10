"""
🔧 NOVAQUOTE Logging System Integration Tool
Quick integration script to update existing agents with expert logging
Automatically converts print() statements to structured logging
Built by Moon Dev - System Integration Specialist
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import time


class LoggingIntegrationTool:
    """
    Tool to integrate NOVAQUOTE expert logging into existing Python files
    Features: Automatic conversion, backup creation, logging pattern detection
    """

    def __init__(self, project_root: str = "src"):
        self.project_root = Path(project_root)
        self.backup_dir = Path("backups_logging_integration")
        self.backup_dir.mkdir(exist_ok=True)

        self.print_patterns = [
            r'print\s*\(\s*[^)]+\)',  # print() statements
            r'cprint\s*\(\s*[^)]+\)',  # cprint() statements (termcolor)
            r'logging\.getLogger\s*\(\s*[^)]+\)',  # Basic logging setup
        ]

        self.logging_imports = [
            "from src.logger import get_logger, log_trade, log_risk, log_agent",
            "from src.agents.base_agent import BaseAgent"
        ]

        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "print_statements_converted": 0,
            "logging_imports_added": 0,
            "errors": 0
        }

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []

        for pattern in ["**/*.py"]:
            python_files.extend(self.project_root.rglob(pattern))

        exclude_patterns = [
            "__pycache__",
            ".pytest_cache",
            "venv",
            "env",
            "node_modules",
            ".git"
        ]

        filtered_files = []
        for file_path in python_files:
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                filtered_files.append(file_path)

        return sorted(filtered_files)

    def backup_file(self, file_path: Path) -> Path:
        """Create a backup of the original file"""
        relative_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        import shutil
        shutil.copy2(file_path, backup_path)

        return backup_path

    def contains_print_statements(self, file_path: Path) -> bool:
        """Check if file contains print statements that should be converted"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern in self.print_patterns[:2]:  # Only print and cprint
                if re.search(pattern, content):
                    return True

            return False

        except Exception as e:
            print(f"Error checking {file_path}: {e}")
            return False

    def convert_print_statements(self, content: str, class_name: str = None) -> Tuple[str, int]:
        """Convert print statements to logging calls"""
        conversions = 0
        new_content = content

        logger_name = class_name if class_name else "agent"

        print_pattern = r'print\s*\(\s*([^)]+)\s*\)'

        def replace_print(match):
            nonlocal conversions
            conversions += 1
            print_arg = match.group(1).strip()

            if print_arg.startswith('f"') or print_arg.startswith("f'"):
                return f'self.logger.info({print_arg})'
            elif print_arg.startswith('"') or print_arg.startswith("'"):
                return f'self.logger.info({print_arg})'
            else:
                return f'self.logger.info(str({print_arg}))'

        new_content = re.sub(print_pattern, replace_print, new_content)

        cprint_pattern = r'cprint\s*\(\s*([^,]+),\s*([^)]+)\s*\)'

        def replace_cprint(match):
            nonlocal conversions
            conversions += 1
            message = match.group(1).strip()
            color = match.group(2).strip()

            color_map = {
                '"red"': 'self.logger.error',
                '"green"': 'self.logger.success',
                '"yellow"': 'self.logger.warning',
                '"blue"': 'self.logger.info',
                '"cyan"': 'self.logger.info',
                '"magenta"': 'self.logger.info'
            }

            logger_method = color_map.get(color, 'self.logger.info')
            return f'{logger_method}({message})'

        new_content = re.sub(cprint_pattern, replace_cprint, new_content)

        return new_content, conversions

    def add_logging_imports(self, content: str) -> Tuple[str, bool]:
        """Add necessary logging imports if not present"""
        new_content = content
        imports_added = False

        if "from src.logger import" in content or "from src.agents.base_agent import BaseAgent" in content:
            return new_content, False

        lines = content.split('\n')
        import_end_index = 0

        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')) and not line.strip().startswith('#'):
                import_end_index = i + 1
            elif line.strip() and not line.strip().startswith(('import ', 'from ', '#')):
                break

        if import_end_index > 0:
            lines.insert(import_end_index, "")
            lines.insert(import_end_index + 1, "# NOVAQUOTE Expert Logging System")
            lines.insert(import_end_index + 2, "from src.logger import get_logger, log_trade, log_risk, log_agent")
            lines.insert(import_end_index + 3, "from src.agents.base_agent import BaseAgent")
            imports_added = True

        return '\n'.join(lines), imports_added

    def update_agent_inheritance(self, content: str) -> Tuple[str, bool]:
        """Update agent classes to inherit from BaseAgent"""
        new_content = content
        inheritance_updated = False

        class_pattern = r'class\s+(\w+Agent)\s*\([^)]*\)\s*:'

        def replace_inheritance(match):
            nonlocal inheritance_updated
            class_name = match.group(1)
            inheritance_updated = True
            return f'class {class_name}(BaseAgent):'

        new_content = re.sub(class_pattern, replace_inheritance, new_content)

        return new_content, inheritance_updated

    def add_logger_initialization(self, content: str, class_name: str) -> Tuple[str, bool]:
        """Add logger initialization to __init__ methods"""
        new_content = content
        logger_added = False

        init_pattern = r'def\s+__init__\s*\([^)]*\)\s*:'

        def add_logger_to_init(match):
            nonlocal logger_added
            logger_added = True

            init_start = match.end()
            lines = new_content[:init_start].split('\n')
            after_init = new_content[init_start:].split('\n')

            parent_call_index = -1
            for i, line in enumerate(after_init):
                if line.strip().startswith(('super().__init__', 'BaseAgent.__init__')):
                    parent_call_index = i
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    break

            if parent_call_index >= 0:
                after_init.insert(parent_call_index + 1, "")
                after_init.insert(parent_call_index + 2, "        # Initialize NOVAQUOTE expert logger")
                after_init.insert(parent_call_index + 3, f"        self.logger = get_logger(\"agent.{class_name.lower()}\")")
                after_init.insert(parent_call_index + 4, "")
            else:
                after_init.insert(0, "")
                after_init.insert(1, "        # Initialize NOVAQUOTE expert logger")
                after_init.insert(2, f"        self.logger = get_logger(\"agent.{class_name.lower()}\")")
                after_init.insert(3, "")

            return new_content[:init_start] + '\n'.join(after_init)

        if re.search(init_pattern, new_content):
            new_content = add_logger_to_init(re.search(init_pattern, new_content))

        return new_content, logger_added

    def process_file(self, file_path: Path) -> Dict:
        """Process a single file and integrate logging"""
        result = {
            "file": str(file_path),
            "backup_created": False,
            "imports_added": False,
            "print_statements_converted": 0,
            "inheritance_updated": False,
            "logger_added": False,
            "modified": False,
            "error": None
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            if not self.contains_print_statements(file_path) and "BaseAgent" not in original_content:
                return result

            backup_path = self.backup_file(file_path)
            result["backup_created"] = True

            new_content = original_content
            modifications = []

            new_content, imports_added = self.add_logging_imports(new_content)
            if imports_added:
                result["imports_added"] = True
                modifications.append("Added logging imports")

            new_content, inheritance_updated = self.update_agent_inheritance(new_content)
            if inheritance_updated:
                result["inheritance_updated"] = True
                modifications.append("Updated BaseAgent inheritance")

            class_pattern = r'class\s+(\w+Agent)\s*\([^)]*\)\s*:'
            classes = re.findall(class_pattern, new_content)

            for class_name in classes:
                new_content, logger_added = self.add_logger_initialization(new_content, class_name)
                if logger_added:
                    result["logger_added"] = True
                    modifications.append(f"Added logger to {class_name}")

            main_class = classes[0] if classes else None
            new_content, print_conversions = self.convert_print_statements(new_content, main_class)
            result["print_statements_converted"] = print_conversions
            if print_conversions > 0:
                modifications.append(f"Converted {print_conversions} print statements")

            if new_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                result["modified"] = True
                result["modifications"] = modifications

        except Exception as e:
            result["error"] = str(e)
            self.stats["errors"] += 1

        return result

    def process_directory(self):
        """Process all Python files in the project directory"""
        python_files = self.find_python_files()

        print(f"🔧 NOVAQUOTE Logging System Integration")
        print("=" * 60)
        print(f"📁 Scanning directory: {self.project_root}")
        print(f"📄 Found {len(python_files)} Python files")
        print(f"💾 Backups will be saved to: {self.backup_dir}")
        print("=" * 60)

        if not python_files:
            print("❌ No Python files found!")
            return

        target_files = []
        for file_path in python_files:
            if "agent" in file_path.name.lower() or self.contains_print_statements(file_path):
                target_files.append(file_path)

        print(f"🎯 Target files for integration: {len(target_files)}")
        print()

        if not target_files:
            print("✅ No files need integration!")
            return

        results = []
        for i, file_path in enumerate(target_files, 1):
            print(f"📄 [{i}/{len(target_files)}] Processing: {file_path.name}")

            result = self.process_file(file_path)
            results.append(result)

            self.stats["files_processed"] += 1

            if result["error"]:
                print(f"   ❌ Error: {result['error']}")
                continue

            if result["modified"]:
                self.stats["files_modified"] += 1
                self.stats["print_statements_converted"] += result["print_statements_converted"]
                if result["imports_added"]:
                    self.stats["logging_imports_added"] += 1

                print(f"   ✅ Modified successfully!")
                if "modifications" in result:
                    for mod in result["modifications"]:
                        print(f"      • {mod}")
            else:
                print(f"   ℹ️  No modifications needed")

        print("\n" + "=" * 60)
        print("📊 INTEGRATION SUMMARY")
        print("=" * 60)
        print(f"📄 Files processed: {self.stats['files_processed']}")
        print(f"🔧 Files modified: {self.stats['files_modified']}")
        print(f"📝 Print statements converted: {self.stats['print_statements_converted']}")
        print(f"📥 Logging imports added: {self.stats['logging_imports_added']}")
        print(f"❌ Errors: {self.stats['errors']}")

        if self.stats["files_modified"] > 0:
            print(f"\n💾 All original files backed up to: {self.backup_dir}")
            print("\n🎉 Integration completed successfully!")
            print("\n📝 Next steps:")
            print("   1. Test the modified agents")
            print("   2. Run: python demo_logging_system.py")
            print("   3. Start the log centralizer: python src/logging/log_centralizer.py --dashboard")
        else:
            print("\n✅ All files already using expert logging!")

    def create_integration_report(self):
        """Create a detailed integration report"""
        report_path = "logging_integration_report.md"

        report_content = f"""# NOVAQUOTE Logging System Integration Report

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

- Files processed: {self.stats['files_processed']}
- Files modified: {self.stats['files_modified']}
- Print statements converted: {self.stats['print_statements_converted']}
- Logging imports added: {self.stats['logging_imports_added']}
- Errors encountered: {self.stats['errors']}

The NOVAQUOTE expert logging system has been successfully integrated into your trading agents.

- **Structured JSON logging**: All logs now in structured format
- **Trade tracking**: Complete transaction monitoring
- **Risk management logging**: Real-time risk alerts
- **Performance metrics**: Detailed operation tracking
- **Agent lifecycle**: Full agent state monitoring

1. **Test your agents**: Run your modified agents to ensure they work correctly
2. **Monitor logs**: Check the `logs/` directory for structured log files
3. **Start centralizer**: Run `python src/logging/log_centralizer.py --dashboard`
4. **Customize logging**: Add more detailed logging to specific operations

- Main logs: `logs/novaquote.log`
- Trade logs: `logs/trades/`
- Agent logs: `logs/agents/`
- Risk logs: `logs/risk/`
- Error logs: `logs/errors/`
- Performance logs: `logs/performance/`


```python
self.logger.success("Trade executed", {"symbol": "BTC", "size": 1.5})

self.logger.risk_alert("HIGH_RISK", "HIGH", {"symbol": "ETH", "position_size": 5000})

log_trade("BUY", "BTC", {"size": 1.0, "price": 45000, "value_usd": 45000})

log_agent("START", "StrategyAgent", {"config": {...}})
```

For issues or questions, refer to the NOVAQUOTE documentation or check the log files for detailed error information.
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n📄 Integration report created: {report_path}")


def main():
    """Main function"""
    print("🔧 NOVAQUOTE LOGGING SYSTEM INTEGRATION TOOL")
    print("=" * 60)
    print("This tool will automatically integrate expert logging into your agents")
    print("⚠️  Make sure your code is committed to version control first!")
    print()

    response = input("Continue with integration? (y/N): ").strip().lower()
    if response != 'y':
        print("Integration cancelled.")
        return

    tool = LoggingIntegrationTool()
    tool.process_directory()

    if tool.stats["files_modified"] > 0:
        tool.create_integration_report()

    print("\n🎉 Integration tool completed!")


if __name__ == "__main__":
    main()