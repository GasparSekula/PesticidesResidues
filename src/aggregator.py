import pandas as pd
import numpy as np


class DataAggregator:
    def __init__(self, data_dir: str, milk_dir: str, butter_dir: str):
        self.data_dir = data_dir
        self.dataframe = pd.read_pickle(data_dir)
        self.milk_dataframe = pd.read_pickle(milk_dir)
        self.butter_dataframe = pd.read_pickle(butter_dir)

        obligatory_year_list_milk = [2013, 2016, 2019, 2022]
        obligatory_year_list_butter = [2012, 2015]

        self.milk_obligatory_dataframe = self.milk_dataframe[
            (self.milk_dataframe["year"].isin(obligatory_year_list_milk))
            & self.milk_dataframe["progType"].isin(["K009A", "K018A"])
        ]
        self.butter_obligatory_dataframe = self.butter_dataframe[
            (self.butter_dataframe["year"].isin(obligatory_year_list_butter))
            & self.butter_dataframe["progType"].isin(["K009A", "K018A"])
        ]
        self.milk_voluntary_dataframe = self.milk_dataframe[
            (~self.milk_dataframe["year"].isin(obligatory_year_list_milk))
            | (self.milk_dataframe["progType"].isin(["K005A", "K018A"]))
        ]
        self.butter_voluntary_dataframe = self.butter_dataframe[
            (~self.butter_dataframe["year"].isin(obligatory_year_list_butter))
            | (self.butter_dataframe["progType"].isin(["K005A", "K018A"]))
        ]

    # 1
    def count_samples(
        self,
        year_list: list,
        country_list: list,
        limits_dir: str,
        product: str = "both",
    ):
        limits = pd.read_csv(limits_dir)

        if product == "milk":
            df = self.milk_dataframe
            limits = limits[limits["product"] == "milk"]

        elif product == "butter":
            df = self.butter_dataframe
            limits = limits[limits["product"] == "butter"]
        else:
            df = self.dataframe

        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]
        df = (
            df.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="unique_sample_count")
        )
        df_limits = pd.merge(
            left=df,
            right=limits,
            how="right",
            left_on=["sampCountry", "year"],
            right_on=["country", "year"],
        ).fillna(0)
        df_limits["success"] = (
            df_limits["limit"] <= df_limits["unique_sample_count"]
        )

        df_obligatory_voluntary = self.count_obligatory_voluntary_samples(
            year_list, country_list, product
        )
        df_limits = pd.merge(
            left=df_limits,
            right=df_obligatory_voluntary,
            how="left",
            left_on=["country", "year"],
            right_on=["sampCountry", "year"],
        )
        df_limits["obligaotry_samples"] = (
            df_limits["obligaotry_samples"].fillna(0).astype(int)
        )
        df_limits["voluntary_samples"] = (
            df_limits["voluntary_samples"].fillna(0).astype(int)
        )
        df_limits["obligatory_success"] = (
            df_limits["limit"] <= df_limits["obligaotry_samples"]
        )

        return df_limits[
            [
                "country",
                "year",
                "limit",
                "unique_sample_count",
                "success",
                "obligaotry_samples",
                "voluntary_samples",
                "obligatory_success",
            ]
        ]

    # 2.1
    def count_samples_without_limits(
        self, year_list: list, country_list: list, product: str = "both"
    ):
        if product == "milk":
            df = self.milk_dataframe
        elif product == "butter":
            df = self.butter_dataframe
        else:
            df = self.dataframe
        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]
        df = (
            df.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="unique_sample_count")
        )
        all_pairs = pd.MultiIndex.from_product(
            [country_list, year_list], names=["sampCountry", "year"]
        )
        df = (
            df.set_index(["sampCountry", "year"])
            .reindex(all_pairs, fill_value=0)
            .reset_index()
        )
        return df

    def count_obligatory_voluntary_samples(
        self,
        year_list: list,
        country_list: list,
        product: str = "milk",
        positive=False,
    ):
        if product == "milk":
            df_obligatory = self.milk_obligatory_dataframe.copy()
            df_voluntary = self.milk_voluntary_dataframe.copy()
        elif product == "butter":
            df_obligatory = self.butter_obligatory_dataframe.copy()
            df_voluntary = self.butter_voluntary_dataframe.copy()
        else:
            return 0

        if positive:
            df_obligatory = df_obligatory[~df_obligatory["resVal"].isna()]
            df_voluntary = df_voluntary[~df_voluntary["resVal"].isna()]

        df_obligatory = df_obligatory[df_obligatory["year"].isin(year_list)]
        df_obligatory = df_obligatory[
            df_obligatory["sampCountry"].isin(country_list)
        ]
        df_obligatory = (
            df_obligatory.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="obligaotry_samples")
        )

        df_voluntary = df_voluntary[df_voluntary["year"].isin(year_list)]
        df_voluntary = df_voluntary[
            df_voluntary["sampCountry"].isin(country_list)
        ]
        df_voluntary = (
            df_voluntary.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="voluntary_samples")
        )

        result = pd.merge(
            df_obligatory, df_voluntary, on=["sampCountry", "year"], how="outer"
        ).fillna(0)
        return result

    def country_year_pesticide_count(
        self, year_list, country_list, paramcodes_path
    ):
        df = self.dataframe
        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]
        res = (
            df.groupby(["sampCountry", "year", "pesticideCode"])["sampleId"]
            .count()
            .reset_index(name="sample_count")
        )
        total_samples_per_country_year = (
            self.dataframe[
                self.dataframe["sampCountry"].isin(country_list)
                & self.dataframe["year"].isin(year_list)
            ]
            .groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
        )

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        res = pd.merge(
            res, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        res["percentage"] = res.apply(
            lambda row: (
                row["sample_count"]
                / total_samples_per_country_year[
                    (row["sampCountry"], row["year"])
                ]
            )
            * 100,
            axis=1,
        ).round(2)
        return res

    # 2.2
    def country_year_pesticide_list(
        self, year_list, country_list, paramcodes_path, product="both", top_k=10
    ):
        if product == "milk":
            df = self.milk_dataframe
        elif product == "butter":
            df = self.butter_dataframe
        else:
            df = self.dataframe
        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]
        df = df[~df["resVal"].isna()]

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        df = pd.merge(
            df, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        res = (
            df.groupby(["sampCountry", "year", "tag"])["sampleId"]
            .nunique()
            .reset_index(name="Number of samples with pesticide")
        )
        res = res.sort_values(
            ["sampCountry", "year", "Number of samples with pesticide"],
            ascending=[True, True, False],
        )
        res = (
            res.groupby(["sampCountry", "year"])
            .head(top_k)
            .reset_index(drop=True)
        )
        return res

    def country_year_pesticide_origin_list(
        self, year_list, country_list, paramcodes_path, product="both", top_k=10
    ):
        if product == "milk":
            df = self.milk_dataframe
        elif product == "butter":
            df = self.butter_dataframe
        else:
            df = self.dataframe
        df = df[df["year"].isin(year_list)]
        df = df[df["origCountry"].isin(country_list)]
        df = df[~df["resVal"].isna()]

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        df = pd.merge(
            df, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        res = (
            df.groupby(["origCountry", "year", "tag"])["sampleId"]
            .nunique()
            .reset_index(name="Number of samples with pesticide")
        )
        res = res.sort_values(
            ["origCountry", "year", "Number of samples with pesticide"],
            ascending=[True, True, False],
        )
        res = (
            res.groupby(["origCountry", "year"])
            .head(top_k)
            .reset_index(drop=True)
        )
        return res

    # 2.3.
    def percentage_with_pesticides(self, year_list, country_list, product):
        if product == "milk":
            df_obligatory = self.milk_obligatory_dataframe.copy().assign(
                programme="obligatory"
            )
            df_voluntary = self.milk_voluntary_dataframe.copy().assign(
                programme="voluntary"
            )
        elif product == "butter":
            df_obligatory = self.butter_obligatory_dataframe.copy().assign(
                programme="obligatory"
            )
            df_voluntary = self.butter_voluntary_dataframe.copy().assign(
                programme="voluntary"
            )
        else:
            print("For both products, no obligatory years are considered.")

        df = pd.concat([df_obligatory, df_voluntary], ignore_index=True)

        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]

        res1 = df.groupby(["sampCountry", "year", "programme"])[
            "sampleId"
        ].nunique()

        res2 = df.groupby(["sampCountry", "year", "programme"])[
            "sampleId"
        ].nunique()

        val_count = (
            df[df["resType"] == "VAL"]
            .groupby(["sampCountry", "year", "programme"])["sampleId"]
            .nunique()
        )

        res1, res2 = res1.align(res2, fill_value=0)
        val_count = val_count.reindex(res2.index, fill_value=0)

        percentage = (
            (res1 / res2 * 100)
            .round(2)
            .reset_index(name="percentage_with_pesticides")
        )
        val_percentage = (
            (val_count / res2 * 100)
            .round(2)
            .reset_index(name="percentage_val_result")
        )
        # merge including programme to keep rows aligned
        percentage = percentage.merge(
            val_percentage, on=["sampCountry", "year", "programme"], how="left"
        ).fillna(0)

        # merge total samples from res2 to avoid length mismatch
        total_samples = res2.reset_index(name="total_samples")
        percentage = percentage.merge(
            total_samples, on=["sampCountry", "year", "programme"], how="left"
        ).fillna(0)

        return percentage

    def percentage_with_number_pesticides(
        self, year_list, country_list, product
    ):
        if product == "milk":
            df = self.milk_dataframe
        elif product == "butter":
            df = self.butter_dataframe
        else:
            df = self.dataframe

        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]

        grouped = (
            df[~df["resVal"].isna()]
            .groupby(["sampCountry", "year", "sampleId"])["pesticideCode"]
            .count()
            .reset_index(name="number_of_pesticides")
        )
        res1 = (
            grouped.groupby(["sampCountry", "year", "number_of_pesticides"])[
                "sampleId"
            ]
            .count()
            .reset_index(name="samples_count")
        )
        total_samples = (
            df.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="total_samples")
        )
        samples_with_pesticides = (
            df[~df["resVal"].isna()]
            .groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="samples_with_pesticides")
        )
        pesticides_per_sample = (
            df[~df["resVal"].isna()]
            .groupby(["sampCountry", "year", "sampleId"])["pesticideCode"]
            .count()
            .reset_index(name="number_of_pesticides")
        )
        count_by_number = (
            pesticides_per_sample.groupby(
                ["sampCountry", "year", "number_of_pesticides"]
            )["sampleId"]
            .count()
            .reset_index(name="samples_count")
        )
        count_by_number = count_by_number.merge(
            total_samples, on=["sampCountry", "year"], how="left"
        )
        count_by_number = count_by_number.merge(
            samples_with_pesticides, on=["sampCountry", "year"], how="left"
        )
        count_by_number["percentage_of_all_samples"] = (
            count_by_number["samples_count"]
            / count_by_number["total_samples"]
            * 100
        ).round(2)
        count_by_number["percentage_of_samples_with_pesticides"] = (
            (
                count_by_number["samples_count"]
                / count_by_number["samples_with_pesticides"].replace(0, np.nan)
                * 100
            )
            .round(2)
            .fillna(0)
        )

        return count_by_number

    # 2.4.
    def percentage_with_pesticides_limits(
        self,
        year_list,
        country_list,
        product,
        limits_path,
        sample_id=False,
        only_unacceptable=True,
    ):
        if product == "milk":
            df = self.milk_dataframe
        elif product == "butter":
            df = self.butter_dataframe
        else:
            df = self.butter_dataframe
            print("For both products, no obligatory years are considered.")

        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]

        df_limits = self._get_paramcodes_limits(path=limits_path)

        res1 = pd.merge(
            df,
            df_limits,
            left_on="pesticideCode",
            right_on="paramcode",
            how="left",
        )
        res1 = res1[res1["limit"] >= 0]
        res1["resVal"] = res1["resVal"].fillna(0)
        res1["acceptable"] = res1["resVal"] <= res1["limit"]
        if only_unacceptable:
            res1 = res1[res1["acceptable"] == False]
        if product == "milk":
            obligatory_year_list = [2013, 2016, 2019, 2022]
        elif product == "butter":
            obligatory_year_list = [2012, 2015]
        else:
            obligatory_year_list = []
        res1["obligatory_programme"] = res1["year"].isin(
            obligatory_year_list
        ) & res1["progType"].isin(["K009A", "K018A"])
        res2 = (
            df.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="total_count")
        )
        res2_indexed = res2.set_index(["sampCountry", "year"])[
            "total_count"
        ].to_dict()

        res1_index = res1.set_index(["sampCountry", "year"])
        res1["total_samples"] = res1_index.index.map(res2_indexed.get)
        unacceptable_counts = (
            res1.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .to_dict()
        )
        res1["unacceptable_count"] = res1_index.index.map(
            unacceptable_counts.get
        )
        res1["unacceptable_percentage"] = (
            100 * res1["unacceptable_count"] / res1["total_samples"]
        ).round(2)

        if sample_id:
            res1["customSampleId"] = res1["sampleId"].astype(str).str[-5:]
            res1 = res1[
                [
                    "year",
                    "customSampleId",
                    "sampCountry",
                    "origCountry",
                    "progType",
                    "long_name",
                    "limit",
                    "resVal",
                    "acceptable",
                    "obligatory_programme",
                    "total_samples",
                    "unacceptable_count",
                    "unacceptable_percentage",
                ]
            ]
        else:
            res1 = res1[
                [
                    "year",
                    "sampCountry",
                    "origCountry",
                    "progType",
                    "name",
                    "limit",
                    "resVal",
                    "acceptable",
                    "obligatory_programme",
                    "total_samples",
                    "unacceptable_count",
                    "unacceptable_percentage",
                ]
            ]

        return res1

    # 2.5.
    def country_pesticides(
        self,
        year_list,
        country_list,
        paramcodes_path,
        top_k=10,
        product="both",
        programme="obligatory",
    ):
        if product == "milk":
            df_source = self.milk_dataframe
            if programme == "obligatory":
                df = self.milk_obligatory_dataframe.copy()
            elif programme == "voluntary":
                df = self.milk_voluntary_dataframe.copy()
            else:
                df = self.milk_dataframe
        elif product == "butter":
            df_source = self.butter_dataframe
            if programme == "obligatory":
                df = self.butter_obligatory_dataframe.copy()
            elif programme == "voluntary":
                df = self.butter_voluntary_dataframe.copy()
            else:
                df = self.butter_dataframe
        else:
            df_source = self.dataframe
            df = self.dataframe
            print("For both products, no obligatory years are considered.")

        df = df[df["year"].isin(year_list)]
        # df = df[df["origCountry"].isin(country_list)]
        df = df[df["resVal"] > 0]

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        df = pd.merge(
            df, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        df_top_pesticides = (
            df.groupby(["sampCountry", "tag"])["sampleId"]
            .nunique()
            .reset_index(name="samples_count")
        )
        df_top_pesticides = df_top_pesticides.sort_values(
            ["sampCountry", "samples_count"], ascending=[True, False]
        )
        df_top_pesticides = (
            df_top_pesticides.groupby("sampCountry")
            .head(top_k)
            .reset_index(drop=True)
        )
        top_pesticides_list = df_top_pesticides["tag"].unique().tolist()

        df_samples = df_source.groupby(["sampCountry"])["sampleId"].nunique()

        res = df[df["tag"].isin(top_pesticides_list)]
        res = (
            res.groupby(["sampCountry", "tag"])["sampleId"]
            .nunique()
            .reset_index(name="pesticides_count")
        )
        res = res.merge(
            df_samples.reset_index(name="sample_count"),
            on="sampCountry",
            how="left",
        )
        res["percentage"] = (
            res["pesticides_count"] / res["sample_count"] * 100
        ).round(2)

        pivot = res.pivot(
            index="tag", columns="sampCountry", values="percentage"
        ).fillna(0)
        pivot.reset_index(inplace=True)
        return pivot

    # 3
    def pesticides_sampling_relation(
        self, year_list, country_list, product, programme
    ):
        if product == "milk":
            if programme == "obligatory":
                df = self.milk_obligatory_dataframe.copy()
            elif programme == "voluntary":
                df = self.milk_voluntary_dataframe.copy()
            else:
                df = self.milk_dataframe
        elif product == "butter":
            if programme == "obligatory":
                df = self.butter_obligatory_dataframe.copy()
            elif programme == "voluntary":
                df = self.butter_voluntary_dataframe.copy()
            else:
                df = self.butter_dataframe
        else:
            df = self.dataframe

        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]

        df_pesticides = df[~df["resVal"].isna()]
        df_pesticides = (
            df_pesticides.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="pesticides_samples_count")
        )

        df = (
            df.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="samples_count")
        )

        res = pd.merge(
            df, df_pesticides, on=["sampCountry", "year"], how="left"
        )
        res["pesticides_samples_count"] = (
            res["pesticides_samples_count"].fillna(0).astype(int)
        )
        return res

    # 5
    def count_detected_pesticides(self, year_list, country_list, product):
        if product == "milk":
            df = self.milk_dataframe
            df_obligatory = self.milk_obligatory_dataframe.copy()
            df_voluntary = self.milk_voluntary_dataframe.copy()
        elif product == "butter":
            df = self.butter_dataframe
            df_obligatory = self.butter_obligatory_dataframe.copy()
            df_voluntary = self.butter_voluntary_dataframe.copy()
        else:
            print("For both products, no obligatory years are considered.")
            pass

        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]
        df = df[~df["resVal"].isna()]
        res = (
            df.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="unique_sample_with_pesticides_count")
        )

        df_obligatory = df_obligatory[df_obligatory["year"].isin(year_list)]
        df_obligatory = df_obligatory[
            df_obligatory["sampCountry"].isin(country_list)
        ]
        df_obligatory = df_obligatory[~df_obligatory["resVal"].isna()]
        df_obligatory = (
            df_obligatory.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="obligatory_unique_sample_with_pesticides_count")
        )

        df_voluntary = df_voluntary[df_voluntary["year"].isin(year_list)]
        df_voluntary = df_voluntary[
            df_voluntary["sampCountry"].isin(country_list)
        ]
        df_voluntary = df_voluntary[~df_voluntary["resVal"].isna()]
        df_voluntary = (
            df_voluntary.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="voluntary_unique_sample_with_pesticides_count")
        )

        res = pd.merge(
            res, df_obligatory, on=["year", "sampCountry"], how="left"
        ).fillna(0)
        res["obligatory_unique_sample_with_pesticides_count"] = res[
            "obligatory_unique_sample_with_pesticides_count"
        ].astype(int)

        res = pd.merge(
            res, df_voluntary, on=["year", "sampCountry"], how="left"
        ).fillna(0)
        res["voluntary_unique_sample_with_pesticides_count"] = res[
            "voluntary_unique_sample_with_pesticides_count"
        ].astype(int)

        return res

    def yearly_top_pesticides(self, year_list, country_list, product, top_k=5):
        if product == "milk":
            df = self.milk_dataframe
            df_obligatory = self.milk_obligatory_dataframe.copy()
            df_voluntary = self.milk_voluntary_dataframe.copy()
        elif product == "butter":
            df = self.butter_dataframe
            df_obligatory = self.butter_obligatory_dataframe.copy()
            df_voluntary = self.butter_voluntary_dataframe.copy()
        else:
            df = self.butter_dataframe
            df_obligatory = self.butter_obligatory_dataframe.copy()
            print("For both products, no obligatory years are considered.")

        df = df[df["year"].isin(year_list)]
        df = df[df["sampCountry"].isin(country_list)]
        df = df[~df["resVal"].isna()]
        res = (
            df.groupby(["year", "sampCountry"])["sampleId"]
            .nunique()
            .reset_index(name="unique_sample_with_pesticides_count")
        )

        df_obligatory = df_obligatory[df_obligatory["year"].isin(year_list)]
        df_obligatory = df_obligatory[
            df_obligatory["sampCountry"].isin(country_list)
        ]
        df_obligatory = df_obligatory[~df_obligatory["resVal"].isna()]
        df_obligatory = (
            df_obligatory.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="obligatory_unique_sample_with_pesticides_count")
        )

        df_voluntary = df_voluntary[df_voluntary["year"].isin(year_list)]
        df_voluntary = df_voluntary[
            df_voluntary["sampCountry"].isin(country_list)
        ]
        df_voluntary = df_voluntary[~df_voluntary["resVal"].isna()]
        df_voluntary = (
            df_voluntary.groupby(["sampCountry", "year"])["sampleId"]
            .nunique()
            .reset_index(name="voluntary_unique_sample_with_pesticides_count")
        )

        res = pd.merge(
            res, df_obligatory, on=["year", "sampCountry"], how="left"
        ).fillna(0)
        res["obligatory_unique_sample_with_pesticides_count"] = res[
            "obligatory_unique_sample_with_pesticides_count"
        ].astype(int)

        res = pd.merge(
            res, df_voluntary, on=["year", "sampCountry"], how="left"
        ).fillna(0)
        res["voluntary_unique_sample_with_pesticides_count"] = res[
            "voluntary_unique_sample_with_pesticides_count"
        ].astype(int)

        res = res.sort_values(
            ["year", "unique_sample_with_pesticides_count"],
            ascending=[True, False],
        )
        res = res.groupby("year").head(top_k).reset_index(drop=True)
        return res

    # 6

    def number_of_pesticides(self, year_list: list, product="both"):
        if product == "milk":
            df = self.milk_dataframe
        elif product == "butter":
            df = self.butter_dataframe
        else:
            df = self.dataframe

        # all samples performed
        df_all_samples = (
            df.groupby(["year"])["sampleId"]
            .nunique()
            .reset_index(name="totalSamplesCount")
        )

        # samples with >1 pesticide
        df_pests = df[~df["resVal"].isna()]
        df_pests = (
            df_pests.groupby(["year", "sampleId"])["pesticideCode"]
            .nunique()
            .reset_index(name="pesticideCount")
        )
        df_pests = (
            df_pests.groupby(["year", "pesticideCount"])["sampleId"]
            .nunique()
            .reset_index(name="sampleCount")
        )

        df_positive_samples = (
            df_pests.groupby(["year"])["sampleCount"]
            .sum()
            .reset_index(name="totalPositiveSamples")
        )

        df_zero_samples = pd.merge(
            df_all_samples, df_positive_samples, on=["year"]
        )
        df_zero_samples["totalNegativeSamples"] = (
            df_zero_samples["totalSamplesCount"]
            - df_zero_samples["totalPositiveSamples"]
        )
        df_zero_samples = df_zero_samples[["year", "totalNegativeSamples"]]

        df_zero_samples["pesticideCount"] = 0
        df_zero_samples = df_zero_samples.rename(
            columns={"totalNegativeSamples": "sampleCount"}
        )
        df_zero_samples = df_zero_samples[
            ["year", "pesticideCount", "sampleCount"]
        ]

        df_pests = (
            pd.concat([df_pests, df_zero_samples], ignore_index=True)
            .sort_values(["year", "pesticideCount"])
            .reset_index(drop=True)
        )
        df_pests = pd.merge(df_pests, df_all_samples, on=["year"], how="left")
        df_pests["percentage"] = (
            100 * df_pests["sampleCount"] / df_pests["totalSamplesCount"]
        ).round(2)
        return df_pests

    # 7
    def country_pesticide_relation(
        self,
        year_list,
        country_list,
        product,
        paramcodes_path,
        top_k=5,
        programme=None,
    ):
        if product == "milk":
            if programme == "obligatory":
                df_source = self.milk_obligatory_dataframe
            elif programme == "voluntary":
                df_source = self.milk_voluntary_dataframe
            else:
                df_source = self.milk_dataframe
        elif product == "butter":
            if programme == "obligatory":
                df_source = self.butter_obligatory_dataframe
            elif programme == "voluntary":
                df_source = self.butter_voluntary_dataframe
            else:
                df_source = self.butter_dataframe
        else:
            df_source = self.dataframe

        df = df_source[df_source["year"].isin(year_list)]
        df = df[df["origCountry"].isin(country_list)]
        df = df[df["resVal"] > 0]

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        result = pd.merge(
            df, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        result = (
            result.groupby(["origCountry", "tag"])["sampleId"]
            .nunique()
            .reset_index(name="sample_count")
        )
        result = result.sort_values(
            ["origCountry", "sample_count"], ascending=[True, False]
        ).reset_index(drop=True)

        total_samples_per_country = (
            df_source[
                df_source["origCountry"].isin(country_list)
                & df_source["year"].isin(year_list)
            ]
            .groupby("origCountry")["sampleId"]
            .nunique()
        )
        result["percentage"] = result.apply(
            lambda row: (
                row["sample_count"]
                / total_samples_per_country[row["origCountry"]]
            )
            * 100,
            axis=1,
        )
        result["percentage"] = result["percentage"].round(2)
        result = (
            result.groupby("origCountry").head(top_k).reset_index(drop=True)
        )
        return result

    # 8
    def voluntary_programmes_ranking(
        self, year_list, country_list, product, country_type, top_k=5
    ):
        if product == "milk":
            df = self.milk_voluntary_dataframe
        elif product == "butter":
            df = self.butter_voluntary_dataframe
        else:
            print("Wrong product.")
            return

        country = "origCountry" if country_type == "origin" else "sampCountry"

        df = df[~df["resVal"].isna()]
        df = (
            df.groupby(["year", country])["sampleId"]
            .nunique()
            .reset_index(name="positive_sample_count")
        )
        df = df.sort_values(
            ["year", "positive_sample_count"], ascending=[True, False]
        )
        return df

    def voluntary_sampling_stats(
        self, year_list, country_list, product, country_type, limits_path
    ):
        if product == "milk":
            df = self.milk_voluntary_dataframe
        elif product == "butter":
            df = self.butter_voluntary_dataframe
        else:
            print("Wrong product.")
            return

        country = "origCountry" if country_type == "origin" else "sampCountry"

        df = df[df["year"].isin(year_list)]
        df = df[df[country].isin(country_list)]

        # VAL > 0
        df1 = df[~df["resVal"].isna()]
        df1 = (
            df1.groupby(["year", country])["sampleId"]
            .nunique()
            .reset_index(name="VAL_samples")
        )

        # Limits exceeded
        df_limits = self._get_paramcodes_limits(path=limits_path)
        df_limits = df_limits[df_limits["limit"] >= 0]
        df2 = pd.merge(
            df,
            df_limits,
            left_on="pesticideCode",
            right_on="paramcode",
            how="left",
        ).fillna(0)
        df2["acceptable"] = df2["limit"] >= df2["resVal"]
        df2 = df2[df2["acceptable"] == False]
        df2 = (
            df2.groupby(["year", country])["sampleId"]
            .nunique()
            .reset_index(name="limit_samples")
        )

        # total samples
        df3 = (
            df.groupby(["year", country])["sampleId"]
            .nunique()
            .reset_index(name="total_samples")
        )

        res = pd.merge(df3, df1, on=["year", country], how="left").fillna(0)
        res = pd.merge(res, df2, on=["year", country], how="left").fillna(0)

        return res

    def additional_tests(
        self,
        year_list,
        product,
        paramcodes_path,
        top_k=None,
    ):
        if product == "milk":
            df = pd.concat(
                [
                    self.milk_obligatory_dataframe.assign(
                        prog_type="obligatory"
                    ),
                    self.milk_voluntary_dataframe.assign(prog_type="voluntary"),
                ],
                ignore_index=True,
            )
        elif product == "butter":
            df = pd.concat(
                [
                    self.butter_obligatory_dataframe.assign(
                        prog_type="obligatory"
                    ),
                    self.butter_voluntary_dataframe.assign(
                        prog_type="voluntary"
                    ),
                ],
                ignore_index=True,
            )

        df = df[df["year"].isin(year_list)]

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        df = pd.merge(
            df, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        df = df[df["mandatory"] == False]

        res = df.groupby(["paramcode", "tag", "long_name", "prog_type"])[
            "sampleId"
        ].nunique()

        if top_k:
            res = res[:top_k, :]

        res = res.reset_index().pivot_table(
            index=["paramcode", "tag", "long_name"],
            columns="prog_type",
            values="sampleId",
            fill_value=0,
        )
        res = res.reset_index()
        res["total_samples"] = res["obligatory"] + res["voluntary"]
        res = res.sort_values("total_samples", ascending=False)

        return res[
            [
                "paramcode",
                "tag",
                "long_name",
                "obligatory",
                "voluntary",
                "total_samples",
            ]
        ]

    def programmes_top_pesticides_comparison(
        self,
        year_list,
        product,
        paramcodes_path,
        top_k=10,
    ):
        if product == "milk":
            df_obligatory = self.milk_obligatory_dataframe
            df_voluntary = self.milk_voluntary_dataframe
        elif product == "butter":
            df_obligatory = self.butter_obligatory_dataframe
            df_voluntary = self.butter_voluntary_dataframe

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        df_obligatory = pd.merge(
            df_obligatory,
            df_names,
            left_on="pesticideCode",
            right_on="paramcode",
        )
        df_voluntary = pd.merge(
            df_voluntary,
            df_names,
            left_on="pesticideCode",
            right_on="paramcode",
        )

        df_obligatory = df_obligatory[
            (df_obligatory["resVal"] > 0)
            & (df_obligatory["resType"].isin(["LOQ", "VAL"]))
        ]
        df_obligatory = (
            df_obligatory.groupby(["tag"])["sampleId"].nunique().reset_index()
        )
        df_obligatory = df_obligatory.sort_values(
            "sampleId", ascending=False
        ).iloc[:top_k, :]

        df_voluntary = df_voluntary[
            (df_voluntary["resVal"] > 0)
            & (df_voluntary["resType"].isin(["LOQ", "VAL"]))
        ]
        df_voluntary = (
            df_voluntary.groupby(["tag"])["sampleId"].nunique().reset_index()
        )
        df_voluntary = df_voluntary.sort_values(
            "sampleId", ascending=False
        ).iloc[:top_k, :]

        return df_obligatory, df_voluntary

    # 17
    def country_year_pesticide_list_obligatory(
        self,
        year_list,
        country_list,
        paramcodes_path,
        product="milk",
        top_k=10,
        programme="obligatory",
        country="sampCountry",
    ):
        if product == "milk":
            if programme == "obligatory":
                df = self.milk_obligatory_dataframe.copy()
            elif programme == "voluntary":
                df = self.milk_voluntary_dataframe.copy()
            else:
                df = self.milk_dataframe
        elif product == "butter":
            if programme == "obligatory":
                df = self.butter_obligatory_dataframe.copy()
            elif programme == "voluntary":
                df = self.butter_voluntary_dataframe.copy()
            else:
                df = self.dataframe
        else:
            return 0

        df = df[df["year"].isin(year_list)]
        df = df[df[country].isin(country_list)]

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        df = pd.merge(
            df, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        # df total samples with this pesticide tested

        df_total = (
            df.groupby([country, "year", "tag"])["sampleId"]
            .nunique()
            .reset_index(name="num_samples")
        )

        # df mrl

        df_mrl = df[df["limit"] < df["resVal"]]
        df_mrl_1 = (
            df_mrl.groupby([country, "year", "tag"])["sampleId"]
            .nunique()
            .reset_index(name="above_mrl_samples")
        )
        df_mrl_2 = (
            df_mrl.groupby([country, "year", "tag"])["resVal"]
            .mean()
            .round(4)
            .reset_index(name="above_mrl_mean")
        )
        df_mrl_3 = (
            df_mrl.groupby([country, "year", "tag"])["resVal"]
            .std()
            .round(4)
            .reset_index(name="above_mrl_std")
        )

        # df val
        df_val = df[(df["limit"] >= df["resVal"]) & (df["resVal"] > 0)]
        df_val_1 = (
            df_val.groupby([country, "year", "tag"])["sampleId"]
            .nunique()
            .reset_index(name="between_loq_and_mrl_samples")
        )
        df_val_2 = (
            df_val.groupby([country, "year", "tag"])["resVal"]
            .mean()
            .round(4)
            .reset_index(name="between_loq_and_mrl_mean")
        )
        df_val_3 = (
            df_val.groupby([country, "year", "tag"])["resVal"]
            .std()
            .round(4)
            .reset_index(name="between_loq_and_mrl_std")
        )

        res = df_total.copy()
        res = res.merge(
            df_mrl_1, on=[country, "year", "tag"], how="left"
        ).fillna(0)
        res = res.merge(df_mrl_2, on=[country, "year", "tag"], how="left")
        res = res.merge(
            df_mrl_3, on=[country, "year", "tag"], how="left"
        ).fillna(0)
        res = res.merge(
            df_val_1, on=[country, "year", "tag"], how="left"
        ).fillna(0)
        res = res.merge(df_val_2, on=[country, "year", "tag"], how="left")
        res = res.merge(
            df_val_3, on=[country, "year", "tag"], how="left"
        ).fillna(0)

        res = res[
            (res["above_mrl_samples"] > 0)
            | (res["between_loq_and_mrl_samples"] > 0)
        ]

        res = res.sort_values(
            [country, "year", "num_samples"],
            ascending=[True, True, False],
        )
        # res = res.groupby([country, "year"]).head(top_k).reset_index(drop=True)
        return res

    def sample_contamination_summary(
        self, paramcodes_path, product="milk", country="origCountry"
    ):

        if product == "milk":
            df = self.milk_dataframe.copy()
        elif product == "butter":
            df = self.butter_dataframe.copy()
        else:
            df = self.dataframe.copy()

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        df = pd.merge(
            df, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        df = df[df["resVal"] > 0]
        # df = df[df["limit"] < df["resVal"]]

        return (
            df.groupby(country)["sampleId"]
            .nunique()
            .reset_index(name="total_samples")
        )

    def highest_levels_of_pesticides(
        self,
        pesticide_tag,
        paramcodes_path,
        product="milk",
        country="origCountry",
    ):
        if product == "milk":
            df = self.milk_dataframe.copy()
        elif product == "butter":
            df = self.butter_dataframe.copy()
        else:
            df = self.dataframe.copy()

        df_names = self._get_paramcodes_limits(path=paramcodes_path)
        df = pd.merge(
            df, df_names, left_on="pesticideCode", right_on="paramcode"
        )

        df = df[(df["tag"] == pesticide_tag) & (~df["resVal"].isna())]

        result = df.groupby("year")["resVal"].idxmax()
        return df.loc[result, ["year", country, "resVal"]].reset_index(
            drop=True
        )

    def _get_paramcodes_limits(self, path: str):
        paramcodes = pd.read_csv(path)

        paramcodes["limit"] = paramcodes["limit"].replace("brak", 0.0)
        paramcodes["limit"] = pd.to_numeric(
            paramcodes["limit"], errors="coerce"
        ).fillna(-1)
        paramcodes = paramcodes[
            [
                "tag",
                "short_name",
                "long_name",
                "paramcode",
                "limit",
                "mandatory",
            ]
        ]
        return paramcodes
