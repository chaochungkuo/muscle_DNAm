import plotly.graph_objects as go
import plotly.figure_factory as ff

import plotly.express as px

def generate_3DPCA(target_df, title, x_label, y_label, z_label):
    
    fig = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='petal_width',
                color='species')
    fig.show()

def generate_hp(target_df, hp_title):
    rowlabels = target_df.index.tolist()
    collabels = target_df.columns.tolist()
    # Initialize figure by creating upper dendrogram
    fig = ff.create_dendrogram(target_df, orientation='bottom', labels=collabels)
    fig['layout'].update(plot_bgcolor='rgba(0, 0, 0, 0)')  # Set the background color to transparent

    for i in range(len(fig['data'])):
        fig['data'][i]['yaxis'] = 'y2'

    # Create Side Dendrogram
    dendro_side = ff.create_dendrogram(target_df, orientation='right')
    for i in range(len(dendro_side['data'])):
        dendro_side['data'][i]['xaxis'] = 'x2'

    # Add Side Dendrogram Data to Figure
    for dendrodata in dendro_side['data']:
        fig.add_trace(dendrodata)

    # Create Heatmap
    dendroup_leaves = fig['layout']['xaxis']['ticktext']
    dendroup_leaves = list(map(int, dendroup_leaves))
    dendroside_leaves = dendro_side['layout']['yaxis']['ticktext']
    dendroside_leaves = list(map(int, dendroside_leaves))
    # data_dist = pdist(target_df)
    # heat_data = squareform(data_dist)
    heat_data = target_df[dendroside_leaves,:]
    heat_data = heat_data[:,dendroup_leaves]

    heatmap = [
        go.Heatmap(
            x = dendroup_leaves,
            y = dendroside_leaves,
            z = heat_data,
            colorscale = 'Blues'
        )
    ]

    heatmap[0]['x'] = fig['layout']['xaxis']['tickvals']
    heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

    # Add Heatmap Data to Figure
    for data in heatmap:
        fig.add_trace(data)

    # Edit Layout
    fig.update_layout({'title':hp_title, 'width':800, 'height':800,
                       'showlegend':False, 'hovermode': 'closest',
                       })
    # Edit xaxis
    fig.update_layout(xaxis={'domain': [.15, 1],
                                    'mirror': False,
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'ticks':""})
    # Edit xaxis2
    fig.update_layout(xaxis2={'domain': [0, .15],
                                    'mirror': False,
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'showticklabels': False,
                                    'ticks':""})

    # Edit yaxis
    fig.update_layout(yaxis={'domain': [0, .85],
                                    'mirror': False,
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'showticklabels': False,
                                    'ticks': ""
                            })
    # Edit yaxis2
    fig.update_layout(yaxis2={'domain':[.825, .975],
                                    'mirror': False,
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'showticklabels': False,
                                    'ticks':""})

    # Plot!
    fig.show()