import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

#Read CSV
data = pd.read_csv("https://raw.githubusercontent.com/bajasiagian/cc_aproval_project/master/dataset/data.csv")
p = data[data.is_high_risk==0]
print(p.cluster.unique())

count_rec = pd.read_csv("https://raw.githubusercontent.com/bajasiagian/cc_aproval_project/master/dataset/credit_record.csv")
credit_record = pd.read_csv("https://raw.githubusercontent.com/bajasiagian/cc_aproval_project/master/dataset/credit_record_raw.csv")

#Color Dictionary
def get_color(group):
    color_dict = {'0-0':'#636EFA',
                  '1-0':'#EF553B',
                  '2-0':'#00CC96',
                  '0-1':'#AB63FA',
                  '1-1':'#FFA15A',
                  '2-1':'#19D3F3'}
    return(color_dict[group])

#Polar Graph
def get_polar(group):
    count_rec['group'] = count_rec['cluster'].astype(str)+'-'+count_rec['is_high_risk'].astype(str)
    df = count_rec.copy()
    df = df[df['group']==group]

    df1=df.drop(columns=['ID','0','1','2','3','4','5','X','C','%hr','Account Age']).groupby(["cluster","is_high_risk"]).mean().reset_index() #taking mean percentage of each status in cluster
    df2=df[['is_high_risk','cluster','Account Age']].groupby(["cluster","is_high_risk"]).median().reset_index() #taking median of the activities of each status in clusters
    temp_polar = pd.merge(df2,df1,how='inner',on=['cluster','is_high_risk'])

    polar=pd.melt(temp_polar,id_vars=["cluster","is_high_risk"])
    polar['group'] = polar['cluster'].astype(str)+'-'+polar['is_high_risk'].astype(str)
    polar = polar.drop(columns=['cluster','is_high_risk'])

    fig = px.line_polar(polar, r="value",
                        theta="variable",
                        line_close=True,
                        range_r= [-10,100],
                        height=500,width=500,
                        template='ggplot2',
                        color_discrete_sequence=[get_color(group)])
    fig.update_layout(showlegend=False)

    return fig

#Vintage Analysis
#Data Preparation
def df_result(cluster,command):
  credit =  pd.merge(credit_record,count_rec[['ID','cluster']],how='left',on='ID').dropna().reset_index(drop=True)
  credit = credit[credit.cluster==cluster]
  grouped = credit.groupby('ID')

  ### convert credit data to wide format which every ID is a row
  pivot_tb = pd.DataFrame({'open_month':grouped['MONTHS_BALANCE'].min(),'end_month':grouped['MONTHS_BALANCE'].max()}).reset_index()
  pivot_tb['window'] = pivot_tb['end_month'] - pivot_tb['open_month'] # calculate observe window

  credit = pd.merge(credit, pivot_tb, on = 'ID', how = 'left') # join calculated information

  credit['status'] = np.where((credit['STATUS'] == '2') | (credit['STATUS'] == '3' )| (credit['STATUS'] == '4' )| (credit['STATUS'] == '5'), 1, 0) # analyze > 60 days past due

  credit['month_on_book'] = credit['MONTHS_BALANCE'] - credit['open_month'] # calculate month on book: how many months after opening account
  credit.sort_values(by = ['ID','month_on_book'], inplace = True)

  #Create due rate
  id_sum = len(set(pivot_tb['ID']))
  credit['status'] = 0
  exec(command)

  credit['month_on_book'] = credit['MONTHS_BALANCE'] - credit['open_month']
  minagg = credit[credit['status'] == 1].groupby('ID')['month_on_book'].min()
  minagg = pd.DataFrame(minagg)
  minagg['ID'] = minagg.index
  obslst = pd.DataFrame({'month_on_book':range(0,61), 'rate': None})

  lst = []
  for i in range(0,61):
    due = list(minagg[minagg['month_on_book']  == i]['ID'])
    lst.extend(due)
    obslst.loc[obslst['month_on_book'] == i, 'rate'] = len(set(lst)) / id_sum

  rate = obslst['rate']

  return credit,rate

#Assigning bad credit
command1 = "credit.loc[(credit['STATUS'] == '0') | (credit['STATUS'] == '1') | (credit['STATUS'] == '2') | (credit['STATUS'] == '3' )| (credit['STATUS'] == '4' )| (credit['STATUS'] == '5'), 'status'] = 1"
command2 = "credit.loc[(credit['STATUS'] == '1') | (credit['STATUS'] == '2') | (credit['STATUS'] == '3' )| (credit['STATUS'] == '4' )| (credit['STATUS'] == '5'), 'status'] = 1"
command3 = "credit.loc[(credit['STATUS'] == '2') | (credit['STATUS'] == '3' )| (credit['STATUS'] == '4' )| (credit['STATUS'] == '5'), 'status'] = 1"
command4 = "credit.loc[(credit['STATUS'] == '3' )| (credit['STATUS'] == '4' )| (credit['STATUS'] == '5'), 'status'] = 1"
command5 = "credit.loc[(credit['STATUS'] == '4' )| (credit['STATUS'] == '5'), 'status'] = 1"
command6 = "credit.loc[(credit['STATUS'] == '5'), 'status'] = 1"

_,rate1_0 = df_result(0,command1)
_,rate2_0 = df_result(0,command2)
_,rate3_0 = df_result(0,command3)
_,rate4_0 = df_result(0,command4)
_,rate5_0 = df_result(0,command5)
_,rate6_0 = df_result(0,command6)

_,rate1_1 = df_result(1,command1)
_,rate2_1 = df_result(1,command2)
_,rate3_1 = df_result(1,command3)
_,rate4_1 = df_result(1,command4)
_,rate5_1 = df_result(1,command5)
_,rate6_1 = df_result(1,command6)

_,rate1_2 = df_result(2,command1)
_,rate2_2 = df_result(2,command2)
_,rate3_2 = df_result(2,command3)
_,rate4_2 = df_result(2,command4)
_,rate5_2 = df_result(2,command5)
_,rate6_2 = df_result(2,command6)

obslst_clust_0 = pd.DataFrame({'Past due more than 30 days': rate2_0,
                               'Past due more than 60 days': rate3_0,
                               'Past due more than 90 days': rate4_0,
                               'Past due more than 120 days': rate5_0,
                               'Past due more than 150 days': rate6_0
                              })
obslst_clust_1 = pd.DataFrame({'Past due more than 30 days': rate2_1,
                               'Past due more than 60 days': rate3_1,
                               'Past due more than 90 days': rate4_1,
                               'Past due more than 120 days': rate5_1,
                               'Past due more than 150 days': rate6_1
                              })
obslst_clust_2 = pd.DataFrame({'Past due more than 30 days': rate2_2,
                               'Past due more than 60 days': rate3_2,
                               'Past due more than 90 days': rate4_2,
                               'Past due more than 120 days': rate5_2,
                               'Past due more than 150 days': rate6_2
                              })

#Vintage Graph
def get_df_cluster(cluster):
   df_dict = {0:obslst_clust_0,
              1:obslst_clust_1,
              2:obslst_clust_2
              }
   
   return df_dict[cluster]

def get_vintage_fig(cluster):
  df = get_df_cluster(cluster)
  fig = go.Figure()
  for col in df.columns:
    fig.add_trace(go.Scatter(x=np.arange(0,61),y=df[col],name=col))
  fig.update_layout(height=500,width=650)
  
  fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ))
  return fig

#Box Plot
def get_box_plot(high_low,var):
    df = data[data.is_high_risk==high_low]

    fig = go.Figure()
    for cluster in [0,1,2]:
        fig.add_trace(go.Box(y=df[df.cluster==cluster][var], name='User Group '+str(cluster)))
    fig.update_layout(showlegend=False,
                      height=500,width=500,)
    
    return fig
#Histogram
def df_to_read():
    temp_df = data.copy()
    temp_df.rename(columns=
                    {
                        'gender':'Gender',
                        'employment_status':'Employment Status',
                        'has_a_car':'Has a Car',
                        'has_a_property':'Has a Property',
                        'marital_status':'Marital Status',
                    }
    ,inplace=True)
    
    temp_df['Gender'] = np.where(temp_df['Gender']=='M','Male','Female')
    temp_df['Has a Car'] = np.where(temp_df['Has a Car']=='Y','Yes','No')
    temp_df['Has a Property'] = np.where(temp_df['Has a Property']=='Y','Yes','No')
    
    return temp_df



def get_histogram(high_low,var):
   df = df_to_read()[df_to_read().is_high_risk==high_low]
   df['cluster'] = np.where(df.cluster==0,'User Group 0',np.where(df.cluster==1,'User Group 1','User Group 2'))
   
   fig = go.Figure()
   for col in df[var].unique():
      fig.add_trace(go.Histogram(x=df[df[var]==col]['cluster'],name=col))
      
   fig.update_layout(title=var)

   return fig