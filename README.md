# High-School-Info-Crawler
This script is the legacy code in schools' project and it crawls the school data from website: 

https://www.privateschoolreview.com</br>  
https://www.publicschoolreview.com</br>

## Required Libs
selenium (version 3.14.0 is required)
BeautifulSoup
six
xlsxwriter
urllib

## Syntax Example

If you want to import to your own python file, just prepare a new blan python file under same file path and ...
```
import HIgh_School_info_Crawler as hsic
```

The file path for text file contains states name</br>
If you do not have idea about the format of this file, please take a look file named 'states_list.txt' in Github link</br>

```
file_path = './states_list.txt'
```

intial the instance</br>
```
sc = hsic.SchoolCrawler(file_path)
```

call crawlong function</br>
```
sc.States_Crawing(1)
```




## Index Form
```
Alabama - 0
Alaska - 1
Arizona - 2
Arkansas - 3
California - 4
Colorado - 5
Connecticut - 6
Delaware - 7
District-of-Columbia - 8
Florida - 9
Georgia - 10
Hawaii - 11
Idaho - 12
Illinois - 13
Indiana - 14
Iowa - 15
Kansas - 16
Kentucky - 17
Louisiana - 18
Maine - 19
Maryland - 20
Massachusetts - 21
Michigan - 22
Minnesota - 23
Mississippi - 24
Missouri - 25
Montana - 26
Nebraska - 27
Nevada - 28
New-Hampshire - 29
New-Jersey - 30
New-Mexico - 31
New-York - 32
North-Carolina -33
North-Dakota - 34
Ohio - 35
Oklahoma - 36
Oregon - 37
Pennsylvania - 38
Rhode-Island - 39
South-Carolina - 40
South-Dakota - 41
Tennessee - 42
Texas - 43
Utah - 44
Vermont - 45
Virginia - 46
Washington - 47
West-Virginia -48
Wisconsin - 49
Wyoming - 50
```

## Authors
FantasticApple</br>
