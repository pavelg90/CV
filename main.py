import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis import network as net
import re

st.set_page_config(layout="wide")


# @st.cache(allow_output_mutation=True)
def get_data():
    url = 'https://docs.google.com/spreadsheets/d/'
    sheet_id = '1lynaboEg3hqvc-xVaL0Gn5k23tjrpenNHTW6y5Vkt6o'
    params = '/export?format=csv'

    # Import csv
    data = pd.read_csv(f'{url}{sheet_id}{params}')
    edges = data[['source', 'target', 'weight']].dropna()
    edges = edges.where(pd.notnull(edges), None)

    # Extract nodes
    nodes = data[['label', 'size', 'group', 'node_color']].dropna()
    nodes = nodes.where(pd.notnull(nodes), None)

    # Extract companies
    companies = data['label'][data['group'] == 'companies'].unique().tolist()

    # Extract Roles
    role = data['label'][data['group'] == 'role'].unique().tolist()

    # Extract Skills
    skills = data['label'][data['group'] == 'skills'].unique().tolist()

    return edges, nodes, companies, role, skills


def generate_graph(edges, nodes, html_file_name=None, filters=None):
    # Define graph network
    g = net.Network(height='800px',
                    width='1200px',
                    bgcolor='#0F202E',
                    # font_color='#FFFFFF'
                    )
    g.set_options('''
                    {"physics": {
        "forceAtlas2Based": {"springLength": 150},
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based",
        "wind": {
            "x": 1.1
        }
    },
        "nodes":
            {"font": {
                "color": "#FFFFFF",
                "size": 20
            },
                "shadow": {
                    "enabled": "true",
                    "color": "rgba(255, 255, 255, 0.2)",
                    "x": 0,
                    "y": 0,
                    "size": 15
                }
            }
    }
    ''')

    # add nodes
    for index, row in nodes.iterrows():
        if isinstance(row['label'], str) or \
                isinstance(row['label'], int):
            label = row['label']
            size = row['size']
            group = row['group']
            color = row['node_color']
            g.add_node(label,
                       size=size,
                       group=group,
                       borderWidth=0,
                       color=color)
    # Add edges
    for index, row in edges.iterrows():
        source = row['source']
        target = row['target']
        weight = row['weight']
        g.add_edge(source,
                   target,
                   weight=weight
                   )
    g.write_html(html_file_name + '.html')


def show_graph(html_file_name=None):
    # Main dashboard wrapper
    with open(html_file_name + '.html', 'r', encoding='utf-8') as f:
        source_code = f.read()
        source_code = re.sub('border:.*;', 'border: none;', source_code)
        components.html(source_code,
                        height=800
                        )


def sidebar(companies, roles, skills):
    with st.sidebar:
        st.subheader('Pavel Gomon')
        st.write('''
        Check out with whom I worked,<br>
        How they called me<br>
        And what did I do there
        ''',
                 unsafe_allow_html=True)
        st.write('<br>', unsafe_allow_html=True)

        # Filters:
        me = ['Me']  # needs this thing here

        companies_selected = st.multiselect('Companies', companies)
        companies_selected = companies_selected if companies_selected else companies

        filtered_roles = get_filtered_list(edges, companies_selected, roles)
        roles_selected = st.multiselect('Roles', filtered_roles)
        roles_selected = roles_selected if roles_selected else filtered_roles

        filtered_skills = get_filtered_list(edges,
                                            roles_selected,
                                            skills)
        skills_selected = st.multiselect('Skills', filtered_skills)
        skills_selected = skills_selected if skills_selected else filtered_skills

    return me, companies_selected, roles_selected, skills_selected


def get_filtered_list(edges, previous_filter_values, next_filter_values):
    edges = edges[(edges['source'].isin(previous_filter_values)) |
                  (edges['target'].isin(previous_filter_values))]
    filtered_roles = []
    for value in edges['source'].unique().tolist() + edges['target'].unique().tolist():
        if value in next_filter_values:
            filtered_roles.append(value)
    return filtered_roles


if __name__ == "__main__":
    # styling:
    with open("app/style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    # Import data
    edges, nodes, companies, role, skills = get_data()

    # Initialize sidebar
    me, companies_selected, roles_selected, skills_selected = sidebar(companies, role, skills)
    filters = companies_selected + roles_selected + skills_selected

    # Filter data
    edges = edges[((edges['source'] == 'Me') & (edges['source'].isin(filters))) |
                  ((edges['source'].isin(me + filters)) & (edges['target'].isin(filters)))]
    nodes = nodes[nodes['label'].isin(me + filters)]

    # save as hml file
    html_file_name = 'graph_net'
    generate_graph(edges, nodes, html_file_name=html_file_name)

    # Get graph from file
    show_graph(html_file_name=html_file_name)

    # Add Link to your repo
    with st.sidebar:
        '''
            [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/AvratanuBiswas/PubLit) 
    
        '''
        st.markdown("<br>", unsafe_allow_html=True)
