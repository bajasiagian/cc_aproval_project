import streamlit as st
import numpy as np
import pandas as pd
from pycaret.classification import load_model
from pycaret.classification import predict_model
from htbuilder import HtmlElement, div, br, hr, a, img, styles, classes, fonts
from htbuilder import p as P
from htbuilder.units import percent
from htbuilder.units import px as pix
from transform import *
from graph import *

st.set_page_config(layout="wide", initial_sidebar_state='expanded',page_title="Credit Approval App")

###-----------------------------------------------------------------------------------------------------------###
#Sidebar Menu
st.sidebar.header('Input User Personal Information')
with st.sidebar.form("my_form"):
  gender = st.selectbox('Gender', ['Male','Female'])
  age = st.slider('Age',18,70,30)

  employment_status = st.selectbox('Employment Status', ['Working', 'Commercial associate', 'Pensioner', 'State servant', 'Student'])
  employment_length = st.slider('Employment Length',0,60,10)
  income = st.number_input('Anual Income',step=1000,min_value=25000,placeholder='Annual Income')
  has_a_car = st.selectbox('Has a Car', ['Yes','No'])
  has_a_property = st.selectbox('Has a Property', ['Yes','No'])

  marital_status = st.selectbox('Marital Status', ['Married', 'Single / not married', 'Separated', 'Civil marriage', 'Widow'])
  children_count = st.slider('Children Count',0,20)
  family_member_count = st.slider('Family Member Count',0,20,4)

  submitted = st.form_submit_button(label="Submit")
  if submitted == True:
    data = {'Gender':gender,
          'Age':age,
          'Employment Status':employment_status,
          'Employment Length':employment_length,
          'Income':income,
          'Has a Car':has_a_car,
          'Has a Property':has_a_property,
          'Marital Status':marital_status,
          'Children Count':children_count,
          'Family Member Count':family_member_count}
  else:
    data = {'Gender':'Male',
          'Age':18,
          'Employment Status':'Working',
          'Employment Length':18,
          'Income':10000,
          'Has a Car':'Yes',
          'Has a Property':'Yes',
          'Marital Status':'Married',
          'Children Count':0,
          'Family Member Count':2}
    
#Compile User Information
user_feature = user_input_features(data)

###-----------------------------------------------------------------------------------------------------------###
#Main Dashboard
st.write("# Credit Approval and Payment Behavior Prediction :credit_card:")

###--------------------------Prediction Part--------------------------###
#Row A
st.header('User Information')
st.dataframe(pd.DataFrame(data,index=[0]),hide_index=True)

#Data Engineering
X = get_dummies(user_feature)

#Predict High Risk
high_risk_clf = load_model("high_risk_prediction")
pred_high_risk = predict_model(high_risk_clf, data=X)

pred_label = pred_high_risk.prediction_label[0]
pred_category = 'high' if pred_high_risk.prediction_label[0]==1 else 'low'
pred_emoji = ':x:' if pred_high_risk.prediction_label[0]==1 else':white_check_mark:'
pred_score = round(pred_high_risk.prediction_score[0]*100,4)

st.markdown(f"### Based on this information, this user having *{pred_category} risk* to default {pred_emoji}")
st.markdown(f"#### With {pred_score}% confidence ")

#Append High Risk Result
X['is_high_risk_1'] = np.where(pred_label == 1,1,0)
#Predict CLuster
cluster_clf = load_model("cluster_prediction")
pred_cluster = predict_model(cluster_clf, data=X)

pred_label_cluster = pred_cluster.prediction_label[0]
pred_score_cluster = pred_cluster.prediction_score[0]

#User Group
group = pred_label_cluster.astype(str)+'-'+pred_label.astype(str)

###------------------------Result Graph Part------------------------###
#Graph
vintage, polar = st.columns((6,4))
with vintage:
  st.markdown('##### Vintage Analysis from Similar Past User Group')
  st.plotly_chart(get_vintage_fig(pred_label_cluster),use_container_width=True)
with polar:
  st.markdown('##### Similar Past User Credit Pattern')
  st.plotly_chart(get_polar(group),use_container_width=True)

st.write(f"We're segmenting the past user into 3 groups, and this user with provided information most likely belongs to `group {pred_label_cluster} with {pred_category} probability to default`, other groups properties can be compared from graph below")

###--------------------------Comparison Part--------------------------###
#Comparison
st.header('Comparison Between Groups')

option = st.selectbox("Choose User Risk",
                      ("Low Risk User","High Risk User"))
picker = 0 if option == 'Low Risk User' else 1

#Box Plot
st.markdown('#### Numeric Variable Comparison')
box1,box2,box3,box4,box5 = st.columns((2.5,2.5,2.5,2.5,2.5))
with box1:
  st.markdown('##### Income')
  st.plotly_chart(get_box_plot(picker,'income'),use_container_width=True)
with box2:
  st.markdown('##### Children Count')
  st.plotly_chart(get_box_plot(picker,'children_count'),use_container_width=True)
with box3:
  st.markdown('##### Family Count')
  st.plotly_chart(get_box_plot(picker,'family_member_count'),use_container_width=True)
with box4:
  st.markdown('##### Age')
  st.plotly_chart(get_box_plot(picker,'age'),use_container_width=True)
with box5:
  st.markdown('##### Employment Length')
  st.plotly_chart(get_box_plot(picker,'employment_length'),use_container_width=True)

#Histogram Plot
st.markdown('#### Categoric Variable Comparison')
options = st.multiselect('Choose Variable',
                         ['Gender','Employment Status','Has a Car','Has a Property','Marital Status'],
                         ['Gender','Employment Status']
                         )
for var in list(options):
  st.plotly_chart(get_histogram(picker,var),use_container_width=True)

###--------------------------Footer Part--------------------------###
#Footer


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style), _class='small-image')


def link(link, text, **style):
    return a(href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility:hidden;}
     .stApp { bottom: 80px;}
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=pix(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height=10,
        opacity=1
    )

    body = P()
    foot = div(
        style=style_div
    )(
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        "Made with ❤️ by Baja Stephanus RS",
        br(),
        link("https://www.kaggle.com/bajasiagian/code", image('https://storage.scolary.com/storage/file/public/71b68248-ba0a-4b26-b15f-0c77cdf341cd.svg',width=pix(25), height=pix(25))),
        "                                                                                                ",
        link("https://www.linkedin.com/in/bajastephanus/", image('https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/LinkedIn_icon.svg/2048px-LinkedIn_icon.svg.png',width=pix(25), height=pix(25))),
    ]
    layout(*myargs)
footer()