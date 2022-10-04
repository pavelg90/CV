import re


with open('graph_net.html', 'r', encoding='utf-8') as f:
    source_code = f.read()
    # {"font": {"color": "#FFFFFF"}
    source_code = re.sub('float: left;',
                         'float: left;\nfont-size: 2em',
                         source_code)
    print(source_code)