import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import pycountry
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

from matplotlib.colors import LinearSegmentedColormap
from mpl_chord_diagram import chord_diagram

def plot_map(country_codes_list, values_list, title, legend_label, custom_color_scale, text_list=None, save_path=None) :
    def get_iso3(iso2_code):
        try:
            country = pycountry.countries.get(alpha_2=iso2_code)
            return country.alpha_3
        except:
            return None

    try:
        pio.renderers.default = "notebook"
    except:
        pio.renderers.default = "png"

    if text_list is not None:
        sample_data = pd.DataFrame({
            'country_code': country_codes_list,
            'value': values_list,
            'text': text_list
        })
    else:
        sample_data = pd.DataFrame({
            'country_code': country_codes_list,
            'value': values_list,
        })

    sample_data['iso3_code'] = sample_data['country_code'].apply(get_iso3)

    sample_data = sample_data.dropna(subset=['iso3_code'])

    location_mode = 'ISO-3'

    assert sample_data['value'].notnull().all(), "Some values are missing in the 'value' column."


    fig = px.choropleth(
        sample_data,
        locations='iso3_code',
        color='value',
        hover_name='iso3_code',
        color_continuous_scale=custom_color_scale,  
        title=title,
        labels={'value': legend_label, 'country_code': 'Country'},
        locationmode=location_mode,
    )
    
    if text_list is not None:
                
        fig.add_scattergeo(
            locations=sample_data['iso3_code'],
            locationmode=location_mode, 
            text=["<b>{}</b>".format(t) for t in sample_data['text']],
            mode='text',
            textfont=dict(
                color='red',
                size=9,
                family='Arial',
            )
        )
    
    fig.update_geos(
        scope='europe',
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth'
    )

    fig.update_layout(
        title_x=0.5,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            showlakes=False,
            bgcolor='rgba(0,0,0,0)'
        ),
        width=1000,
        height=700
    )
    
    fig.update_layout(
    title_x=0.5,
    title=dict(
        text=title,
        x=0.5,
        pad=dict(t=40)  # Increase top padding (default is 0)
    ),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        showlakes=False,
        bgcolor='rgba(0,0,0,0)'
    ),
    width=1000,
    height=700
    )
    
    if save_path is not None:
        fig.write_html(save_path)

    try:
        fig.show()
        print("✓ Interactive map displayed successfully!")
    except Exception as e:
        print(f"Interactive display failed: {e}")
        print("Trying static image display...")
        try:
            img_bytes = fig.to_image(format="png", width=1000, height=700)
            from IPython.display import Image, display
            display(Image(img_bytes))
            print("✓ Static map displayed successfully!")
        except Exception as e2:
            print(f"Static display also failed: {e2}")
            print("Please use the matplotlib alternative below.")
            
            
def plot_chord(df: pd.DataFrame, product: str, country_type: str, title: str, top_k_countries: int = 5, top_k_pesticides: int = 5):
    if country_type == 'origin':
        country = "origCountry"
    elif country_type == 'reporting':
        country = 'sampCountry'
    else:
        print('Wrong country type')
        return 
    
    agg = df.groupby([country, "name"])["Number of samples with pesticide"].sum().reset_index()
    country_totals = agg.groupby(country)["Number of samples with pesticide"].sum()

    top_countries = country_totals.sort_values(ascending=False).head(top_k_countries).index
    agg[country] = agg[country].where(agg[country].isin(top_countries), "Other countries")

    agg = agg.groupby([country, "name"])["Number of samples with pesticide"].sum().reset_index()


    top_pest = (
        df.groupby("name")["Number of samples with pesticide"]
        .sum()
        .sort_values(ascending=False)
        .head(top_k_pesticides)
        .index
    )
    agg = agg[agg["name"].isin(top_pest)]

    countries = agg[country].unique().tolist()
    pesticides = agg["name"].unique().tolist()

    nodes = countries + pesticides
    node_index = {name: i for i, name in enumerate(nodes)}

    matrix = [[0] * len(nodes) for _ in range(len(nodes))]

    for _, row in agg.iterrows():
        i = node_index[row[country]]
        j = node_index[row["name"]]
        matrix[i][j] = row["Number of samples with pesticide"]
        matrix[j][i] = row["Number of samples with pesticide"]  

    

    colors = []
    for i, node in enumerate(nodes):
        if node in countries:
            gray_value = i / max(len(countries) - 1, 1)
            colors.append((gray_value, gray_value, gray_value, 1.0))
        else:
            if product == 'milk':
                t = (i - len(countries)) / max(len(pesticides) - 1, 1)
                r = int(253 + (90 - 253) * t)
                g = int(226 + (24 - 226) * t)
                b = int(243 + (154 - 243) * t)
                colors.append((r / 255, g / 255, b / 255, 1.0))
            elif product == 'butter':
                t = (i - len(countries)) / max(len(pesticides) - 1, 1)
                r = int(224 + (2 - 224) * t)
                g = int(251 + (62 - 251) * t)
                b = int(252 + (138 - 252) * t)
                colors.append((r / 255, g / 255, b / 255, 1.0))
            else:
                colors.append(cm.tab20(i % 20))  # pesticide colors

    plt.figure(figsize=(12,12))
    plt.subplots_adjust(top=0.55)
    chord_diagram(
        matrix,
        names=nodes,
        colors=colors,
        sort="size",      
        rotate_names=True,
        fontcolor="black",
        fontsize=10
    )
    plt.title(title)

def plot_stats_heatmap(df, country, product, title):
    plt.figure(figsize=(10, 14))

    df_labels = df.copy()
    df_labels['label'] = df_labels.apply(
        lambda x: f"L={int(x['limit_samples'])} \nV={int(x['VAL_samples'])} \n∑={int(x['total_samples'])}", 
        axis=1
    )

    pivot = df.pivot_table(index=country, columns='year', values='limit_samples', aggfunc='first')
    pivot = pivot.astype(float) 
    labels = df_labels.pivot_table(index=country, columns='year', values='label', aggfunc='first')

    if product == 'butter':
        cmap = LinearSegmentedColormap.from_list("custom_blue", ["#E0FBFC", "#023E8A"])
    else:
        cmap = LinearSegmentedColormap.from_list("custom_blue", ["#FDE2F3", "#5A189A"])

    ax = sns.heatmap(
        pivot,
        annot=labels,
        fmt='',
        cmap=cmap,
        cbar=False,
        linewidths=0.5,
        linecolor='gray',
        clip_on=False,
        square=False
    )
    
    for t in ax.texts:
        t.set_fontsize(9)
        
    plt.xticks(fontsize=12 )
    plt.yticks(rotation=360, fontsize=12)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Country', fontsize=12)
    plt.suptitle(f"{title}", fontsize=14)
    plt.title("L - number of samples exceeding pesticides' limits, V - number of samples with pesticide detected, ∑ - total number of samples ", fontsize=10)
    plt.tight_layout()
    plt.subplots_adjust(right=0.98, bottom=0.08, top=0.92, left=0.15)
    plt.show()