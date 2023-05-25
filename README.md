# Portfolio-Profect-Web_Scraping

## Table of contents

* [Project Overview](#project-overview)
* [Prerequisite](#prerequisite)
* [Project Detail](#project-detail)
  - [1.Get all the hotel list](#1-get-all-the-hotel-list)
  - [2.Scrape the data using the url list](#2-scrape-the-data-using-the-url-list)
  - [3.Combine all the file and insert into database](#3-combine-all-the-file-and-insert-into-database)
* [Further Improvements](#further-improvements)

## Project Overview

This project is aim to create a web-scraping python script. To scrape [Booking.com](https://www.booking.com/) to get the information for the hotel like review score, loaation, Id etc. 

Checking the [Robots.txt](https://www.booking.com/robots.txt) for [Booking.com](https://www.booking.com/) there is no disallow of scaping the hotel page data there is also a [XML page](https://www.booking.com/sitembk-hotel-index.xml) with all the hotel in different language for the clawer to use.

We will use this script [GetUrl](/GetUrl.ipynb) to get the hotel list in the [XML page](https://www.booking.com/sitembk-hotel-index.xml) and pass this to this (template)[/template.txt] to scpate the data. 

There are many hotel just TH hotel alone have around 20,000 hotels. So to reduce the script run time I have try to split the workload into multiple run by using this [Scrapebooking](/Scapebooking.ipynb) to populate the (template)[/template.txt] into multiple file base on the node varible provide.

Then use this [.bat] (/Run.bat) file to run the code at the same time this will create multikple instance of python to run this script. Once the script done running the file will be paste in this folder
 [Output](/Output) then we will use this [Combine_load](/Combine_load.ipynb) to combine all the file into one and insert into a local SQL database. 
 
 In the future I want to implement [Multiprocessing](https://docs.python.org/3/library/multiprocessing.html) and [Multithreading](https://docs.python.org/3/library/threading.html) to reduce the run time for the script.
 

## Prerequisite

This project use Python and below package
1. [Pandas](https://pandas.pydata.org/)
2. [Pyodbc](https://pypi.org/project/pyodbc/)
3. [Requests](https://pypi.org/project/requests/)
4. [Bs4](https://pypi.org/project/beautifulsoup4/)
5. [Regex](https://pypi.org/project/regex/)

Please clone this project 
```
git clone https://github.com/Chalermdej-l/Portfolio-Project-Web_Scraping
```

And navigate to the clone directory
```
cd Portfolio-Project-Web_Scraping
```

You can install the above package in the [Requirement.txt](/Requirement.txt) file provide in this project

```
pip install -r Requirements.txt
```


## Project Detail

### 1 Get all the hotel list

The goal is to get data of the hotel on [Booking.com](https://www.booking.com/). Thankfully Booking.com don't forbid cawlers [Robots.txt](https://www.booking.com/robots.txt) and they provide a list of useful information in xml format amoung them is all the hotel list this [XML page](https://www.booking.com/sitembk-hotel-index.xml).

![xml](/image/xmlurl.png)

Which we will use to scrape the data. We will use this [script](/GetUrl.ipynb) to save all the hotel list into local directory. The script will access the xml page and download each file into one list and then sepearte them into each country in a csv file.

![csv](/image/csvurl.png)

### 2 Scrape the data using the url list

After we get the url list of the hotel we will then scrape the page using this [template](/template.txt) this code will scrape the data for location name hotel id and dest id and the rview of the hotels.

![hotel](/image/scapehotel.png)

as there are many url in the list depend on the country there are about 20,000 hotel in TH alone so we can't run the script with 1 intance this will take too much time to solve this issue I have create this [script](/Scapebooking.ipynb) this script will open the csv file we get in step 1 and calculate the workload into different node we provide then it will create a script for each node using the [template](/template.txt) then run the created code with this [.bat](/Run.bat) file to run all the code at the same time with as the task is an [I/O bound](https://en.wikipedia.org/wiki/I/O_bound) tpye.

![splitfile](/image/splitfile.png)

### 3 Combine all the file and insert into database

After we done with the script we will then run this [script](/Combine_load.ipynb) this script will combine all the created file into one and insert this data into the local database. We can also save this as a CSV file instead  

![scrape](/image/scapetask.png)

## Further Improvements

Implement a [Multiprocessing](https://docs.python.org/3/library/multiprocessing.html) and [Multithreading](https://docs.python.org/3/library/threading.html) to reduce the workload intead of split the task into multiple file and run them. The current code need to be run manaully and not continuous as a pipeline with Multiprocessing and Multithreading we can setup a pipeline to wait for all the task to finish then combine all the file and insert them into a data storage.
