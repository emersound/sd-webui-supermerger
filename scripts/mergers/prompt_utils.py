"""
Prompt Utilities for SuperMerger Extension

This module provides clean, well-documented utilities for extracting and processing
LoRA information from Stable Diffusion prompts.

Key functions:
- extract_loras_from_prompt(): Parse LoRA syntax from prompts
- build_output_name_lookup(): Create mapping from ss_output_name metadata to filenames
- get_lora_directory(): Get the configured LoRA directory

This module has no Gradio dependencies and can be used standalone.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Try to import from SD WebUI modules, with fallbacks for standalone use
try:
    from modules import extra_networks, shared
    HAS_WEBUI = True
except ImportError:
    HAS_WEBUI = False
    extra_networks = None
    shared = None


def get_lora_directory() -> Path:
    """
    Get the LoRA models directory.
    
    Returns:
        Path to the LoRA directory, or None if not found.
    """
    if HAS_WEBUI and shared:
        lora_dir = getattr(shared.cmd_opts, 'lora_dir', None)
        if lora_dir:
            return Path(lora_dir)
        return Path(shared.data_path) / "models" / "Lora"
    return None


def load_lora_metadata(filepath: Path) -> Optional[Dict]:
    """
    Load metadata from a safetensors LoRA file.
    
    Args:
        filepath: Path to the .safetensors file
        
    Returns:
        Metadata dict, or None if file can't be read
    """
    try:
        import json
        with open(filepath, 'rb') as f:
            header_len = int.from_bytes(f.read(8), 'little')
            header = json.loads(f.read(header_len))
            return header.get('__metadata__', {})
    except Exception:
        return None


def build_output_name_lookup() -> Dict[str, str]:
    """
    Build a mapping from ss_output_name metadata values to actual LoRA filenames.
    
    This allows matching LoRAs by their training output name (stored in metadata)
    rather than just their filename.
    
    Returns:
        Dict mapping ss_output_name -> filename (without extension)
    """
    lookup = {}
    
    # Prefer using lora.available_loras if available (already loaded by WebUI)
    try:
        import lora
        for name, lora_obj in lora.available_loras.items():
            try:
                if hasattr(lora_obj, 'metadata') and lora_obj.metadata:
                    ss_output = lora_obj.metadata.get('ss_output_name', '')
                    if ss_output and ss_output != name and ss_output.lower() != 'merged':
                        lookup[ss_output] = name
            except:
                pass
        return lookup
    except ImportError:
        pass
    
    # Fallback to scanning files directly
    lora_dir = get_lora_directory()
    if not lora_dir or not lora_dir.exists():
        return lookup
    
    for filepath in lora_dir.glob("**/*.safetensors"):
        metadata = load_lora_metadata(filepath)
        if metadata:
            output_name = metadata.get('ss_output_name')
            if output_name:
                filename = filepath.stem
                lookup[output_name] = filename
    
    return lookup


def parse_lora_syntax(prompt: str) -> List[Tuple[str, float, Optional[str]]]:
    """
    Parse LoRA syntax from a prompt string.
    
    Supports formats:
    - <lora:name:weight>
    - <lora:name:weight:lbw_params>
    
    Args:
        prompt: The prompt string containing LoRA references
        
    Returns:
        List of tuples: (name, weight, lbw_params or None)
    """
    results = []
    pattern = r'<lora:([^:>]+):([^:>]+)(?::([^>]+))?>'
    
    for match in re.finditer(pattern, prompt):
        name = match.group(1).strip()
        try:
            weight = float(match.group(2))
        except ValueError:
            weight = 1.0
        lbw = match.group(3).strip() if match.group(3) else None
        results.append((name, weight, lbw))
    
    return results


def extract_loras_from_prompt(
    prompt: str,
    selectable_loras: List[str] = None
) -> Tuple[List[str], str]:
    """
    Extract LoRA information from a prompt and match to available LoRAs.
    
    This is the main function for the "get from prompt" feature.
    
    Args:
        prompt: The prompt string containing LoRA references
        selectable_loras: List of available LoRA names (filenames without extension)
        
    Returns:
        Tuple of:
        - List of LoRA names to check (matched to selectable_loras)
        - Formatted string "name1:weight1,name2:weight2,..."
    """
    if not prompt or not isinstance(prompt, str):
        return [], ""
    
    selectable_loras = selectable_loras or []
    parsed = parse_lora_syntax(prompt)
    output_name_lookup = build_output_name_lookup()
    
    checked_loras = []
    formatted_parts = []
    
    for name, weight, lbw in parsed:
        if lbw:
            formatted_parts.append(f"{name}:{weight}:{lbw}")
        else:
            formatted_parts.append(f"{name}:{weight}")
        
        if name in selectable_loras:
            checked_loras.append(name)
        elif name in output_name_lookup:
            actual_filename = output_name_lookup[name]
            if actual_filename in selectable_loras:
                checked_loras.append(actual_filename)
    
    return checked_loras, ",".join(formatted_parts)
