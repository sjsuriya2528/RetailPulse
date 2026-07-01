import os, glob

views_dir = 'dashboard/views'
files = glob.glob(os.path.join(views_dir, '*.py'))

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    load_data_lines = []
    show_lines = []
    
    state = 'imports'
    
    for line in lines:
        if line.startswith('def show():'):
            continue
            
        if state == 'imports':
            if line.startswith('@st.cache_data'):
                state = 'load_data'
                load_data_lines.append(line)
            elif 'st.markdown(' in line and '<style>' in line:
                show_lines.append('    ' + line.lstrip())
                state = 'show' 
            else:
                if line.strip() and not line.startswith('\"\"\"') and not 'RetailPulse' in line and not line.startswith('import ') and not line.startswith('from ') and not line.startswith('PROCESSED ='):
                    show_lines.append('    ' + line.lstrip())
        elif state == 'load_data':
            if line.startswith('    kpi, ') or line.startswith('    daily, ') or line.startswith('    rfm, ') or line.startswith('    churn, ') or line.startswith('    inv, ') or line.startswith('    exports =') or line.startswith('    st.markdown(') or line.strip() == 'st.markdown(\"\"\")' or line.strip() == 'kpi, orders, order_items, payments, invoices = load_data()':
                state = 'show'
                show_lines.append('    ' + line.lstrip())
            else:
                if line.startswith('def load_data'):
                    load_data_lines.append('def load_data():')
                elif line.startswith('        '):
                    load_data_lines.append('    ' + line[8:])
                elif line.startswith('    '):
                    load_data_lines.append(line)
                else:
                    load_data_lines.append(line)
        elif state == 'show':
            if line.startswith('    '):
                show_lines.append(line)
            elif line.strip() == '':
                show_lines.append('')
            else:
                show_lines.append('    ' + line)
                
    final_content = 'import streamlit as st\nimport pandas as pd\nimport plotly.express as px\nimport plotly.graph_objects as go\nfrom pathlib import Path\nimport io\n\n'
    
    final_content += 'PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"\n\n'
    
    final_content += '\n'.join(load_data_lines) + '\n\n'
    
    final_content += 'def show():\n'
    final_content += '\n'.join(show_lines) + '\n'
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(final_content)
