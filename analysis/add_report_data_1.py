import pandas as pd 

def insert_row(df: pd.DataFrame, values: tuple, year: int):
    country, limit, unique_sample_count = values
    
    success = limit <= unique_sample_count
    obligaotry_samples = unique_sample_count
    voluntary_samples = 0
    obligatory_success = success

    new_row = pd.DataFrame([{
        'country': country,
        'year': year,
        'limit': limit,
        'unique_sample_count': unique_sample_count,
        'success': success,
        'obligaotry_samples': obligaotry_samples,
        'voluntary_samples': voluntary_samples,
        'obligatory_success': obligatory_success
    }], columns=df.columns)
    
    return pd.concat([df, new_row], ignore_index=True)

if __name__ == '__main__':
    butter_df = pd.read_csv('../results/results_v4/1_samples_count_butter_v4.csv')
    milk_df = pd.read_csv('../results/results_v4/1_samples_count_milk_v4.csv')
    
    values_list_butter = [
        ('AT', 12, 14),
        ('BE', 12, 15),
        ('BG', 12, 0),
        ('CY', 12, 4),
        ('CZ', 12, 15),
        ('DK', 12, 0),
        ('EE', 12, 15),
        ('FI', 12, 0),
        ('FR', 66, 0),
        ('DE', 93, 68),
        ('GR', 12, 16), 
        ('HU', 12, 0),
        ('IS', 0, 0),
        ('IE', 12, 15),
        ('IT', 65, 5),
        ('LV', 12, 14),
        ('LT', 12, 16),
        ('LU', 12, 0),
        ('MT', 12, 15),
        ('NL', 17, 24),
        ('NO', 0, 0),
        ('PL', 45, 50),
        ('PT', 12, 0),
        ('RO', 17, 0),
        ('SK', 12, 15),
        ('SI', 12, 15), 
        ('ES', 45, 21),
        ('SE', 12, 27),
        ('GB', 66, 109)
    ]
    
    values_list_milk = [
        ('AT', 12, 17),
        ('BE', 12, 15),
        ('BG', 12, 0),
        ('CY', 12, 5),
        ('CZ', 12, 0),
        ('DK', 12, 15),
        ('EE', 12, 15),
        ('FI', 12, 16),
        ('FR', 66, 0),
        ('DE', 93, 94),
        ('GR', 12, 0), 
        ('HU', 12, 0),
        ('IS', 0, 0),
        ('IE', 12, 68),
        ('IT', 65, 0),
        ('LV', 12, 8),
        ('LT', 12, 10),
        ('LU', 12, 18),
        ('MT', 12, 0),
        ('NL', 17, 22),
        ('NO', 0, 15),
        ('PL', 45, 1),
        ('PT', 12, 0),
        ('RO', 17, 38),
        ('SK', 12, 15),
        ('SI', 12, 1), 
        ('ES', 45, 16),
        ('SE', 12, 30),
        ('GB', 66, 235)
    ]
    
    for v in values_list_butter:
        butter_df = insert_row(df=butter_df, values=v, year=2009)
        
    for v in values_list_milk:
        milk_df = insert_row(df=milk_df, values=v, year=2010)
        
    butter_df.to_csv('../results/results/1_samples_count_butter.csv')
    milk_df.to_csv('../results/results/1_samples_count_milk.csv')
    
    