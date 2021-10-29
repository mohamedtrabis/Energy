import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# import pickle
from PIL import Image
from IPython.core.display import display, HTML
from pandas.util._validators import validate_ascending

from streamlit_folium import folium_static
import folium
from folium import plugins

import seaborn as sns

import pickle

from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder

st.set_page_config(
    page_title="Seattle Energy",
    layout="wide",
    initial_sidebar_state="expanded",
)

col17, col18, col19 = st.columns([4 , 8 , 4 ])

with col18:
    image = Image.open("images/seattle.png")
    st.image(image, '')

st.write("------------------------------------------------------------------------------------------------------")

# Create a page dropdown
page = st.sidebar.radio("Choisissez votre Application",
                        ["Analyse Exploratoire", "Map - Cluster", "Prédiction Energie"])

# importer la base de données
df_15_16 = pd.read_csv('energy.csv')


if page == "Prédiction Energie":
    # Collecter le profil d'entrée
    st.sidebar.header("Les caractéristiques")


    # --------------------------------------------------------------------------------------------------------------------
    def energy_caract_entree():
        PrimaryPropertyType = st.sidebar.selectbox('Batiment Type', ('Hotel', 'Other', 'Store', 'Education', 'Office',
                                                                     'Warehouse', 'Residence', 'Health', 'Restaurant'))

        Electricity = st.sidebar.number_input("Electricity (max : 55835740)", 0, 55835740, 55835740)
        SourceEUI = st.sidebar.slider('SourceEUI(kBtu/sf)', 0, 2620, 2620)
        YearBuilt = st.sidebar.slider('YearBuilt', 1900, 2015, 2015)
        TotalGHGEmissions = st.sidebar.slider('TotalGHGEmissions', 0, 1936, 1936)
        PropertyGFATotal = st.sidebar.number_input("PropertyGFATotal (max : 1605578)", 11285, 1605578, 1605578)
        PropertyGFABuilding = st.sidebar.number_input('PropertyGFABuilding (max : 1592914)', 3636, 1592914, 61320)
        SteamUse = st.sidebar.number_input("SteamUse(kBtu) (max : 16284570)", 0, 23458518, 23458518)

        data = {
            'PrimaryPropertyType': PrimaryPropertyType,
            'Electricity(kBtu)': Electricity,
            'SourceEUI(kBtu/sf)': SourceEUI,
            'YearBuilt': YearBuilt,
            'TotalGHGEmissions': TotalGHGEmissions,
            'PropertyGFATotal': PropertyGFATotal,
            'PropertyGFABuilding(s)': PropertyGFABuilding,
            'SteamUse(kBtu)': SteamUse,
        }

        energy_features = pd.DataFrame(data, index=[0])
        return energy_features


    # --------------------------------------------------------------------------------------------------------------------

    input_df = energy_caract_entree()

    columns = ['PrimaryPropertyType', 'Electricity(kBtu)', 'SteamUse(kBtu)', 'SourceEUI(kBtu/sf)',
               'YearBuilt', 'TotalGHGEmissions', 'PropertyGFATotal', 'PropertyGFABuilding(s)']

    donnee_entree = pd.concat([input_df, df_15_16[columns]])

    donnee_entree = donnee_entree[:1]

    st.write("""
    <style>

    table {
    font-size:13px !important;
    border:3px solid #6495ed;
    border-collapse:collapse;
    /*margin:auto;*/
    }

    th {
    font-family:monospace bold;
    border:1px dotted #6495ed;
    background-color:#EFF6FF;
    text-align:center;
    }
    td {
    font-family:sans-serif;
    font-size:95%;
    border:1px solid #6495ed;
    text-align:left;
    width:auto;
    }

    .url {
      transition: transform .2s; /* Animation */
      margin: 0 auto;
    }

    .url:hover {
      transform: scale(3); /* (300% zoom - Note: if the zoom is too large, it will go outside of the viewport) */
    }

    </style>
    </style>
    """, unsafe_allow_html=True)

    df_encoder = pd.DataFrame(donnee_entree)

    le = LabelEncoder()

    # df_encoder['PrimaryPropertyType'] = le.inverse_transform(donnee_entree['PrimaryPropertyType'])

    # df_encoder.fillna(value=0, inplace=True)
    pd.options.display.float_format = "{:,.2f}".format

    st.header("L'application pour prédire la consomation annulle d'énergie\n")

    # afficher les données transformées
    st.subheader('Les caracteristiques transformées')

    st.write(HTML(df_encoder.to_html(escape=False, index=False)), unsafe_allow_html=True)

    df_encoder['PrimaryPropertyType'] = le.fit_transform(donnee_entree['PrimaryPropertyType'])

    # importer le modèle
    model = pickle.load(open('model.sav', 'rb'))

    # appliquer le modèle sur le profil d'entrée
    prevision = model.predict(df_encoder)

    st.subheader('')
    st.subheader('Résultat de la prévision')
    prevision = pd.DataFrame(prevision)

    prevision = prevision

    # st.write(prevision[0][0])
    prevision.rename(columns={0: "Prévision de la quantité annuelle d'énergie consommée (kBtu)"}, inplace=True)

    st.write(HTML(prevision.to_html(escape=False, index=False)), unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------------------------------------------------------------------
if page == "Map - Cluster":


    col39, col40 = st.columns([2, 8])

    with col39:
        categorie = st.selectbox('Type du Batiment', ('Hotel', 'Other', 'Store', 'Education', 'Office',
                                                      'Warehouse', 'Residence', 'Health', 'Restaurant', 'All'))
        cluster = st.selectbox('Cluster', ('TotalGHGEmissions', 'SiteEnergyUse(kBtu)' , 'Electricity(kBtu)'))


    st.subheader("L'emplacement des bâtiments de type : "+ categorie + " (Heatmap : "  + cluster +")" )

    df_geo = pd.DataFrame(df_15_16)

    df_geo['energy_grad'] = ''


    def energy_grad(df):

        df.loc[df.eval("ENERGYSTARScore <= 20"), "energy_grad"] = "D"
        df.loc[df.eval("ENERGYSTARScore > 20"), "energy_grad"] = "C"
        df.loc[df.eval("ENERGYSTARScore > 40"), "energy_grad"] = "B"
        df.loc[df.eval("ENERGYSTARScore > 60"), "energy_grad"] = "A"
        df.loc[df.eval("ENERGYSTARScore > 80"), "energy_grad"] = "A+"


    energy_grad(df_geo)


    def couleur(val):
        if val == 'A+':
            return 'darkgreen'

        if val == 'A':
            return 'green'

        if val == 'B':
            return 'lightgreen'

        if val == 'C':
            return 'orange'

        if val == 'D':
            return 'red'

        else:
            return 'black'


    def icon_funct(val):
        if val >= 50:
            return 'thumbs-up'

        if val < 50:
            return 'thumbs-down'

        else:
            return 'remove-sign'

    #Fonction folium marker
    def repere_geo(df, map):

        for index, row in df.iterrows():
            popup = (df['PrimaryPropertyType'][index] + ' : </br>' +
                     df['PropertyName'][index]) + '</br>' + '_____________________________' + '</br>' + \
                    'Address :' + '</br>' + (
                        df['full_address'][index]) + '</br>' + '_____________________________' + '</br>' + \
                    'ENERGY STAR Score : ' + '</br>' + str(df['ENERGYSTARScore'][index]) + '</br>' + '_____________________________' + '</br>' + \
                    'Site Energy Use : ' + '</br>' + str('{0:,}'.format(df['SiteEnergyUse(kBtu)'][index]))

            folium.Marker(location=(row['Latitude'], row['Longitude']),
                          icon=folium.Icon(color=couleur(df['energy_grad'][index]),
                                           icon=icon_funct(df['ENERGYSTARScore'][index])),
                          popup=popup).add_to(map)


    colonne_geo = ['OSEBuildingID', 'PropertyName', 'PrimaryPropertyType', 'DataYear', 'Electricity(kBtu)',
                    'SourceEUI(kBtu/sf)','YearBuilt', 'TotalGHGEmissions', 'PropertyGFATotal',
                    'PropertyGFABuilding(s)', 'PropertyGFAParking', 'SteamUse(kBtu)', 'SiteEnergyUse(kBtu)','Address', 'City',
                    'State','full_address', 'ENERGYSTARScore','Latitude','Longitude', 'energy_grad', 'SiteEUI(kBtu/sf)']

    df_geo = pd.DataFrame(df_15_16[colonne_geo])

    df_geo['full_address'] = df_geo.Address + "," + df_geo.City + "," + df_geo.State
    df_geo = df_geo.sort_values(by=['OSEBuildingID', 'DataYear'], ascending=False)
    df_geo.drop_duplicates(subset="OSEBuildingID", keep='first', inplace=True)

    if categorie != 'All':
        df_geo = df_geo[df_geo['PrimaryPropertyType'] == categorie]
    else:
        df_geo = pd.DataFrame(df_15_16[colonne_geo])
        df_geo['full_address'] = df_geo.Address + "," + df_geo.City + "," + df_geo.State
        df_geo = df_geo.sort_values(by=['OSEBuildingID', 'DataYear'], ascending=False)
        df_geo.drop_duplicates(subset="OSEBuildingID", keep='first', inplace=True)

    mapa = folium.Map(location=(47.62322, -122.320277), zoom_start=11, control_scale=True, prefer_canvas=True)


    # Ajout de plugins---------------------------------------------

    # Barre color map
    # colormap = folium.branca.colormap.linear.YlOrRd_09.scale(0, 8500)
    # colormap = colormap.to_step(index=[0, 1000, 3000, 5000, 8500])
    colormap = folium.branca.colormap.LinearColormap(colors=['blue', 'green', 'orange', 'red'],
                                                     vmin=df_geo[cluster].min(),
                                                     vmax=df_geo[cluster].max())

    colormap.caption = cluster
    colormap.add_to(mapa)

    draw = plugins.Draw(export=False)
    draw.add_to(mapa)

    plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(mapa)

    minimap = plugins.MiniMap()
    mapa.add_child(minimap)

    data = (np.random.normal(size=(100, 3)) * np.array([[1, 1, 1]]) + np.array([[48, 5, 1]])).tolist()
    plugins.HeatMap(data).add_to(mapa)

    # Adds tool to the top right
    from folium.plugins import MeasureControl

    mapa.add_child(MeasureControl())

    # List comprehension to make out list of lists
    # Plot it on the map
    from folium.plugins import HeatMap

    # List comprehension to make out list of lists

    # df_geo['ENERGYSTARScore'].fillna(value = 0, inplace=True)
    # create heatmap layer
    heatmap = HeatMap(list(zip(df_geo['Latitude'], df_geo['Longitude'], df_geo[cluster])),
                      min_opacity=0.2,
                      max_val=df_geo[cluster].max(),
                      radius=40,
                      # blur=40,
                      gradient={'0': 'blue', '0.25': 'green', '0.5': 'green', '0.75': 'orange', '1': 'Red'},
                      max_zoom=10,
                      )

    # Create a layer control object and add it to our map instance
    #folium.LayerControl().add_to(mapa)

    # add heatmap layer to base map
    heatmap.add_to(mapa)
    # Fin plugins---------------------------------------------------

    repere_geo(df_geo, mapa)
    with col40:
        folium_static(mapa, width=830, height=600)
    # Fin Map Mapa----------------------------------------------------------------------------------------------------------------

    # Map cluster-------------------------------------------------------------------------------------------------------
    st.write('_________________________________________________________________________________________________________')

    col20, col21, col22 = st.columns([1/3, 1/3, 1/3])
    with col20:
        cluster2 = st.selectbox('Cluster Map', ('TotalGHGEmissions', 'SiteEnergyUse(kBtu)', 'Electricity(kBtu)',
                                                'PropertyGFATotal', 'PropertyGFAParking','SiteEUI(kBtu/sf)'))

    st.subheader('Map Cluster : ' + cluster2)

    df_geo2 = pd.DataFrame(df_15_16[colonne_geo])
    df_geo2['full_address'] = df_geo2.Address + "," + df_geo2.City + "," + df_geo2.State
    df_geo2 = df_geo2.sort_values(by=['OSEBuildingID', 'DataYear'], ascending=False)
    df_geo2.drop_duplicates(subset="OSEBuildingID", keep='first', inplace=True)

    mapa2 = folium.Map(location=(47.62322, -122.320277), zoom_start=11, control_scale=True, prefer_canvas=True)

    marker_cluster = plugins.MarkerCluster().add_to(mapa2)


    colormap = folium.branca.colormap.LinearColormap(colors=['blue', 'green', 'orange', 'red'],
                                                     vmin=df_geo2[cluster2].min(),
                                                     vmax=df_geo2[cluster2].max())
    colormap.caption = cluster2
    colormap.add_to(mapa2)

    plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(mapa2)

    # Add Mini Map
    mapa2.add_child(minimap)

    # Adds tool to the top right
    mapa2.add_child(MeasureControl())

    # Marcker cluster
    #points = np.array((df_geo2['Latitude'], df_geo2['Longitude'])).T
    #plugins.MarkerCluster(points).add_to(mapa2)

    # Heatmap
    heatmap2 = HeatMap(list(zip(df_geo2['Latitude'], df_geo2['Longitude'], df_geo2[cluster2])),
                       min_opacity=0.2,
                       max_val=df_geo2[cluster2].max(),
                       radius=40,
                       # blur=40,
                       gradient={'0': 'blue', '0.25': 'green', '0.5': 'green', '0.75': 'orange', '1': 'Red'},
                       max_zoom=10,
                       )
    # add heatmap layer to base map
    heatmap2.add_to(mapa2)
    # Fin plugins---------------------------------------------------

    repere_geo(df_geo2, marker_cluster)

    folium_static(mapa2, width=1000, height=600)
# End Map cluster-------------------------------------------------------------------------------------------------------

#Graphique Joinplot-------------------------------------------------------------------------------------------------------
df_15_16 = df_15_16.sort_values(by=['energy_grad'], ascending=True)
if page == "Analyse Exploratoire":
    # Create a page dropdown
    sub_page = st.sidebar.radio("Choisissez l'analyse exploratoire",["Univariée", "Bivariée", "Boxplot"])

    colonnes = ('SiteEnergyUse(kBtu)', 'Electricity(kBtu)', 'SourceEUI(kBtu/sf)', 'YearBuilt', 'TotalGHGEmissions',
                'PropertyGFATotal', 'PropertyGFABuilding(s)', 'SteamUse(kBtu)', 'NumberofFloors', 'NumberofBuildings',
                'PropertyGFAParking', 'ENERGYSTARScore')

    col1, col2, col3, col4 = st.columns([2 / 8, 4 / 8, 4 / 8, 2 / 8])
    col5, col6, col7 = st.columns([1 / 6, 8 / 12, 1 / 6])
    col23, col24, col25 = st.columns([1/3, 1/3, 1/3])
    col26, col24, col25 = st.columns([1/3, 1/3, 1/3])
    col37, col38 = st.columns([5, 5])
    col35, col36 = st.columns([3, 7])


    if sub_page == 'Bivariée':
        with col38:
            st.subheader('Graphique Joinplot')

        with col35:
            Energy_1 = st.selectbox('Variable_X', colonnes)
            Energy_2 = st.selectbox('Variable_Y', colonnes)

        with col36:
            colors = ['#83c000', 'darkgreen', 'yellow', 'orange', 'red','lightblue']
            sns.set_palette(sns.color_palette(colors))

            fig = sns.jointplot(x=Energy_1, y=Energy_2, data=df_15_16, hue='energy_grad', height=11, ratio=8,dropna=True)

            st.pyplot(fig)

            st.write('-----------------------------------------------------------------------------------------------------------------------')
    if sub_page == 'Univariée':
        col23, col24, col25 = st.columns([1 / 3, 6 / 6, 1 / 3])

        with col24:
            Energy_4 = st.selectbox('Colonne', colonnes)

        fig3 = plt.figure(1)

        plt.suptitle(Energy_4 +  '2015/16\n',fontsize=14)

        plt.subplot(121)

        his = sns.histplot(data=df_15_16, x=df_15_16[Energy_4], kde=True, hue='DataYear', palette='bright')
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=10)
        his.set_xlabel(Energy_4 + ' 2015/16', fontsize=12)

        plt.subplot(122)
        ax = df_15_16[Energy_4].plot.box(figsize=(15,4), color='b')
        ax.set_xticklabels(['\n'+ Energy_4+" 2015/16"])


        plt.xticks(fontsize=12)
        plt.yticks(fontsize=10)

        st.pyplot(fig3)
        st.write('------------------------------------------------------------------------------------------------------')

        col27, col28, col29 = st.columns([1 / 3, 10 / 6, 1 / 3])
        with col28:
            categorie_grad = st.selectbox('Sélectionner le type du bâtiment', ('All', 'Hotel', 'Other', 'Store', 'Education', 'Office',
                                                          'Warehouse', 'Residence', 'Health', 'Restaurant'))

            fig2 = plt.figure(figsize=(12, 12))

            if categorie_grad != 'All':
                y = df_15_16['energy_grad'][df_15_16['PrimaryPropertyType'] == categorie_grad].value_counts().index
                x = df_15_16['energy_grad'][df_15_16['PrimaryPropertyType'] == categorie_grad].value_counts().values
            else:
                y = df_15_16['energy_grad'].value_counts().index
                x = df_15_16['energy_grad'].value_counts().values

            colors = {'A+': 'darkgreen', 'A': 'green', 'B': 'yellow', 'C': 'orange', 'D': 'red', 'NC': 'lightblue'}
            colors = pd.DataFrame(colors, index=[len(y)])

            var = colors[y.values]
            var = var.values.tolist()
            var = var[0]

            plt.pie(x, labels=y,
                    colors=var,
                    #explode=[0.2, 0, 0, 0, 0],
                    autopct=lambda x: str(round(x, 2)) + '%',
                    pctdistance=0.8, labeldistance=1.09,
                    shadow=True)

            plt.title('Analyse univariée Energie-grade pour : '+ categorie_grad, fontsize=16)



            #plt.legend(loc=2, fontsize=13, facecolor='#f4f4f4')
            plt.legend(y, loc=[1, 0.45], labels=['%s : %1.2f%%' % (l, s) for l, s in zip(y, (x / sum(x)) * 100)],
                       fontsize=16, facecolor='#fbf8f8')

            st.pyplot(fig2)
    #-----------------------------------------------------------------------------------------------------------------------
    #Fin Graphique Joinplot-------------------------------------------------------------------------------------------------------

#Graphique Boxplot-------------------------------------------------------------------------------------------------------

    Col_boxplot = ('SiteEnergyUse(kBtu)', 'Electricity(kBtu)', 'SourceEUI(kBtu/sf)', 'YearBuilt', 'TotalGHGEmissions',
                   'PropertyGFATotal',
                   'PropertyGFABuilding(s)', 'NumberofFloors', 'ENERGYSTARScore')

    if sub_page == 'Boxplot':

        col14, col15, col16 = st.columns([1 / 3, 1 / 3, 1 / 3])
        col8, col9, col10 = st.columns([1 / 12, 10 / 12, 1 / 12])

        with col15:
            fig, ax = plt.subplots()

            colors = ['#58F73C', 'blue', 'gray', 'red', 'orange', '#F73CA5', 'lightblue', 'pink', 'yellow']

            sns.set_palette(sns.color_palette(colors))

        with col6:
            Energy_3 = st.selectbox('Colonnes Boxplot', Col_boxplot)

        with col9:
            grouped = df_15_16.loc[:, ['PrimaryPropertyType', Energy_3]] \
                .groupby(['PrimaryPropertyType']) \
                .median() \
                .sort_values(by=Energy_3)

            sns.boxplot(x=df_15_16['PrimaryPropertyType'], y=np.log(df_15_16[Energy_3]), data=df_15_16, order=grouped.index,
                        showfliers=False)
            # sns.swarmplot(x= df_15_16['PrimaryPropertyType'], y = np.log(df_15_16[Energy_3]), data = df_15_16, order=grouped.index)

            # Ajouter des textes aux labels, titre etc.
            fig.set_size_inches(25, 10)
            ax.set_ylabel(Energy_3, fontsize=18)
            # ax.set_title("La quantité totale d'émissions de gaz à effet de serre (MetricTonsCO2e) - 2015/16\n", fontsize=18)
            ax.set_title("Boxplot de la colonne : " + Energy_3 + "\n", fontsize=18)

            plt.xticks(rotation='90', fontsize=18)
            plt.yticks(fontsize=15)
            plt.xlabel("\nType de propriété", fontsize=22)

            st.pyplot(fig)
#Fin Graphique Boxplot-------------------------------------------------------------------------------------------------------
