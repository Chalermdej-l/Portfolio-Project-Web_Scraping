# Portfolio-Profect-Web_Scraping

## Table of contents

* [Project Overview](#project-overview)
* [Prerequisite](#prerequisite)
* [Project Detail](#project-detail)


## Project Overview

This project is aim to create a web-scraping python script. To scape [Booking.com](https://www.booking.com/) to get the information for the hotel like review score, loaation, Id etc. Checking the [Robots.txt](https://www.booking.com/robots.txt)
 for [Booking.com](https://www.booking.com/) there is no disallow of scaping the hotel page data there is also a [XML page](https://www.booking.com/sitembk-hotel-index.xml) with all the hotel in different language for the clawer to use.
 We will use this script [GetUrl](/GetUrl.ipynb) to get the hotel list in the [XML page](https://www.booking.com/sitembk-hotel-index.xml) and pass this to this (template)[/template.txt] to scpate the data. There are many hotel
 just TH hotel alone have around 20,000 hotels. So to reduce the script run time I have try to split the workload into multiple run by using this [Scapebooking](/Scapebooking.ipynb) to populate the (template)[/template.txt] into multiple
 file base on the node varible provide then use this [.bat] (/Run.bat) file to run the code at the same time this will create multikple instance of python to run this script. Once the script done running the file will be paste in this folder
 [Output](/Output) then we will use this [Combine_load](/Combine_load.ipynb) to combine all the file into one and insert into a local SQL database. In the future I want to implement [Multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
 and [Multiprocessing](https://docs.python.org/3/library/multiprocessing.html) to reduce the run time for the script.
 

## Prerequisite

This project use Python and below package
1. [Pandas](https://pandas.pydata.org/)
2. [Pyodbc](https://pypi.org/project/pyodbc/)
3. [Requests](https://pypi.org/project/requests/)
4. [Bs4](https://pypi.org/project/beautifulsoup4/)
5. [Regex](https://pypi.org/project/regex/)

You can install the above project in the [Requirement.txt](/Requirement.txt) file provide in this project

```
pip install -r requirements.txt
```


## Project Detail

After clone the project you will find 2 excel file

1.Project_DashBoard

You can find the Dashboard create using excel function in `Portfolio 3` tab

![dashboard](/image/Excel_dashboard.png)


This dashboard show the monthly summary of the suppport call center stat like avg call per minute how many call take about what subject what agent receive the most call etc..

The data use in this dashboard can be found in `Portfolio 3_2` in this tab you can see the raw data and the calculation use for the dashboard.

2.Portfolio Project_VBA

Please note you may have to [enable trust](https://support.microsoft.com/en-us/topic/a-potentially-dangerous-macro-has-been-blocked-0952faa0-37e7-4316-b61d-5b5ed6024216) to this file as microsoft diable Macro by default.

2.1 First code `Portfolio1` use this [VBA code](/Script/Portfolio1_Loopandopenfile.bas) this code is desing to load the Excel and Text file data into this file

Please select `Import File` there will be a popup window to choose the file once choose the content will be insert into this sheet

![VBAtab1.png](/image/VBAtab1.png)

You can select `Clear Data` to remove all data in this page to load a new file

2.2 Second code `Portfolio 2` use this [VBA code](/Script/Portfolio2_LoopCellAndSavePDFdf.bas) this code is desing to export the data into WHT pdf format in  `Portfolio 2_2` tab

![wht](/image/Whtformat.png)

Please select `Save as pdf` button there will be a window to choose which Ref no. to start generated the data from.

![VBAtab2.png](/image/VBAtab2.png)

Once hit run the code will run depend on how many data there ar the code might take a minute or two to run 

After done there will be a folder create in the Desktop name `Print` folder this will store all the output pdf file generated

The code will also open this folder to check the output for any issue.

2.3 Thrid code `Portfolio 3` is desing to export the data into a text file for wht tax filing via the [RD Prep](https://efiling.rd.go.th/rd-cms/) program.

This sofeware can be use to file the Wht tax but you would need to prepare the data into the correct text format.

![VBAtab3.png](/image/VBAtab3.png)

This code will use the data in `Portfolio 3_2` and seperate them into different address type like province, City, Post code along with necessary data for the tax filing like tax rate tax amount.

You can chnage the number in `A2` cell to change between WHT3 and WHT53 form you can insert 3 or 53 in this cell and the fomula will change accordingly

Please select `Export03` button this will create a `WHTaxGenerate` folder in the Desktop with the text file generated.

The code will also open this folder to check the output file for any error.
