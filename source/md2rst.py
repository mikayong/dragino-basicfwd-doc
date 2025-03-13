import re

def md_to_rst(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    rst_lines = []
    in_code_block = False
    code_indent = 0
    list_stack = []
    current_list_indent = 0

    # 标题符号映射表
    underline_symbols = ['=', '-', '~', '^', '"', "'"]
    
    for line in lines:
        stripped = line.strip()
        
        # 处理代码块
        if in_code_block:
            if stripped.startswith('```'):
                in_code_block = False
                rst_lines.append('')
            else:
                rst_lines.append(' ' * code_indent + line)
            continue
            
        if stripped.startswith('```'):
            in_code_block = True
            lang = stripped[3:].strip()
            if lang:
                rst_lines.append(f'.. code-block:: {lang}')
                code_indent = 3
            else:
                rst_lines.append('::')
                code_indent = 3
            rst_lines.append('')
            continue
        
        # 处理标题
        if stripped.startswith('#'):
            match = re.match(r'^(#+)\s+(.*)', stripped)
            if match:
                level = len(match.group(1)) - 1
                title = match.group(2)
                symbol = underline_symbols[level] if level < len(underline_symbols) else '-'
                rst_lines.append(title)
                rst_lines.append(symbol * len(title))
                continue
        
        # 处理列表
        list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)', line)
        if list_match:
            indent = len(list_match.group(1))
            bullet = list_match.group(2)
            content = list_match.group(3)
            
            # 确定列表类型
            list_type = 'unordered' if bullet in ['-', '*', '+'] else 'ordered'
            
            # 计算缩进层级
            list_level = indent // 2  # 假设每级缩进2个空格
            
            # 维护列表层级栈
            while list_stack and list_stack[-1]['level'] >= list_level:
                list_stack.pop()
                
            # 确定当前列表符号
            if not list_stack or list_stack[-1]['level'] < list_level:
                list_stack.append({
                    'level': list_level,
                    'type': list_type,
                    'bullet': bullet if list_type == 'unordered' else '1.'
                })
                
            # 生成RST列表项
            current_indent = list_level * 2
            rst_line = ' ' * current_indent + list_stack[-1]['bullet'] + ' ' + content
            rst_lines.append(rst_line)
            continue
        
        # 处理图片
        img_match = re.match(r'!$$(.*?)$$$(.*?)(?:\s+"(.*?)")?$', line)
        if img_match:
            alt_text = img_match.group(1)
            url = img_match.group(2)
            title = img_match.group(3)
            rst_lines.append(f'.. image:: {url}')
            rst_lines.append(f'   :alt: {alt_text}')
            if title:
                rst_lines.append(f'   :title: {title}')
            continue
        
        # 处理链接
        link_match = re.findall(r'$$(.*?)$$$(.*?)$', line)
        if link_match:
            for text, url in link_match:
                line = line.replace(f'[{text}]({url})', f'`{text} <{url}>`_')
        
        # 处理加粗和斜体
        line = re.sub(r'\*\*(.*?)\*\*', r'**\1**', line)
        line = re.sub(r'\*(.*?)\*', r'*\1*', line)
        
        rst_lines.append(line)

    # 后处理：确保代码块正确缩进
    rst_content = '\n'.join(rst_lines)
    rst_content = re.sub(r'\n::\n\s*\n', '\n::\n\n', rst_content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rst_content)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python md_to_rst.py input.md output.rst")
        sys.exit(1)
    md_to_rst(sys.argv[1], sys.argv[2])
