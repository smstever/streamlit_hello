# import the necessary libraries
import pandas as pd
import streamlit as st
import plotly.express as px  # interactive charts
import time

st.set_page_config(
    page_title="AWS MySQL Testing",
    page_icon="XX",
    layout="wide",
)

st.title('Here is my weather app!')
st.header('Live Data')
datadisplay = st.empty() #this is the top row on the dashboard 
temp_graph = st.empty() #this is the line chart of the temp on the dashboardw
humid_graph = st.empty() #this is the line chart of the humidity on the dashboard


# Initialize connection.
conn = st.connection('mysql', type='sql')


# st.cache_data is important for your app when it runs for a few days
# we have found that setting Time To Live (ttl) to 55 seconds works well 
# for a project that posts new data every minute and 
# the While True delay is 2 seconds
# place st.cache_data right before the query
# the query uses the object conn (defined above) and the method query

@st.cache_data(ttl=55)
def fetch_data():
    df = conn.query('SELECT tempF, humidity, YEAR(date_add(time_stamp,INTERVAL-5 HOUR)) as year, MONTH(date_add(time_stamp,INTERVAL-5 HOUR)) as month, DAY(date_add(time_stamp,INTERVAL-5 HOUR)) as day, HOUR(date_add(time_stamp,INTERVAL-5 HOUR)) as hour, MINUTE(date_add(time_stamp,INTERVAL-5 HOUR)) as minute, SECOND(date_add(time_stamp,INTERVAL-5 HOUR)) as second, date_add(time_stamp,INTERVAL-5 HOUR) as ts FROM esp32_dht20 ORDER BY time_stamp DESC LIMIT 5760;', ttl=1)
    return df


while True:
    # call the fetch_data function and store results in the dataframe named data
    data = fetch_data()

    #extract current temp in F and humidity and store in variables 
    current_temp, current_humidity = data.at[data.index[0], "tempF"], data.at[data.index[0], "humidity"]
    
    #extract penultimate temp(F) and humidity readings and store in variables 
    old_temp, old_humidity = data.at[data.index[1], "tempF"], data.at[data.index[1], "humidity"]

    #calculate the change in temp and change in humidity between the last two readings
    temp_delta, humid_delta = int(current_temp)-int(old_temp), int(current_humidity)-int(old_humidity)
    
    #making strings out of each part of the date
    month = str(data.at[data.index[0],"month"])
    day = str(data.at[data.index[0],"day"])
    year = str(data.at[data.index[0],"year"])
    hour = str(data.at[data.index[0],"hour"])
    minute = str(data.at[data.index[0],"minute"])
    second = str(data.at[data.index[0],"second"])

    #forming a formatted string for the date and time by concatenating several strings 
    lasttime_str = "Time of Last Data: "+ month + "/" + day + "/" + year + " at "+ hour + ":" + minute + ":" + second
   
   #the next section defines the contents of the datadisplay container
    with datadisplay.container():
        
        #the first item is printing the lasttime_str
        st.text(lasttime_str)    
        
        # Create Summary Temperature Information in two columns
        kpi1, kpi2 = st.columns(2)

        #each column uses the streamlit data element st.metric
        kpi1.metric(
            label = "Temperature F",
            value = "{} F".format(current_temp),
            delta = "{} F".format(temp_delta)
        )

        kpi2.metric(
            label="Humidity",
            value="{} %".format(current_humidity),
            delta="{} %".format(humid_delta)
        )
             
    with temp_graph:
        #this first line makes a copy of two columns from the data dataframe
        #and stores that in tempdata
        tempdata = data[['ts','tempF']].copy()
        fig_t = px.line(
            tempdata,
            x="ts", 
            y="tempF",
            title="Temperature (F)")
        st.plotly_chart(fig_t)


    with humid_graph:
        humiddata = data[['ts','humidity']].copy()
        fig_h = px.area(
            humiddata,
            x="ts", 
            y="humidity",
            title="Humidity (%)")
        st.plotly_chart(fig_h)
        
    
    wait_time = 2 # Change to required intervals
    time.sleep(wait_time)
