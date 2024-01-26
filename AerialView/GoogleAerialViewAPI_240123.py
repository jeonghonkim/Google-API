'''                                                                              
Script: Google Aerial View API 
Author: Jeong Hoon Kim 
Date: Jan 23, 2024 
Last Updated: Jan 23, 2024         
''' 

# import libraries
import arcpy, requests, os, json
import pandas as pd

# set parameters
MY_API_KEY = arcpy.GetParameterAsText(0) # Google Api Key, String
MY_ADDRESS = arcpy.GetParameterAsText(1) # Address, String

# Environment setting
arcpy.env.overwriteOutput = True
aprx = arcpy.mp.ArcGISProject("CURRENT") # Current Project 

# Define function url_request
def aerial_render(address):
    render_url = 'https://aerialview.googleapis.com/v1/videos:renderVideo'
    render_headers = {'Content-Type': 'application/json',}
    render_params = {'key': str(MY_API_KEY),}
    render_jsonData = {'address': str(address),}
    MY_RENDER = requests.post(render_url,
                                params=render_params,
                                headers=render_headers,
                                json=render_jsonData).json()
    return MY_RENDER

# Define function url_request
def aerial_lookup(address):
    # Request aerial view
    lookup_url = 'https://aerialview.googleapis.com/v1/videos:lookupVideo'
    lookup_params = {'key': str(MY_API_KEY), 
                     'address': str(address),}
    MY_VIDEO = requests.get(lookup_url, params=lookup_params).json()
    # Handle the output
    MY_DF = pd.json_normalize(MY_VIDEO)
    MY_STATUS = MY_DF.iloc[0][0]
    if MY_STATUS == 'ACTIVE':
        MY_LINK = MY_DF.iloc[0][3]
        arcpy.AddMessage(MY_LINK)
        return MY_LINK
    elif MY_STATUS == 'PROCESSING':
        print("Video is currently being rendering. Please check it later")
    elif MY_STATUS == 404:
        aerial_render(address)
        arcpy.AddMessage(aerial_render(address))
        arcpy.AddMessage("-Requested a new video under the address. It will take about 1 hour.")
    else:
        return arcpy.AddMessage(MY_VIDEO, "There is an issue. Please check the below!")

# run the function
aerial_lookup(MY_ADDRESS)
