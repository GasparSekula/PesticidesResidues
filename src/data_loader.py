import os
import pandas as pd

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
    def load_dataset_new(self, country: str, year: int, dest_dir: str, save: bool = True):
        path = os.path.join(self.data_dir, f'MOPER_ALL_DATA_SSD2_{year}_{country}.csv')
        df = pd.read_csv(path)
        df_selected = df[['sampId_A', 'sampMatCode.base.building', 'paramCode.base.param', 'origCountry', 'sampCountry', 'resType', 'resVal', 'progType']]
        df_filtered = df_selected[((df_selected['sampMatCode.base.building'] == 'A039C') | (df_selected['sampMatCode.base.building'].str.contains('A02L.*')))]
        df_filtered = df_filtered[df_filtered['progType'].isin(['K005A', 'K009A', 'K018A'])]
        df_renamed = df_filtered.rename(columns = {'sampMatCode.base.building' : 'productCode',
                                                   'paramCode.base.param' : 'pesticideCode',
                                                   'sampId_A' : 'sampleId'})
        df_renamed.reset_index()
        
        if save:
            df_renamed.to_pickle(f'{dest_dir}/cleaned_{year}_{country}.pkl')
        else:
            return df_renamed
        
    def load_dataset_old(self, country: str, year: int, dest_dir: str, save: bool = True):
        path = os.path.join(self.data_dir, f'MOPER_ALL_DATA_{year}_{country}.csv')
        df = pd.read_csv(path)
        df_selected = df[['LABSAMPCODE_A', 'SAMPCOUNTRY','ORIGCOUNTRY', 'PRODCODE', 'EFSAPRODCODE', 'PRODTREAT', 'PROGTYPE', 'PARAMCODE', 'RESVAL', 'FATPERC', 'RESTYPE']]
        df_filtered = df_selected[df_selected['PRODCODE'].isin(['P1020000A', 'P1020010A'])]
        df_filtered = df_filtered[df_filtered['PROGTYPE'].isin(['K005A', 'K009A', 'K018A'])]
        df_filtered = df_filtered[df_filtered['PRODTREAT'].isin(['T134A', 'T150A', 'T152A', 'T999A'])]
        df_renamed = df_filtered.rename(columns = {'LABSAMPCODE_A' : 'sampleId', 
                                                   'SAMPCOUNTRY' : 'sampCountry',
                                                   'ORIGCOUNTRY' : 'origCountry', 
                                                   'PRODCODE' : 'productCode', 
                                                   'EFSAPRODCODE' : 'efsaProductCode', 
                                                   'PRODTREAT' : 'productTreat', 
                                                   'PROGTYPE' : 'progType', 
                                                   'PARAMCODE' : 'pesticideCode', 
                                                   'RESVAL' : 'resVal', 
                                                   'FATPERC' : 'fatPerc', 
                                                   'RESTYPE' : 'resType'
        })
        
        df_renamed.reset_index()
        
        if save:
            df_renamed.to_pickle(f'{dest_dir}/cleaned_{year}_{country}.pkl')
        else:
            return df_renamed
    
    def load_all_datasets(self, country_list: list, year_list: list, exceptions_list: list[tuple], dest_dir: str):
        for country in country_list:
            for year in year_list:
                if year <= 2018:
                    if (country, year) not in exceptions_list:
                        self.load_dataset_old(country=country, year=year, dest_dir=dest_dir)
                else:
                    if (country, year) not in exceptions_list:
                        self.load_dataset_new(country=country, year=year, dest_dir=dest_dir)
            print(f'Loading data for {country} completed.')
            
    def concat_datasets(self, country_list: list, year_list: list, orig_dir: str, exceptions_list: list[tuple], dest_dir: str):
        all_dfs = []
        for year in year_list:
            for country in country_list:
                if (country, year) not in exceptions_list:
                    df = pd.read_pickle(f'{orig_dir}/cleaned_{year}_{country}.pkl')
                    df['year'] = year
                    all_dfs.append(df)
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_pickle(f'{dest_dir}/final_dataset.pkl')
        print('All datasets concatenated and saved.')