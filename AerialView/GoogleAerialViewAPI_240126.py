'''                                                                              
Script: Google Aerial View API Ver1.2
Author: Jeong Hoon Kim
Date: Jan 19, 2024 
Last Updated: Jan 26, 2024         
''' 

# import libraries
import arcpy, requests, os, json
import pandas as pd

# set parameters
MY_GDB = arcpy.GetParameterAsText(0) # Current workspace
MY_API_KEY = arcpy.GetParameterAsText(1) # Google Api Key, String
MY_ADDRESS = arcpy.GetParameterAsText(2) # Address, String

# set environment
arcpy.env.workspace = MY_GDB
arcpy.env.overwriteOutput = True 

# Define function for aerial_render
def aerial_render(address):
    render_url = 'https://aerialview.googleapis.com/v1/videos:renderVideo'
    render_headers = {'Content-Type': 'application/json',}
    render_params = {'key': str(MY_API_KEY),}
    render_jsonData = {'address': str(address),}
    MY_REQUEST = requests.post(render_url,
                                params=render_params,
                                headers=render_headers,
                                json=render_jsonData).json()
    return MY_REQUEST

# Define a function for geocode
def geocode(address):
    # request Geocoding API
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geocode_params = {
        'address': str(address),
        'key': str(MY_API_KEY),}    
    MY_JSON = requests.get(geocode_url, params=geocode_params).json()
    MY_STATUS = MY_JSON['status']
    if MY_STATUS == 'OK':
        MY_LOCATION = pd.json_normalize(MY_JSON['results'][0]['geometry']['location'])        
        MY_LOCATION.to_csv("my_location.csv")
        MY_CWD = os.getcwd()
        MY_CSV = os.path.join(MY_CWD, "my_location.csv")
        MY_POINT = os.path.join(MY_GDB, "my_point")
        arcpy.management.XYTableToPoint(MY_CSV, MY_POINT, 'lng', 'lat', '', arcpy.SpatialReference('WGS 1984'))
        return MY_POINT
    else:
        arcpy.AddMessage("There are some issues. Please check the following status.")
        return arcpy.AddMessage(MY_STATUS)

# Define function for aerial_lookup
def aerial_lookup(address):
    # Request aerial view
    lookup_url = 'https://aerialview.googleapis.com/v1/videos:lookupVideo'
    lookup_params = {'key': str(MY_API_KEY),
              'address': str(address),}
    MY_AERIALVIEW = requests.get(lookup_url, params=lookup_params).json()
    # Handle the output
    MY_DF = pd.json_normalize(MY_AERIALVIEW)
    MY_STATUS = MY_DF.iloc[0][0]
    if MY_STATUS == 'ACTIVE':
        MY_VIDEO = MY_DF.iloc[0][3] # High quality MP4 file - landscape
        arcpy.AddMessage("Video and location is created. Please check the link and feature point.")
        return geocode(address), arcpy.AddMessage(MY_VIDEO)
    elif MY_STATUS == 'PROCESSING':
        arcpy.AddMessage("Video is currently being rendering. Please check it later.")
        pass
    elif MY_STATUS == 404:
        arcpy.AddMessage("Rendering is requested. It will take a hour.")
        return aerial_render(address)
    else:
        arcpy.AddMessage("There is an issue. Please check the below.")
        return arcpy.AddMessage(MY_AERIALVIEW)

# run the function
aerial_lookup(MY_ADDRESS)