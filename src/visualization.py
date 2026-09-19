import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
import pycountry
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

from matplotlib.colors import LinearSegmentedColormap
from mpl_chord_diagram import chord_diagram
from matplotlib.ticker import ScalarFormatter

FONTSIZE = 14
FONT_BIG = 16

COLOR_GREEN = "#6aa84f"
COLOR_YELLOW = "#f1c231"
COLOR_RED = "#cc0100"


def plot_map(
    country_codes_list,
    values_list,
    title,
    legend_label,
    custom_color_scale,
    text_list=None,
    save_path=None,
):
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
        sample_data = pd.DataFrame(
            {
                "country_code": country_codes_list,
                "value": values_list,
                "text": text_list,
            }
        )
    else:
        sample_data = pd.DataFrame(
            {
                "country_code": country_codes_list,
                "value": values_list,
            }
        )

    sample_data["iso3_code"] = sample_data["country_code"].apply(get_iso3)

    sample_data = sample_data.dropna(subset=["iso3_code"])

    location_mode = "ISO-3"

    assert (
        sample_data["value"].notnull().all()
    ), "Some values are missing in the 'value' column."

    fig = px.choropleth(
        sample_data,
        locations="iso3_code",
        color="value",
        hover_name="iso3_code",
        color_continuous_scale=custom_color_scale,
        title=title,
        labels={"value": legend_label, "country_code": "Country"},
        locationmode=location_mode,
    )

    if text_list is not None:

        fig.add_scattergeo(
            locations=sample_data["iso3_code"],
            locationmode=location_mode,
            text=["<b>{}</b>".format(t) for t in sample_data["text"]],
            mode="text",
            textfont=dict(
                color="red",
                size=9,
                family="Arial",
            ),
        )

    fig.update_geos(
        scope="europe",
        showframe=False,
        showcoastlines=True,
        projection_type="natural earth",
    )

    fig.update_layout(
        title_x=0.5,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            showlakes=False,
            bgcolor="rgba(0,0,0,0)",
        ),
        width=1000,
        height=700,
    )

    fig.update_layout(
        title_x=0.5,
        title=dict(
            text=title,
            x=0.5,
            pad=dict(t=40),  # Increase top padding (default is 0)
        ),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            showlakes=False,
            bgcolor="rgba(0,0,0,0)",
        ),
        width=1000,
        height=700,
    )

    if save_path is not None:
        fig.write_image(save_path, width=1000, height=700)

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


def plot_chord(
    df: pd.DataFrame,
    product: str,
    country_type: str,
    top_k_countries: int = 5,
    top_k_pesticides: int = 5,
):
    if country_type == "origin":
        country = "origCountry"
    elif country_type == "reporting":
        country = "sampCountry"
    else:
        print("Wrong country type")
        return

    df["Number of samples with pesticide"] = (
        df["above_mrl_samples"] + df["between_loq_and_mrl_samples"]
    )

    agg = (
        df.groupby([country, "tag"])["Number of samples with pesticide"]
        .sum()
        .reset_index()
    )
    country_totals = agg.groupby(country)[
        "Number of samples with pesticide"
    ].sum()

    top_countries = (
        country_totals.sort_values(ascending=False).head(top_k_countries).index
    )
    agg[country] = agg[country].where(
        agg[country].isin(top_countries), "Other countries"
    )

    agg = (
        agg.groupby([country, "tag"])["Number of samples with pesticide"]
        .sum()
        .reset_index()
    )

    top_pest = (
        df.groupby("tag")["Number of samples with pesticide"]
        .sum()
        .sort_values(ascending=False)
        .head(top_k_pesticides)
        .index
    )
    agg = agg[agg["tag"].isin(top_pest)]

    countries = agg[country].unique().tolist()
    pesticides = agg["tag"].unique().tolist()

    nodes = countries + pesticides
    node_index = {name: i for i, name in enumerate(nodes)}

    matrix = [[0] * len(nodes) for _ in range(len(nodes))]

    for _, row in agg.iterrows():
        i = node_index[row[country]]
        j = node_index[row["tag"]]
        matrix[i][j] = row["Number of samples with pesticide"]
        matrix[j][i] = row["Number of samples with pesticide"]

    colors = []
    for i, node in enumerate(nodes):
        if node in countries:
            gray_value = i / max(len(countries) - 1, 1)
            colors.append((gray_value, gray_value, gray_value, 1.0))
        else:
            if product == "milk":
                t = (i - len(countries)) / max(len(pesticides) - 1, 1)
                r = int(253 + (90 - 253) * t)
                g = int(226 + (24 - 226) * t)
                b = int(243 + (154 - 243) * t)
                colors.append((r / 255, g / 255, b / 255, 1.0))
            elif product == "butter":
                t = (i - len(countries)) / max(len(pesticides) - 1, 1)
                r = int(224 + (2 - 224) * t)
                g = int(251 + (62 - 251) * t)
                b = int(252 + (138 - 252) * t)
                colors.append((r / 255, g / 255, b / 255, 1.0))
            else:
                colors.append(cm.tab20(i % 20))  # pesticide colors

    plt.figure(figsize=(12, 12))
    plt.subplots_adjust(top=0.55)
    chord_diagram(
        matrix,
        names=nodes,
        colors=colors,
        sort="size",
        rotate_names=True,
        fontcolor="black",
        fontsize=10,
    )

    title = f"Chord diagram of the most frequently detected pesticide \n residues in {product} within the Multi Annual National Control Plan (MANCP),\n 2011-2024, and their accosiation with {country_type} countries"
    plt.title(title)


def plot_stats_heatmap(df, country, product, title):
    plt.figure(figsize=(10, 14))

    df_labels = df.copy()
    df_labels["label"] = df_labels.apply(
        lambda x: f"L={int(x['limit_samples'])} \nV={int(x['VAL_samples'])} \n∑={int(x['total_samples'])}",
        axis=1,
    )

    pivot = df.pivot_table(
        index=country, columns="year", values="limit_samples", aggfunc="first"
    )
    pivot = pivot.astype(float)
    labels = df_labels.pivot_table(
        index=country, columns="year", values="label", aggfunc="first"
    )

    if product == "butter":
        cmap = LinearSegmentedColormap.from_list(
            "custom_blue", ["#E0FBFC", "#023E8A"]
        )
    else:
        cmap = LinearSegmentedColormap.from_list(
            "custom_blue", ["#FDE2F3", "#5A189A"]
        )

    ax = sns.heatmap(
        pivot,
        annot=labels,
        fmt="",
        cmap=cmap,
        cbar=False,
        linewidths=0.5,
        linecolor="gray",
        clip_on=False,
        square=False,
    )

    for t in ax.texts:
        t.set_fontsize(9)

    plt.xticks(fontsize=12)
    plt.yticks(rotation=360, fontsize=12)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Country", fontsize=12)
    plt.suptitle(f"{title}", fontsize=14)
    plt.title(
        "L - number of samples exceeding pesticides' limits, V - number of samples with pesticide detected, ∑ - total number of samples ",
        fontsize=10,
    )
    plt.tight_layout()
    plt.subplots_adjust(right=0.98, bottom=0.08, top=0.92, left=0.15)
    plt.show()


def plot_loq_bar(
    df,
    aggregator,
    limits_path="../data/paramcodes.csv",
    prog_type="both",
    product="both",
    external_data=None,
):

    assert prog_type in [
        "o",
        "v",
        "both",
    ], "Type of programme should be 'o', 'v' or 'both'."
    assert product in [
        "butter",
        "milk",
        "both",
    ], "Product should be 'butter', 'milk' or 'both'."

    df_paramcodes = aggregator._get_paramcodes_limits(limits_path)

    sources = {
        "butter": {
            "o": aggregator.butter_obligatory_dataframe,
            "v": aggregator.butter_voluntary_dataframe,
        },
        "milk": {
            "o": aggregator.milk_obligatory_dataframe,
            "v": aggregator.milk_voluntary_dataframe,
        },
    }

    selected_dfs = []

    target_products = ["butter", "milk"] if product == "both" else [product]
    target_progs = ["o", "v"] if prog_type == "both" else [prog_type]

    for p in target_products:
        for t in target_progs:
            temp_df = sources[p][t].copy()
            temp_df["product"] = p.capitalize()
            selected_dfs.append(temp_df)

    if not selected_dfs:
        print("No data found for the selected criteria.")
        return

    df_samples = pd.concat(selected_dfs)

    df = pd.merge(
        df_samples,
        df_paramcodes,
        how="inner",
        left_on="pesticideCode",
        right_on="paramcode",
    )
    df = df[df["resType"] != "BIN"]

    resVal = df["resVal"]
    resType = df["resType"]
    limit = df["limit"]

    conditions = [
        resType.isin(["LOD", "LOQ"]),
        (resVal > 0) & (resVal < limit),
        resVal >= limit,
    ]
    choices = ["% below LOQ", "% between LOQ and MRL", "% above MRL"]

    df["category"] = np.select(conditions, choices, "ERROR")
    df["tag"] = df["product"] + " " + df["year"].astype(str)

    df = (
        df.groupby(["tag", "category"])["sampleId"]
        .nunique()
        .reset_index(name="samplesCount")
    )
    df = df.pivot(
        index="tag", columns="category", values="samplesCount"
    ).fillna(0)

    for col in choices:
        if col not in df.columns:
            df[col] = 0

    df = df.sort_values(["tag"], ascending=False)
    df["total"] = df[choices].sum(axis=1)

    for col in choices:
        df[col] = (df[col] / df["total"] * 100).round(2)

    if external_data is not None:
        ext_df = pd.DataFrame.from_dict(external_data, orient="index")

        for col in choices:
            if col not in ext_df.columns:
                ext_df[col] = 0.0

        ext_df = ext_df[choices]
        df = pd.concat([df[choices], ext_df])

    df = df.sort_index(ascending=False)

    fig = plt.figure(figsize=(12, 0.8 * len(df.index)))
    ax = fig.add_subplot(111)

    colors = [COLOR_GREEN, COLOR_YELLOW, COLOR_RED]
    left = np.zeros(len(df))
    y_pos = np.arange(len(df))

    for i, category in enumerate(choices):
        ax.barh(
            y_pos,
            df[category],
            left=left,
            label=category,
            color=colors[i],
            height=0.5,
        )

        for j, (idx, row) in enumerate(df.iterrows()):
            value = row[category]
            if value == 0:
                continue

            if category == "% above MRL":
                ax.text(
                    left[j] + value + 1,
                    j,
                    f"{value:.1f}",
                    va="center",
                    ha="left",
                    fontsize=FONTSIZE + 1,
                    color="crimson",
                )
            else:
                if value < 2.5:
                    ax.text(
                        left[j] + value / 2,
                        j,
                        f"{value:.1f}",
                        va="center",
                        ha="center",
                        fontsize=FONTSIZE + 1,
                        color="black",
                    )
                else:
                    ax.text(
                        left[j] + value / 2,
                        j,
                        f"{value:.1f}",
                        va="center",
                        ha="center",
                        fontsize=FONTSIZE + 1,
                        color="black",
                    )
        left += df[category].values

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df.index, fontsize=FONT_BIG)
    ax.set_xlabel("Percentage (%)", fontsize=FONT_BIG)
    ax.tick_params(axis="x", labelsize=FONTSIZE)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=3,
        fontsize=FONTSIZE,
    )
    ax.grid(axis="x", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.show()


def _create_multiple_residues_df(
    aggregator, product="butter", prog_type="v", res_type="val"
):

    assert product in [
        "milk",
        "butter",
        "both",
    ], "Product should be milk, butter, or both."
    assert prog_type in [
        "o",
        "v",
        "both",
    ], "Type of programme should be o, v or both."
    assert res_type in [
        "limit",
        "val",
    ], "Type of result should be val or limit."

    df_butter_obligatory = aggregator.butter_obligatory_dataframe
    df_butter_voluntary = aggregator.butter_voluntary_dataframe
    df_milk_obligatory = aggregator.milk_obligatory_dataframe
    df_milk_voluntary = aggregator.milk_voluntary_dataframe

    prog_options = {
        "o": {
            "butter": df_butter_obligatory.assign(product="Butter"),
            "milk": df_milk_obligatory.assign(product="Milk"),
        },
        "v": {
            "butter": df_butter_voluntary.assign(product="Butter"),
            "milk": df_milk_voluntary.assign(product="Milk"),
        },
        "both": {
            "butter": pd.concat(
                [df_butter_obligatory, df_butter_voluntary]
            ).assign(product="Butter"),
            "milk": pd.concat([df_milk_obligatory, df_milk_voluntary]).assign(
                product="Milk"
            ),
        },
    }

    if product == "both":
        df_samples = pd.concat(
            [prog_options[prog_type]["butter"], prog_options[prog_type]["milk"]]
        )
    else:
        df_samples = prog_options[prog_type][product]

    # Get total samples per year before filtering
    total_samples_per_year = (
        df_samples.groupby("year")["sampleId"]
        .nunique()
        .reset_index(name="total_samples")
    )

    if res_type == "val":
        df_samples = df_samples[df_samples["resVal"] > 0]

    df = (
        df_samples.groupby(["year", "sampleId"])["pesticideCode"]
        .nunique()
        .reset_index(name="pesticideCount")
    )
    df = (
        df.groupby(["year", "pesticideCount"])["sampleId"]
        .nunique()
        .reset_index(name="samplesCount")
    )

    # Add samples with 0 pesticides
    zero_pesticide_rows = []
    for _, row in total_samples_per_year.iterrows():
        year = row["year"]
        total_samples = row["total_samples"]
        positive_samples = df[df["year"] == year]["samplesCount"].sum()
        zero_samples = total_samples - positive_samples
        if zero_samples > 0:
            zero_pesticide_rows.append(
                {
                    "year": year,
                    "pesticideCount": 0,
                    "samplesCount": zero_samples,
                }
            )

    if zero_pesticide_rows:
        df_zero = pd.DataFrame(zero_pesticide_rows)
        df = pd.concat([df, df_zero], ignore_index=True).sort_values(
            ["year", "pesticideCount"]
        )

    df["pesticideCount"] = df["pesticideCount"].astype(str)

    return df


def plot_multiple_residues_bar(
    aggregator, product="butter", prog_type="v", res_type="val"
):

    df = _create_multiple_residues_df(aggregator, product, prog_type, res_type)
    df["percentage"] = (
        df.groupby("year")["samplesCount"]
        .transform(lambda x: x / x.sum() * 100)
        .round(2)
    )

    years = sorted(df["year"].unique())

    rows = max(1, int(np.ceil(len(years) / 2)))
    fig, axes = plt.subplots(rows, 2, figsize=(14, rows * 5), squeeze=False)
    labels = [
        "(a)",
        "(b)",
        "(c)",
        "(d)",
        "(e)",
        "(f)",
        "(g)",
        "(h)",
        "(i)",
        "(j)",
        "(k)",
        "(l)",
        "(m)",
        "(o)",
    ][: len(years)]

    for i, ax in enumerate(axes.flat):
        if i < len(years):
            year = years[i]
            data = df[df["year"] == year]

            if product == "butter":
                bar_color = "#023E8A"
            else:
                bar_color = "#5A189A"

            ax.bar(
                data["pesticideCount"],
                data["percentage"],
                color=bar_color,
                tick_label=[
                    f"{row['pesticideCount']}\n(n={row['samplesCount']:.0f})"
                    for _, row in data.iterrows()
                ],
                width=0.8,
            )
            ax.tick_params(axis="x", labelsize=9)

            total_samples = int(data["samplesCount"].sum())
            ax.set_title(
                f"{labels[i]} Year: {year}\nTotal samples: {total_samples}"
            )
            ax.set_xlabel("Number of pesticides")
            ax.set_ylabel("Percentage (%) of all samples tested")
        else:
            ax.axis("off")

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.show()


def plot_highest_levels_per_year(
    df, color, pesticide, limit, product, log_scale=True, country="origCountry"
):

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.axhline(y=limit, color="darkred", linestyle="dashed", label="limit")

    p = ax.bar(
        df["year"], df["resVal"], color=color, alpha=0.5, label=df[country]
    )

    ax.bar_label(
        p,
        labels=df[country].astype(str).tolist(),
        padding=3,
        label_type="center",
        fontweight="bold",
        fontsize=11,
    )
    if log_scale:
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(ScalarFormatter())
        ax.ticklabel_format(style="plain", axis="y")
        ax.set_ylabel("Residue Value (log scale)")
    else:
        ax.set_ylabel("Residue Value")

    ax.set_xlabel("Year")
    ax.set_title(f"Highest Levels of {pesticide} per Year, product: {product}")
    ax.set_xticks(df["year"].unique())
    ax.tick_params(labelrotation=45, axis="x")
    plt.tight_layout()
    plt.show()
