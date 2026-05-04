# DreamOS-Only Variant Cleanup Census

Generated: 2026-05-04T04:04:00-05:00
Root: /data/data/com.termux/files/home/projects

Excluded: AgentTools, because it is a toolbelt repo, not a Dream.OS variant.

## Summary

```text
repo                     branch                   dirty    files    dirs     pyc      json     md       yaml     js      
----                     ------                   -----    -----    ----     ---      ----     --       ----     --      
DreamOS                  main                     4        157      41       0        8        55       10       0       
Dream.os                 main                     0        1033     207      0        93       51       19       0       
Victor.os                agent-1-agent-leader     0        385      116      0        10       30       11       0       
```

## Top Directories

### DreamOS
```text
     13 _ops/reports
      9 runtime/tasks
      8 tests
      8 src/core
      7 dreamos/core
      6 dreamos/tools
      6 dreamos/tests
      6 01_runtime_core
      6 00_foundation
      5 src/transports
      5 _ops/scripts
      5 03_execution
      5 01_core
      4 src/relay
      4 contracts
      4 _ops/reports/repo_consolidation
      3 tools
      3 tests/audit
      3 scripts/ci
      3 scripts
```

### Dream.os
```text
     69 tests
     58 core
     39 memory
     22 utils
     22 interfaces/pyqt/tabs
     22 core/services
     18 core/factories
     18 config
     17 scripts
     17 core/social/strategies
     16 social/strategies
     15 social
     14 tests/gui
     14 cursor_prompts/ollama_tests
     14 core/social
     14 core/Agents
     13 interfaces/pyqt
     13 core/chatgpt_automation
     12 templates/prompt_templates
     10 runtime/tasks
```

### Victor.os
```text
     36 src/dreamos/tools
     15 src/dreamos/core
     13 scripts
     13 _ops/reports
     12 tests
     11 src/dreamos/integrations/social
     10 src/dreamos/tools/scanner
      8 tests/runtime
      8 src/dreamos/testing/module_validation
      7 src/dreamos/backtesting
      7 src/dreamos/agents
      6 tests/integration
      6 src/dreamos/utils
      6 src/dreamos/tools/agent_resume
      6 src/dreamos/governance
      6 src/dreamos/feedback
      6 src/dreamos/bridge
      6 src/dreamos/agents/agent3
      6 dreamos_clean
      6 dreamos/skills/lifecycle
```

## Next Rule

Clean only remaining dirty Dream.OS variants. If all are clean, stop pruning and generate promote manifests.
