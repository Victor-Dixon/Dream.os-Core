from __future__ import annotations

from collections.abc import Callable

from src.core.phase2_contracts import CommandMessage, CommandResult

CommandHandler = Callable[[CommandMessage], CommandResult]


class CommandRouter:
    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler] = {
            "resume": self._handle_resume,
            "sync": self._handle_sync,
            "restart": self._handle_restart,
        }

    def register(self, command: str, handler: CommandHandler) -> None:
        self._handlers[command.strip().lower()] = handler

    def route(self, message: CommandMessage) -> CommandResult:
        handler = self._handlers.get(message.command.strip().lower())
        if handler is None:
            return CommandResult(
                command=message.command,
                status="ignored",
                detail=f"unknown command: {message.command}",
                data={"known_commands": sorted(self._handlers)},
            )
        return handler(message)

    def _handle_resume(self, message: CommandMessage) -> CommandResult:
        target = str(message.args.get("target", "swarm"))
        return CommandResult(
            command="resume",
            status="ok",
            detail=f"resumed {target}",
            data={"target": target},
        )

    def _handle_sync(self, message: CommandMessage) -> CommandResult:
        scope = str(message.args.get("scope", "all"))
        return CommandResult(
            command="sync",
            status="ok",
            detail=f"sync complete for {scope}",
            data={"scope": scope},
        )

    def _handle_restart(self, message: CommandMessage) -> CommandResult:
        target = str(message.args.get("target", "agent"))
        return CommandResult(
            command="restart",
            status="ok",
            detail=f"restart issued for {target}",
            data={"target": target},
        )
