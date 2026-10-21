import re

def extract_actions_of_sm(log_content: str, only_tool_calls: bool = False) -> str:
    lines = log_content.splitlines()
    
    in_block = False
    block_closer = None
    current_block_lines = []
    preceded_by_calling_tools = False
    
    blocks_info = [] 
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        if not in_block:
            # 1. Detect opening tags
            if stripped_line.startswith('```') or stripped_line == '<code>':
                in_block = True
                block_closer = '</code>' if stripped_line == '<code>' else '```'
                current_block_lines = []
                
                # Forgiving Look-behind: Ignore empty lines and nested opening tags
                preceded_by_calling_tools = False
                for j in range(i - 1, -1, -1):
                    prev_line = lines[j].strip()
                    if not prev_line:
                        continue
                    if prev_line == '<code>' or prev_line.startswith('```'):
                        continue
                    
                    if prev_line == "Calling tools:":
                        preceded_by_calling_tools = True
                    break
                    
            else:
                # 3 & 4. Search for associated error message
                if blocks_info and blocks_info[-1]['is_valid'] and blocks_info[-1]['error'] is None:
                    if re.match(r"^Code parsing failed on line \d+ due to: SyntaxError", stripped_line):
                        blocks_info[-1]['error'] = stripped_line
        else:
            # Detect closing tags
            if stripped_line == block_closer:
                in_block = False
                
                # Forgiving Look-ahead: Scan forward for 'Calling tools:'
                # Abort if we hit boundary markers for other sections, ensuring we don't bleed into the next turn.
                is_valid = False
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if not next_line:
                        continue
                    
                    if next_line == "Calling tools:":
                        is_valid = not preceded_by_calling_tools
                        break
                        
                    if next_line in ["Observation:", "Execution logs:", "New task:"] or next_line.startswith("Thought:"):
                        break
                
                # Clean up nested markdown (e.g., if ```python was inside <code>)
                # This ensures perfect normalization to <code> in the final output.
                if current_block_lines:
                    if current_block_lines[0].strip().startswith('```'):
                        current_block_lines = current_block_lines[1:]
                    if current_block_lines and current_block_lines[-1].strip() == '```':
                        current_block_lines = current_block_lines[:-1]
                
                blocks_info.append({
                    'code': '\n'.join(current_block_lines).strip('\n'),
                    'is_valid': is_valid,
                    'error': None
                })
            else:
                current_block_lines.append(line)
        
        i += 1
        
    # 5. Format Output
    output_chunks = []
    for block in blocks_info:
        if block['is_valid']:
            chunk = f"<code>\n{block['code']}\n</code>"
            if block['error']:
                chunk += f"\n{block['error']}"
            output_chunks.append(chunk)
            
    return "\n\n".join(output_chunks)


def extract_actions_of_oh(
    log_text: str,
    only_tool_calls: bool = False
) -> str:
    """
    Return formatted string output.

    Rules
    -----
    If only_tool_calls=True:
        Return only tool-call action dictionaries.

    If only_tool_calls=False:
        Return:
        1. action dictionaries
        2. any <sometext_ignore> appearing inside [agent] blocks,
           including text between:
               [agent] tool_call:
               ...
               action : {...}
           BUT ignore any <sometext_ignore> in [environment/...].
        3. [user] prompts

    Extra processing
    ----------------
    - Truncate workspace prefix:
        /home/xuanlong/Misbehaviors/misbehavior/DevEval/SC_*/ -> removed

    - For str_replace actions:
        old_str / new_str => "... (placeholder)"
    """

    outputs = []

    # --------------------------------------------------
    # Split numbered blocks
    # --------------------------------------------------
    blocks = re.findall(
        r'(\[\d+\].*?)(?=\n\[\d+\]|\Z)',
        log_text,
        re.DOTALL
    )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def truncate_paths(text: str) -> str:
        return re.sub(
            r"/home/xuanlong/Misbehaviors/misbehavior/DevEval/SC_[^/]+/",
            "",
            text
        )

    def hide_replace_strings(text: str) -> str:
        if "'command': 'str_replace'" in text:
            text = re.sub(
                r"'old_str':\s*'.*?',",
                "'old_str': '... (placeholder)',",
                text,
                flags=re.DOTALL
            )
            text = re.sub(
                r"'new_str':\s*'.*?',",
                "'new_str': '... (placeholder)',",
                text,
                flags=re.DOTALL
            )
        return text

    # --------------------------------------------------
    # Process each block
    # --------------------------------------------------
    counter = 1
    for block in blocks:
        block = block.strip()

        is_user = "[user]" in block
        is_agent = "[agent]" in block
        is_environment = "[environment/" in block

        if only_tool_calls:
            # Standard tool-call only extraction
            if is_agent:
                action_match = re.search(
                    r'action\s*:\s*(\{.*?\})(?=\n|$)',
                    block,
                    re.DOTALL
                )
                if action_match:
                    content = action_match.group(1).strip()
                    content = truncate_paths(content)
                    content = hide_replace_strings(content)
                    outputs.append({
                        "role": "agent",
                        "content": content
                    })
        else:
            # Full sequence tracking
            if is_user:
                # Extract the user block, discarding the original number
                match = re.search(r'^\[\d+\]\s*(\[user\].*)', block, re.DOTALL)
                if match:
                    content = match.group(1).strip()
                else:
                    content = re.sub(r'^\[\d+\]\s*', '', block).strip()
                
                content = truncate_paths(content)
                
                outputs.append({
                    "role": "raw",
                    "content": f"[{counter:03d}] {content}"
                })
                counter += 1
                
            elif is_agent:
                # Extract the block up to the action dict, discarding the original number
                match = re.search(
                    r'^\[\d+\]\s*(\[agent\].*?action\s*:\s*\{.*?\})', 
                    block, 
                    re.DOTALL | re.MULTILINE
                )
                if match:
                    content = match.group(1).strip()
                else:
                    # Fallback: just strip the original counter
                    content = re.sub(r'^\[\d+\]\s*', '', block).strip()
                
                content = truncate_paths(content)
                content = hide_replace_strings(content)
                
                outputs.append({
                    "role": "raw",
                    "content": f"[{counter:03d}] {content}"
                })
                counter += 1
                
            elif is_environment:
                # Extract exclusively the [environment/tool_name] (STATUS)
                match = re.search(r'(\[environment/[^\]]+\]\s*\([^)]+\))', block)
                if match:
                    env_header = match.group(1).strip()
                else:
                    # Fallback logic if pattern matching fails
                    first_line = block.split('\n')[0].strip()
                    env_header = re.sub(r'^\[\d+\]\s*', '', first_line).strip()
                    if env_header.endswith(':'):
                        env_header = env_header[:-1].strip()
                
                outputs.append({
                    "role": "raw",
                    "content": f"[{counter:03d}] {env_header}"
                })
                counter += 1

    # --------------------------------------------------
    # Build final formatted string
    # --------------------------------------------------
    lines = []

    if only_tool_calls:
        for i, msg in enumerate(outputs, 1):
            lines.append(f"{i}. [{msg['role']}]")
            lines.append(msg["content"])
            lines.append("-" * 60)
        return "\n".join(lines)
    else:
        # Join the re-labeled blocks with dashes
        separator = "\n" + "-" * 60 + "\n"
        return separator.join(msg["content"] for msg in outputs)


def extract_actions_of_ag(
    log_text: str,
    only_tool_calls: bool = False
) -> list[dict[str, str]]:
    """
    Extract messages from the log file.

    Args:
        log_text: Raw log text
        only_tool_calls:
            False -> return all messages normally
            True  -> return ONLY assistant tool call payload lines
                     (ignore assistant reasoning/content text)

    Returns:
        List[Dict[str, str]]

    Behavior when only_tool_calls=True:
        Output only messages like:
        - {'id': ..., 'function': ..., ...}
    """

    pattern = re.compile(
        r"--- Message\s+\d+\s+\((.*?)\)\s+---\n(.*?)(?=--- Message\s+\d+\s+\(|\Z)",
        re.DOTALL
    )

    messages = []

    for match in pattern.finditer(log_text):
        role = match.group(1).strip()
        block = match.group(2).strip()

        # --------------------------------------------------
        # TOOL CALLS ONLY MODE
        # --------------------------------------------------
        if only_tool_calls:
            if role != "ASSISTANT":
                continue

            tool_match = re.search(
                r"Tool Calls:\n(.*)",
                block,
                re.DOTALL
            )

            if not tool_match:
                continue

            tool_text = tool_match.group(1).strip()

            if tool_text:
                messages.append({
                    "role": role,
                    "content": tool_text
                })

            continue

        # --------------------------------------------------
        # NORMAL MODE
        # --------------------------------------------------
        if role == "TOOL":
            content = "<TOOL_RESPONSE>"

        else:
            parts = []

            # Content section
            content_match = re.search(
                r"Content:\n(.*?)(?=\nTool Calls:|\Z)",
                block,
                re.DOTALL
            )

            if content_match:
                txt = content_match.group(1).strip()
                if txt:
                    parts.append(txt)

            # Tool Calls section
            tool_match = re.search(
                r"Tool Calls:\n(.*)",
                block,
                re.DOTALL
            )

            if tool_match:
                tool_txt = tool_match.group(1).strip()
                if tool_txt:
                    parts.append("Tool Calls:\n" + tool_txt)

            content = "\n\n".join(parts)

        messages.append({
            "role": role,
            "content": content
        })

    return messages


def extract_actions_from_history(log_text: str, framework: str):
    if framework == "sm":
        return extract_actions_of_sm(log_text, True)
    elif framework == "oh":
        return extract_actions_of_oh(log_text, True)
    elif framework == "ag":
        return extract_actions_of_ag(log_text, True)
    else:
        raise ValueError(f"Framework {framework} is not supported")
