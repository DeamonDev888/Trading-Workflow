#!/usr/bin/env python3
"""
[OK] NOVAQUOTE Documentation Manager
Built with love by Deamon Dev [ROCKET]

Script d'analyse, organisation et validation de la documentation du projet NOVAQUOTE.
Surveille la racine, organise @docs, valide la documentation existante.
"""

import os
import re
// import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
import hashlib

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
ROOT_DIR = PROJECT_ROOT

# Fichiers de documentation critiques à surveiller
CRITICAL_DOCS = [
    "docs/HYPERLIQUID_API_DOCUMENTATION.md",
    "docs/COMMANDS_AGENTS.md",
    "docs/COMMANDS_AGENTS_GUIDE.md",
    "docs/AGENTS_ARCHITECTURE_DIAGRAM.md",
    "docs/other/README.md",
    "docs/other/PROMPT_SYSTEME_NOVAQUOTE.md"
]

# Fichiers à laisser à la racine (ne pas déplacer)
ROOT_FILES = [
    "README.md",
    "PROMPT_SYSTEME_NOVAQUOTE.md"
]

# Patterns de documentation à détecter
DOC_PATTERNS = [
    r'\.md$',           # Markdown files
    r'\.txt$',          # Text files
    r'\.rst$',          # reStructuredText
    r'DOCUMENTATION',   # Files with DOCUMENTATION in name
    r'GUIDE',           # Guide files
    r'README',          # README files
    r'CHANGELOG',       # Changelog files
    r'CONTRIBUTING',    # Contributing files
]

class DocumentationManager:
    """Gestionnaire de documentation NOVAQUOTE"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.docs_dir = DOCS_DIR
        self.root_dir = ROOT_DIR
        self.critical_docs = [PROJECT_ROOT / f for f in CRITICAL_DOCS]

        # Créer répertoire docs s'il n'existe pas
        self.docs_dir.mkdir(exist_ok=True)

        print("📚 Documentation Manager initialized")
        print(f"📁 Project root: {self.project_root}")
        print(f"📖 Docs directory: {self.docs_dir}")

    def scan_root_for_docs(self) -> Dict[str, List[Path]]:
        """Scanner la racine pour trouver tous les fichiers de documentation"""
        print("\n🔍 Scanning root directory for documentation...")

        found_docs = {
            "markdown": [],
            "text": [],
            "other": [],
            "critical": []
        }

        # Scanner tous les fichiers à la racine (non récursif)
        for item in self.root_dir.iterdir():
            if item.is_file():
                file_path = item
                file_name = file_path.name

                # Vérifier si c'est un fichier de documentation (mais pas les fichiers root réservés)
                is_doc = False
                for pattern in DOC_PATTERNS:
                    if re.search(pattern, file_name, re.IGNORECASE):
                        is_doc = True
                        break

                # Ne pas traiter les fichiers root réservés (ils sont déjà dans docs/other/)
                if file_name in ROOT_FILES:
                    continue

                if is_doc:
                    if file_path.suffix.lower() == '.md':
                        found_docs["markdown"].append(file_path)
                    elif file_path.suffix.lower() in ['.txt', '.rst']:
                        found_docs["text"].append(file_path)
                    else:
                        found_docs["other"].append(file_path)

                    # Vérifier si c'est un fichier critique
                    if file_path in self.critical_docs:
                        found_docs["critical"].append(file_path)

        print(f"📄 Found {len(found_docs['markdown'])} markdown files")
        print(f"📝 Found {len(found_docs['text'])} text files")
        print(f"📚 Found {len(found_docs['other'])} other documentation files")
        print(f"⭐ Found {len(found_docs['critical'])} critical documentation files")

        return found_docs

    def organize_docs_in_docs_dir(self, found_docs: Dict[str, List[Path]]) -> Dict[str, List[str]]:
        """Organiser la documentation dans le répertoire @docs"""
        print("\n📦 Organizing documentation in @docs directory...")

        organized = {
            "moved": [],
            "already_in_docs": [],
            "errors": []
        }

        # Créer sous-répertoires
        subdirs = {
            "api": self.docs_dir / "api",
            "agents": self.docs_dir / "agents",
            "guides": self.docs_dir / "guides",
            "architecture": self.docs_dir / "architecture",
            "other": self.docs_dir / "other"
        }

        for subdir in subdirs.values():
            subdir.mkdir(exist_ok=True)

        # Organiser chaque fichier trouvé
        for category, files in found_docs.items():
            if category == "critical":
                continue  # Les fichiers critiques sont déjà dans docs/

            for file_path in files:
                try:
                    file_name = file_path.name

                    # Vérifier si c'est un fichier à laisser à la racine
                    if file_name in ROOT_FILES:
                        print(f"📌 Keeping {file_name} at root (as requested)")
                        continue

                    # Déterminer le sous-répertoire approprié
                    target_subdir = self.docs_dir / "other"  # Default

                    if "api" in file_name.lower() or "hyperliquid" in file_name.lower():
                        target_subdir = subdirs["api"]
                    elif "agent" in file_name.lower():
                        target_subdir = subdirs["agents"]
                    elif "guide" in file_name.lower() or "command" in file_name.lower():
                        target_subdir = subdirs["guides"]
                    elif "architecture" in file_name.lower() or "diagram" in file_name.lower():
                        target_subdir = subdirs["architecture"]

                    target_path = target_subdir / file_name

                    # Vérifier si le fichier est déjà dans docs/
                    if str(file_path).startswith(str(self.docs_dir)):
                        organized["already_in_docs"].append(str(file_path))
                        continue

                    # Déplacer le fichier
                    shutil.move(str(file_path), str(target_path))
                    organized["moved"].append(f"{file_path} → {target_path}")

                    print(f"✅ Moved: {file_name} → {target_subdir.name}/")

                except Exception as e:
                    error_msg = f"❌ Error moving {file_path}: {str(e)}"
                    organized["errors"].append(error_msg)
                    print(error_msg)

        return organized

    def validate_critical_docs(self) -> Dict[str, Dict]:
        """Valider que tous les fichiers de documentation critiques existent et sont à jour"""
        print("\n🔍 Validating critical documentation files...")

        validation_results = {}

        for critical_doc in self.critical_docs:
            doc_info = {
                "exists": critical_doc.exists(),
                "size": 0,
                "last_modified": None,
                "is_recent": False,
                "checksum": None,
                "status": "unknown"
            }

            if critical_doc.exists():
                stat = critical_doc.stat()
                doc_info["size"] = stat.st_size
                doc_info["last_modified"] = datetime.fromtimestamp(stat.st_mtime)

                # Vérifier si le fichier a été modifié récemment (7 jours)
                days_since_modified = (datetime.now() - doc_info["last_modified"]).days
                doc_info["is_recent"] = days_since_modified <= 7

                # Calculer checksum pour détecter les changements
                with open(critical_doc, 'rb') as f:
                    doc_info["checksum"] = hashlib.md5(f.read()).hexdigest()

                # Évaluer le statut
                if doc_info["size"] > 1000:  # Au moins 1KB
                    if doc_info["is_recent"]:
                        doc_info["status"] = "current"
                    else:
                        doc_info["status"] = "needs_review"
                else:
                    doc_info["status"] = "incomplete"

            else:
                doc_info["status"] = "missing"

            validation_results[str(critical_doc.relative_to(self.project_root))] = doc_info

            # Afficher le statut
            status_icon = {
                "current": "✅",
                "needs_review": "⚠️",
                "incomplete": "❌",
                "missing": "🚫",
                "unknown": "❓"
            }.get(doc_info["status"], "❓")

            print(f"{status_icon} {critical_doc.name}: {doc_info['status']}")

        return validation_results

    def analyze_docs_content(self) -> Dict[str, Dict]:
        """Analyser le contenu des fichiers de documentation critiques"""
        print("\n📖 Analyzing documentation content...")

        content_analysis = {}

        for critical_doc in self.critical_docs:
            if not critical_doc.exists():
                continue

            analysis = {
                "word_count": 0,
                "line_count": 0,
                "has_code_blocks": False,
                "has_tables": False,
                "has_links": False,
                "sections": [],
                "completeness_score": 0
            }

            try:
                with open(critical_doc, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Analyses basiques
                analysis["word_count"] = len(content.split())
                analysis["line_count"] = len(content.split('\n'))

                # Détecter les éléments Markdown
                analysis["has_code_blocks"] = "```" in content
                analysis["has_tables"] = "|" in content and "---" in content
                analysis["has_links"] = "[" in content and "](" in content

                # Extraire les sections (headers Markdown)
                sections = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
                analysis["sections"] = sections

                # Calculer un score de complétude
                score = 0
                if analysis["word_count"] > 100: score += 1
                if analysis["has_code_blocks"]: score += 1
                if analysis["has_tables"]: score += 1
                if analysis["has_links"]: score += 1
                if len(analysis["sections"]) > 3: score += 1
                if analysis["line_count"] > 50: score += 1

                analysis["completeness_score"] = min(score, 5)  # Max 5 points

            except Exception as e:
                analysis["error"] = str(e)

            content_analysis[str(critical_doc.relative_to(self.project_root))] = analysis

            # Afficher le résumé
            completeness_icons = "⭐" * analysis["completeness_score"]
            print(f"📊 {critical_doc.name}: {analysis['word_count']} words, {len(analysis['sections'])} sections {completeness_icons}")

        return content_analysis

    def maintain_readme(self) -> Dict[str, str]:
        """Maintenir le README.md à jour en tant qu'expert documentation"""
        print("\n📝 Maintaining README.md as documentation expert...")

        readme_path = self.project_root / "docs" / "other" / "README.md"
        maintenance_results = {
            "readme_path": str(readme_path),
            "actions_taken": [],
            "recommendations": [],
            "status": "unknown"
        }

        if not readme_path.exists():
            maintenance_results["status"] = "missing"
            maintenance_results["recommendations"].append("Create README.md file")
            print("❌ README.md not found")
        return maintenance_results

    def self_improve_agent(self) -> Dict[str, str]:
        """Auto-amélioration de l'agent documentation - analyse et améliore son propre prompt et script"""
        print("\n🤖 Self-improving Agent Documentation...")

        improvement_results = {
            "agent_file": ".claude/agents/agent-documentation.md",
            "script_file": "scripts/documentation_manager.py",
            "analysis": {},
            "improvements_made": [],
            "status": "unknown"
        }

        try:
            # 1. Analyser le prompt de l'agent
            agent_file_path = self.project_root / ".claude" / "agents" / "agent-documentation.md"
            script_file_path = self.project_root / "scripts" / "documentation_manager.py"

            if not agent_file_path.exists():
                improvement_results["status"] = "agent_file_missing"
                print("❌ Agent file not found")
                return improvement_results

            if not script_file_path.exists():
                improvement_results["status"] = "script_file_missing"
                print("❌ Script file not found")
                return improvement_results

            # Lire les fichiers actuels
            with open(agent_file_path, 'r', encoding='utf-8') as f:
                agent_content = f.read()

            with open(script_file_path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            original_agent_content = agent_content
            original_script_content = script_content
            improvements = []

            # 2. Analyser et améliorer le prompt de l'agent
            agent_improvements = self._analyze_and_improve_agent_prompt(agent_content)
            if agent_improvements["modifications"]:
                agent_content = agent_improvements["new_content"]
                improvements.extend([f"Agent prompt: {imp}" for imp in agent_improvements["modifications"]])

            # 3. Analyser et améliorer le script
            script_improvements = self._analyze_and_improve_script(script_content)
            if script_improvements["modifications"]:
                script_content = script_improvements["new_content"]
                improvements.extend([f"Script: {imp}" for imp in script_improvements["modifications"]])

            # 4. Sauvegarder les améliorations si nécessaire
            if agent_content != original_agent_content:
                with open(agent_file_path, 'w', encoding='utf-8') as f:
                    f.write(agent_content)
                print("✅ Agent prompt improved and saved")

            if script_content != original_script_content:
                with open(script_file_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                print("✅ Script improved and saved")

            # 5. Résultats
            improvement_results["analysis"] = {
                "agent_improvements": agent_improvements,
                "script_improvements": script_improvements
            }
            improvement_results["improvements_made"] = improvements
            improvement_results["status"] = "improved" if improvements else "no_improvements_needed"

            if improvements:
                print(f"🎯 Made {len(improvements)} self-improvements")
                for imp in improvements:
                    print(f"   • {imp}")
            else:
                print("✅ No improvements needed - agent is optimal")

        except Exception as e:
            improvement_results["status"] = "error"
            improvement_results["error"] = str(e)
            print(f"❌ Error during self-improvement: {e}")

        return improvement_results

    def _analyze_and_improve_agent_prompt(self, content: str) -> Dict[str, any]:
        """Analyser et améliorer le prompt de l'agent documentation"""
        modifications = []
        new_content = content

        # 1. Vérifier et améliorer la description
        if "Expert Documentation & Content Manager" not in content:
            # Mettre à jour la description pour inclure l'auto-amélioration
            desc_pattern = r'description: .*'
            new_desc = 'description: Expert Documentation & Content Manager with Self-Improvement Capabilities'
            new_content = re.sub(desc_pattern, f'description: {new_desc}', new_content)
            modifications.append("Updated agent description to include self-improvement")

        # 2. Ajouter une section auto-amélioration si elle n'existe pas
        if "Auto-Amélioration" not in content and "Self-Improvement" not in content:
            # Trouver un bon endroit pour insérer
            responsibilities_match = re.search(r'## Responsabilités', content, re.IGNORECASE)
            if responsibilities_match:
                insert_pos = responsibilities_match.end()

                self_improvement_section = """

### 7. **Auto-Amélioration Continue**
- Analyser ses propres performances et efficacité
- Identifier les axes d'amélioration du prompt et du script
- Modifier automatiquement son propre code et configuration
- S'adapter aux nouveaux besoins de documentation
- Optimiser ses patterns de détection et organisation"""

                new_content = new_content[:insert_pos] + self_improvement_section + content[insert_pos:]
                modifications.append("Added self-improvement responsibility section")

        # 3. Améliorer les exemples d'usage
        if not re.search(r'@agent-documentation.*improve|@agent-documentation.*self', content, re.IGNORECASE):
            examples_match = re.search(r'## Exemples d\'Usage', content, re.IGNORECASE)
            if examples_match:
                insert_pos = examples_match.end()

                self_improve_examples = """

### Auto-Amélioration
```bash
@agent-documentation Self-improve agent
# → Analyse ses propres performances
# → Identifie les améliorations possibles
# → Modifie automatiquement son prompt et script
# → S'optimise pour de meilleures performances
```"""

                new_content = new_content[:insert_pos] + self_improve_examples + content[insert_pos:]
                modifications.append("Added self-improvement usage examples")

        # 4. Ajouter des commandements sur l'auto-amélioration
        commandments_match = re.search(r'## Commandements Directs', content, re.IGNORECASE)
        if commandments_match:
            insert_pos = commandments_match.end()

            self_improve_commandments = """
8. **S'AMÉLIORER** continuellement en analysant ses performances
9. **MODIFIER** son propre prompt et script quand nécessaire
10. **S'ADAPTER** aux nouveaux patterns de documentation découverts"""

            new_content = new_content[:insert_pos] + self_improve_commandments + content[insert_pos:]
            modifications.append("Added self-improvement commandments")

        return {
            "modifications": modifications,
            "new_content": new_content
        }

    def _analyze_and_improve_script(self, content: str) -> Dict[str, any]:
        """Analyser et améliorer le script documentation_manager.py"""
        modifications = []
        new_content = content

        # 1. Vérifier la présence de la méthode self_improve_agent
        if "def self_improve_agent(self)" not in content:
            # Ajouter la méthode d'auto-amélioration
            maintain_readme_match = re.search(r'    def maintain_readme\(self\)', content)
            if maintain_readme_match:
                # Trouver la fin de la méthode maintain_readme
                method_end = maintain_readme_match.end()
                next_method_match = re.search(r'\n    def \w+', content[method_end:])
                if next_method_match:
                    insert_pos = method_end + next_method_match.start()

                    self_improve_method = """
    def self_improve_agent(self) -> Dict[str, str]:
        \"\"\"Auto-amélioration de l'agent documentation - analyse et améliore son propre prompt et script\"\"\"
        print("\\n🤖 Self-improving Agent Documentation...")

        improvement_results = {
            "agent_file": ".claude/agents/agent-documentation.md",
            "script_file": "scripts/documentation_manager.py",
            "analysis": {},
            "improvements_made": [],
            "status": "unknown"
        }

        try:
            # Analyser et améliorer le prompt et le script
            agent_file_path = self.project_root / ".claude" / "agents" / "agent-documentation.md"
            script_file_path = self.project_root / "scripts" / "documentation_manager.py"

            if agent_file_path.exists() and script_file_path.exists():
                with open(agent_file_path, 'r', encoding='utf-8') as f:
                    agent_content = f.read()

                # Améliorer le prompt de l'agent
                improved_agent = self._improve_agent_prompt_content(agent_content)
                if improved_agent["modified"]:
                    with open(agent_file_path, 'w', encoding='utf-8') as f:
                        f.write(improved_agent["content"])
                    improvement_results["improvements_made"].append(f"Enhanced agent prompt: {improved_agent['changes']}")

                improvement_results["status"] = "improved" if improvement_results["improvements_made"] else "optimal"

            print(f"🎯 Self-improvement completed: {len(improvement_results['improvements_made'])} enhancements")

        except Exception as e:
            improvement_results["status"] = "error"
            improvement_results["error"] = str(e)
            print(f"❌ Self-improvement error: {e}")

        return improvement_results

    def _improve_agent_prompt_content(self, content: str) -> Dict[str, any]:
        \"\"\"Améliorer le contenu du prompt de l'agent\"\"\"
        modified = False
        changes = []

        # Ajouter des capacités d'auto-amélioration si manquantes
        if "auto-amélioration" not in content.lower() and "self-improvement" not in content.lower():
            # Ajouter une note sur l'auto-amélioration
            content += "\\n\\n**🎯 CAPACITÉ SPÉCIALE**: Cet agent peut s'auto-améliorer en analysant et modifiant son propre prompt et script."
            modified = True
            changes.append("Added self-improvement capability note")

        return {
            "modified": modified,
            "changes": ", ".join(changes),
            "content": content
        }
"""

                    new_content = new_content[:insert_pos] + self_improve_method + content[insert_pos:]
                    modifications.append("Added self_improve_agent method to script")

        # 2. Ajouter l'appel à self_improve_agent dans run_full_analysis
        if "readme_maintenance = self.maintain_readme()" in content and "self_improve_agent" not in content:
            # Ajouter l'auto-amélioration après la maintenance du README
            readme_match = re.search(r'        # 4\.5\. Maintenir le README\.md', content)
            if readme_match:
                insert_pos = readme_match.end()
                next_step_match = re.search(r'        # 5\.', content[insert_pos:])
                if next_step_match:
                    step_insert_pos = insert_pos + next_step_match.start()

                    self_improve_step = """
        # 4.6. Auto-amélioration de l'agent
        agent_improvement = self.self_improve_agent()

"""

                    new_content = new_content[:step_insert_pos] + self_improve_step + content[step_insert_pos:]
                    modifications.append("Added self-improvement step to analysis workflow")

        # 3. Vérifier les imports nécessaires
        if "import hashlib" not in content:
            import_match = re.search(r'import hashlib', content)
            if not import_match:
                imports_section = re.search(r'import \w+', content)
                if imports_section:
                    # Ajouter hashlib import
                    new_content = new_content.replace("import hashlib", "import hashlib", 1)
                    if "import hashlib" not in new_content:
                        new_content = "import hashlib\n" + new_content
                        modifications.append("Added hashlib import for self-improvement")

        return {
            "modifications": modifications,
            "new_content": new_content
        }

    def generate_docs_report(self, scan_results: Dict, organization_results: Dict,
                           validation_results: Dict, content_analysis: Dict) -> str:
        """Générer un rapport complet de l'état de la documentation"""
        print("\n📋 Generating documentation report...")

        report = f"""# 📚 NOVAQUOTE Documentation Status Report
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔍 Documentation Scan Results

### Files Found in Root Directory
- **Markdown files:** {len(scan_results.get('markdown', []))}
- **Text files:** {len(scan_results.get('text', []))}
- **Other documentation:** {len(scan_results.get('other', []))}
- **Critical files:** {len(scan_results.get('critical', []))}

### Organization Actions
- **Files moved to @docs:** {len(organization_results.get('moved', []))}
- **Files already in docs:** {len(organization_results.get('already_in_docs', []))}
- **Errors during organization:** {len(organization_results.get('errors', []))}

## ✅ Critical Documentation Validation

"""

        # Ajouter les détails de validation
        for doc_path, info in validation_results.items():
            status_icon = {
                "current": "✅",
                "needs_review": "⚠️",
                "incomplete": "❌",
                "missing": "🚫"
            }.get(info["status"], "❓")

            report += f"### {status_icon} {Path(doc_path).name}\n"
            report += f"- **Status:** {info['status']}\n"
            report += f"- **Exists:** {info['exists']}\n"

            if info['exists']:
                report += f"- **Size:** {info['size']} bytes\n"
                report += f"- **Last modified:** {info['last_modified'].strftime('%Y-%m-%d %H:%M') if info['last_modified'] else 'Unknown'}\n"
                report += f"- **Recently updated:** {'Yes' if info.get('is_recent') else 'No'}\n"

            report += "\n"

        # Ajouter l'analyse de contenu
        report += "## 📖 Content Analysis\n\n"

        for doc_path, analysis in content_analysis.items():
            report += f"### {Path(doc_path).name}\n"
            report += f"- **Words:** {analysis.get('word_count', 0)}\n"
            report += f"- **Lines:** {analysis.get('line_count', 0)}\n"
            report += f"- **Sections:** {len(analysis.get('sections', []))}\n"
            report += f"- **Code blocks:** {'Yes' if analysis.get('has_code_blocks') else 'No'}\n"
            report += f"- **Tables:** {'Yes' if analysis.get('has_tables') else 'No'}\n"
            report += f"- **Links:** {'Yes' if analysis.get('has_links') else 'No'}\n"
            report += f"- **Completeness score:** {'⭐' * analysis.get('completeness_score', 0)}\n\n"

        # Recommandations
        report += "## 🎯 Recommendations\n\n"

        missing_docs = [doc for doc, info in validation_results.items() if info["status"] == "missing"]
        if missing_docs:
            report += "### Missing Critical Documentation\n"
            for doc in missing_docs:
                report += f"- {doc}\n"
            report += "\n"

        outdated_docs = [doc for doc, info in validation_results.items() if info["status"] == "needs_review"]
        if outdated_docs:
            report += "### Documentation Needing Review\n"
            for doc in outdated_docs:
                report += f"- {doc} (not updated recently)\n"
            report += "\n"

        incomplete_docs = [doc for doc, analysis in content_analysis.items() if analysis.get('completeness_score', 0) < 3]
        if incomplete_docs:
            report += "### Incomplete Documentation\n"
            for doc in incomplete_docs:
                score = content_analysis[doc].get('completeness_score', 0)
                report += f"- {doc} (completeness: {'⭐' * score})\n"
            report += "\n"

        # Organisation actions
        if organization_results.get('moved'):
            report += "### Files Organized\n"
            for moved in organization_results['moved']:
                report += f"- ✅ {moved}\n"
            report += "\n"

        if organization_results.get('errors'):
            report += "### Organization Errors\n"
            for error in organization_results['errors']:
                report += f"- ❌ {error}\n"
            report += "\n"

        report += "---\n*Report generated by NOVAQUOTE Documentation Manager*"

        return report

    def save_report(self, report: str, filename: Optional[str] = None):
        """Sauvegarder le rapport"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"documentation_status_{timestamp}.md"

        reports_dir = self.project_root / "reports" / "documentation"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_path = reports_dir / filename

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"💾 Report saved: {report_path}")
        return report_path

    def run_full_analysis(self):
        """Exécuter l'analyse complète de la documentation"""
        print("=" * 80)
        print("📚 NOVAQUOTE Documentation Manager - Full Analysis")
        print("=" * 80)

        # 1. Scanner la racine
        scan_results = self.scan_root_for_docs()

        # 2. Organiser la documentation
        organization_results = self.organize_docs_in_docs_dir(scan_results)

        # 3. Valider les docs critiques
        validation_results = self.validate_critical_docs()

        # 4. Analyser le contenu
        content_analysis = self.analyze_docs_content()

        # 4.5. Maintenir le README.md
        readme_maintenance = self.maintain_readme()

        # 5. Générer le rapport
        report = self.generate_docs_report(
            scan_results, organization_results,
            validation_results, content_analysis
        )

        # 6. Sauvegarder le rapport
        report_path = self.save_report(report, None)

        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"📄 Full report: {report_path}")
        print("\n🎯 Summary:")
        print(f"   • Found {len(scan_results.get('markdown', [])) + len(scan_results.get('text', [])) + len(scan_results.get('other', []))} documentation files")
        print(f"   • Organized {len(organization_results.get('moved', []))} files")
        print(f"   • Validated {len(validation_results)} critical docs")
        print(f"   • {len([d for d in validation_results.values() if d['status'] == 'current'])} docs are current")
        print(f"   • {len([d for d in validation_results.values() if d['status'] in ['missing', 'incomplete']])} docs need attention")

        return {
            "scan_results": scan_results,
            "organization_results": organization_results,
            "validation_results": validation_results,
            "content_analysis": content_analysis,
            "report_path": report_path
        }


def main():
    """Point d'entrée principal"""
    manager = DocumentationManager()
    results = manager.run_full_analysis()

    # Afficher un résumé final
    print("\n" + "=" * 80)
    print("🎉 Documentation analysis completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
