"""
🔧 KiloCode Command Logger - NOVAQUOTE Trading System
Log tous les appels KiloCode des agents pour monitoring temps réel
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class KiloCodeLogger:
    """Logger pour capturer tous les appels KiloCode des agents Python"""

    def __init__(self):
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.log_file = self.log_dir / "kilocode_commands.log"
        self.log_dir.mkdir(exist_ok=True)

    def log_command(
        self,
        agent_name: str,
        command: str,
        response: str,
        duration_ms: int,
        exit_code: int,
        mode: str = "ask",
        agent_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Logger un appel KiloCode"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "command": command,
            "response": response[:2000] + "..." if len(response) > 2000 else response,  # Limiter la taille
            "duration": f"{duration_ms}ms",
            "exitCode": exit_code,
            "mode": mode,
            "agentType": agent_type,
            "metadata": metadata or {}
        }

        try:
            # Lire le contenu existant
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    existing_logs = f.read().strip()
            else:
                existing_logs = ""

            # Ajouter la nouvelle entrée
            new_entry = json.dumps(log_entry, ensure_ascii=False, indent=2)

            with open(self.log_file, 'a', encoding='utf-8') as f:
                if existing_logs and not existing_logs.endswith('\n'):
                    f.write('\n')
                f.write(new_entry + '\n')

        except Exception as e:
            print(f"[ERROR] Failed to log KiloCode command: {e}")

    def get_recent_commands(self, limit: int = 20, agent_filter: Optional[str] = None) -> list:
        """Lire les commandes récentes depuis le log"""

        if not self.log_file.exists():
            return []

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            commands = []
            for line in reversed(lines):
                line = line.strip()
                if line:
                    try:
                        cmd_data = json.loads(line)

                        # Filtrer par agent si spécifié
                        if agent_filter and cmd_data.get("agentType") != agent_filter.lower():
                            continue

                        commands.append(cmd_data)

                        if len(commands) >= limit:
                            break

                    except json.JSONDecodeError:
                        continue

            return commands

        except Exception as e:
            print(f"[ERROR] Failed to read KiloCode commands: {e}")
            return []


# Instance globale du logger
kilocode_logger = KiloCodeLogger()