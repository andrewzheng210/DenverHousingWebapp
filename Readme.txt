1. Description and File Structure
1.1 Description
	Our project visualizes the analytics of Denver single family housing market, showing both historical and predicted house prices in Denver area. 
	
	This package include all needed data and codes for hosting our website: a house hunting portal.
	We have cleaned raw data for modeling and visualization, and only include necessary data and codes for the final deliverable (i.e. website hosting). Detailed project description and data sets are hosted on GitHub (https://github.com/lzhao-byte/denver-housing)

1.2 File Structure
	CODE/
		-CSVFiles: text files used in the website
		-JsonFiles: geojson files for map plotting
		-Models: prediction model and model parameter description
		-assets: css style files and website icon
		-app.py: main python file for website deployment
		-utils.py: utility functions for the application
		-Credentials: credentials for Mapbox and Google Street View features
		
2. Installation and Execution
	-- Our application is hosted on heroku.com, website address is:
		https://test-denver.herokuapp.com/
	-- To host our website locally, a python version of or above 3.7.6 is needed
		a. unzip the 'CODE' folder
		b. open the command line
		c. nagivate to 'CODE' folder
		d. run the following code
			> pip install numpy pandas dash dash_core_components dash_html_components dash_bootstrap_components dash_table xgboost jsonschema
			> python app.py
		e. open website with any internet browser using following address
			http://127.0.0.1:8050
		
		Notes: we use credentials to show additional features such as Google Street View picture for each house, to use such feature, please copy and paste your Mapbox access token to '/Credentials/mapbox_access_token.txt' file, and Google Street View Static API key to '/Credentials/google_street_view_api.txt'. Additional features should now work.