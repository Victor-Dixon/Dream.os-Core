# PROMOTE_CONTRACT Inspection

Generated: 2026-05-04T10:14:52-05:00
Canonical: /data/data/com.termux/files/home/projects/DreamOS

## Dream.os merit chain schema

variant_path=/data/data/com.termux/files/home/projects/Dream.os/core/schemas/merit_chain_schema.json
canonical_same_path=/data/data/com.termux/files/home/projects/DreamOS/core/schemas/merit_chain_schema.json

```text
variant_exists=yes
65 /data/data/com.termux/files/home/projects/Dream.os/core/schemas/merit_chain_schema.json
3b0a541c89d3a899c44cc031bd2407e6716b1704c99764391027fdf8af0b2ff9  /data/data/com.termux/files/home/projects/Dream.os/core/schemas/merit_chain_schema.json
canonical_same_path_exists=no
```

### Variant preview

```text
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MeritChain Entry Schema",
  "description": "Schema for validating MeritChain entries representing high-resonance profile matches",
  "type": "object",
  "required": ["platform", "username", "resonance_score", "timestamp"],
  "properties": {
    "platform": {
      "type": "string",
      "description": "The platform where the profile was found (e.g., 'twitter', 'instagram')"
    },
    "username": {
      "type": "string",
      "description": "The username of the profile"
    },
    "resonance_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Resonance score indicating how well the profile matches your criteria (0-100)"
    },
    "matching_traits": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of traits that match your criteria"
    },
    "red_flags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of potential red flags or concerns"
    },
    "summary": {
      "type": "string",
      "description": "Short summary of why this profile matches or doesn't match"
    },
    "first_message": {
      "type": "string",
      "description": "Suggested first message to send to this person"
    },
    "should_save_to_meritchain": {
      "type": "boolean",
      "description": "Whether this profile should be saved to the merit chain"
    },
    "merit_tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Tags to categorize this merit entry"
    },
    "suggested_follow_up": {
      "type": "string",
      "description": "Suggested follow-up action or message"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 timestamp when this entry was created"
    }
  },
  "additionalProperties": true
} ```

### Same-path diff if canonical exists

```diff
NO_SAME_PATH_DIFF
```

## Victor.os product output schema

variant_path=/data/data/com.termux/files/home/projects/Victor.os/src/dreamos/core/tasks/schemas/product_output_schema.py
canonical_same_path=/data/data/com.termux/files/home/projects/DreamOS/src/dreamos/core/tasks/schemas/product_output_schema.py

```text
variant_exists=yes
128 /data/data/com.termux/files/home/projects/Victor.os/src/dreamos/core/tasks/schemas/product_output_schema.py
6a27d74123c12712525985f7b44dcda799513743a0e2df7dcfcdc7686fd4199b  /data/data/com.termux/files/home/projects/Victor.os/src/dreamos/core/tasks/schemas/product_output_schema.py
canonical_same_path_exists=no
```

### Variant preview

```text
"""
Product output schema for Dream.OS.

This module defines the JSON schema for validating product outputs,
ensuring they meet quality standards and contain all required metadata.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class ProductOutputMetadata(BaseModel):
    """Metadata for a product output."""
    created_at: datetime = Field(..., description="Timestamp when the output was created")
    created_by: str = Field(..., description="ID of the agent that created the output")
    version: str = Field(..., description="Version of the output format")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score of the output")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the output")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies required for the output")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics for the output")

class CodeOutput(BaseModel):
    """Code-based product output."""
    type: str = Field("code", const=True)
    content: str = Field(..., description="The actual code content")
    language: str = Field(..., description="Programming language of the code")
    metadata: ProductOutputMetadata

class DocumentationOutput(BaseModel):
    """Documentation-based product output."""
    type: str = Field("documentation", const=True)
    content: str = Field(..., description="The documentation content")
    format: str = Field(..., description="Format of the documentation (e.g., markdown, rst)")
    metadata: ProductOutputMetadata

class DataOutput(BaseModel):
    """Data-based product output."""
    type: str = Field("data", const=True)
    content: Dict[str, any] = Field(..., description="The data content")
    format: str = Field(..., description="Format of the data (e.g., json, yaml)")
    metadata: ProductOutputMetadata

class ProductOutput(BaseModel):
    """Base model for all product outputs."""
    output_id: str = Field(..., description="Unique identifier for the output")
    task_id: str = Field(..., description="ID of the task that generated this output")
    output_type: str = Field(..., description="Type of output (code, documentation, data)")
    content: Union[CodeOutput, DocumentationOutput, DataOutput]
    metadata: ProductOutputMetadata
    validation_status: str = Field(..., description="Status of output validation")
    validation_errors: List[str] = Field(default_factory=list, description="Any validation errors found")

# JSON Schema for validation
PRODUCT_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["output_id", "task_id", "output_type", "content", "metadata", "validation_status"],
    "properties": {
        "output_id": {"type": "string"},
        "task_id": {"type": "string"},
        "output_type": {"type": "string", "enum": ["code", "documentation", "data"]},
        "content": {
            "oneOf": [
                {"$ref": "#/definitions/code_output"},
                {"$ref": "#/definitions/documentation_output"},
                {"$ref": "#/definitions/data_output"}
            ]
        },
        "metadata": {"$ref": "#/definitions/metadata"},
        "validation_status": {"type": "string", "enum": ["valid", "invalid", "pending"]},
        "validation_errors": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "definitions": {
        "metadata": {
            "type": "object",
            "required": ["created_at", "created_by", "version", "quality_score"],
            "properties": {
                "created_at": {"type": "string", "format": "date-time"},
```

### Same-path diff if canonical exists

```diff
NO_SAME_PATH_DIFF
```

## Victor.os cursor feedback schema

variant_path=/data/data/com.termux/files/home/projects/Victor.os/src/dreamos/integrations/cursor/bridge/schemas/cursor_feedback_schema.json
canonical_same_path=/data/data/com.termux/files/home/projects/DreamOS/src/dreamos/integrations/cursor/bridge/schemas/cursor_feedback_schema.json

```text
variant_exists=yes
47 /data/data/com.termux/files/home/projects/Victor.os/src/dreamos/integrations/cursor/bridge/schemas/cursor_feedback_schema.json
16e22fa48babf64ec53623e6a445ea85ccfffec878c978bca905f5b790f9d380  /data/data/com.termux/files/home/projects/Victor.os/src/dreamos/integrations/cursor/bridge/schemas/cursor_feedback_schema.json
canonical_same_path_exists=no
```

### Variant preview

```text
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Cursor Feedback Payload",
  "description": "Schema for feedback/results sent from the Cursor Bridge back to GPT.",
  "type": "object",
  "properties": {
    "request_id": {
      "description": "The unique identifier of the original command request.",
      "type": "string",
      "format": "uuid"
    },
    "timestamp": {
      "description": "ISO 8601 timestamp of when the feedback was generated.",
      "type": "string",
      "format": "date-time"
    },
    "command_type": {
      "description": "The type of command this feedback relates to.",
      "type": "string",
       "enum": [
        "edit_file", 
        "run_terminal", 
        "codebase_search", 
        "file_search",
        "read_file",
        "list_dir",
        "grep_search"
      ]
    },
    "status": {
      "description": "Execution status of the command.",
      "type": "string",
      "enum": ["success", "error", "simulated_success"]
    },
    "result": {
      "description": "Output data from the command execution (if status is success/simulated_success) or an error message/details (if status is error). Can be string or object.",
      "type": ["object", "string", "array", "null"]
    }
  },
  "required": [
    "request_id",
    "timestamp",
    "command_type",
    "status",
    "result"
  ],
  "additionalProperties": false
} ```

### Same-path diff if canonical exists

```diff
NO_SAME_PATH_DIFF
```

## Victor.os gpt command schema

variant_path=/data/data/com.termux/files/home/projects/Victor.os/src/dreamos/integrations/cursor/bridge/schemas/gpt_command_schema.json
canonical_same_path=/data/data/com.termux/files/home/projects/DreamOS/src/dreamos/integrations/cursor/bridge/schemas/gpt_command_schema.json

```text
variant_exists=yes
59 /data/data/com.termux/files/home/projects/Victor.os/src/dreamos/integrations/cursor/bridge/schemas/gpt_command_schema.json
a35cb9f65ab38b8e5c6712da03ba4b8fed28666a7cc2dd6fcb4b3fd5c6dedf7b  /data/data/com.termux/files/home/projects/Victor.os/src/dreamos/integrations/cursor/bridge/schemas/gpt_command_schema.json
canonical_same_path_exists=no
```

### Variant preview

```text
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GPT Command Payload",
  "description": "Schema for commands sent from GPT to the Cursor Bridge.",
  "type": "object",
  "properties": {
    "request_id": {
      "description": "Unique identifier for the request.",
      "type": "string",
      "format": "uuid"
    },
    "timestamp": {
      "description": "ISO 8601 timestamp of when the command was generated.",
      "type": "string",
      "format": "date-time"
    },
    "command_type": {
      "description": "The type of action Cursor should perform.",
      "type": "string",
      "enum": [
        "edit_file", 
        "run_terminal", 
        "codebase_search", 
        "file_search",
        "read_file",
        "list_dir",
        "grep_search"
      ]
    },
    "parameters": {
      "description": "Command-specific parameters.",
      "type": "object",
      "properties": { 
        "target_file": {"type": "string"},
        "code_edit": {"type": "string"},
        "instructions": {"type": "string"},
        "command": {"type": "string"},
        "is_background": {"type": "boolean"},
        "query": {"type": "string"},
        "target_directories": {"type": "array", "items": {"type": "string"}},
        "start_line_one_indexed": {"type": "integer"},
        "end_line_one_indexed_inclusive": {"type": "integer"},
        "should_read_entire_file": {"type": "boolean"},
        "relative_workspace_path": {"type": "string"},
        "case_sensitive": {"type": "boolean"},
        "include_pattern": {"type": "string"},
        "exclude_pattern": {"type": "string"}
        
      },
      "# Note": "Specific required fields depend on command_type, needs runtime validation."
    }
  },
  "required": [
    "request_id",
    "timestamp",
    "command_type",
    "parameters"
  ],
  "additionalProperties": false
} ```

### Same-path diff if canonical exists

```diff
NO_SAME_PATH_DIFF
```

# Suggested First Merge Lane

Do not bulk-copy. Promote contracts one at a time under canonical paths after deciding ownership.
