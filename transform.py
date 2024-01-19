import numpy as np
import pandas as pd

def user_input_features(data):
    features = pd.DataFrame(data, index=[0])
    
    features.rename(columns=
                    {
                        'Gender':'gender',
                        'Age':'age',
                        'Employment Status':'employment_status',
                        'Employment Length':'employment_length',
                        'Income':'income',
                        'Has a Car':'has_a_car',
                        'Has a Property':'has_a_property',
                        'Marital Status':'marital_status',
                        'Children Count':'children_count',
                        'Family Member Count':'family_member_count'
                    }
    ,inplace=True)
    
    features['gender'] = np.where(features['gender']=='Male','M','F')
    features['has_a_car'] = np.where(features['has_a_car']=='Yes','Y','N')
    features['has_a_property'] = np.where(features['has_a_property']=='Yes','Y','N')
    
    return features

def get_dummies(df):
    data = pd.DataFrame(
        {
            'age':df.age,
            'employment_length':df.employment_length,
            'income':df.income,
            'children_count':df.children_count,
            'family_member_count':df.family_member_count,
            'gender_M':np.where(df.gender=='M',1,0),
            'has_a_car_Y':np.where(df.has_a_car=='Y',1,0),
            'has_a_property_Y':np.where(df.has_a_property=='Y',1,0),
            'employment_status_Pensioner':np.where(df.employment_status=='Pensioner',1,0),
            'employment_status_State servant':np.where(df.employment_status=='State servant',1,0),
            'employment_status_Student':np.where(df.employment_status=='Student',1,0),
            'employment_status_Working':np.where(df.employment_status=='Working',1,0),
            'marital_status_Married':np.where(df.marital_status=='Married',1,0),
            'marital_status_Separated':np.where(df.marital_status=='Separated',1,0),
            'marital_status_Single / not married':np.where(df.marital_status=='Single / not married',1,0),
            'marital_status_Widow':np.where(df.marital_status=='Widow',1,0)
        }
    )

    return data

