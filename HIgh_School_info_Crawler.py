
# coding: utf-8

'''
Syntax Example:

#The file path for text file contains states name
#If you do not have idea about the format of this file, please take a look file named 'states_list.txt' in Github link
file_path = './states_list.txt'

#intial the instance
sc = SchoolCrawler(file_path)

#call crawlong function
#the number will determine which state data you want to gather. 

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
 
sc.States_Crawing(1)

'''

# In[1]:


#third-party lib
from bs4 import BeautifulSoup
from six import iteritems
#from pprint import pprint
#import pdb, traceback, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions

#regular libs
import os
import urllib.request
from urllib import request, parse
import re
import xlsxwriter


# In[30]:


class SchoolCrawler(object):
    
    '''
    Initilization
    
    file_path: string 
        The file path of states list file. The format should be one state per line in 'txt' format.
        The text of each state should match the name on website.
        
    web_drive_wait_time: int - optional
        Defalut is set to 5 seconds.
        The explicit wait time for web drive(Firefox, Chrome...) after executing JS-execute function. 
        This parameter needs to be adjusted with the accordance of network traffic condition. 
        Theoritically, heavier traffic requires bigger number.
        Otherwise, it keeps throwing 'TimeOutException'
        
    web_drive_name: string - optinal
        Defalut is set as Firefox browser.
        Specifiy this paramter if and only if the machine does not have Firefox installed.
        
        *WARNING*
        The browsers other than Firefox are not tested due to the limit of developer's machine. 
        Check the official website to get more infos about supported browsers:
        https://www.seleniumhq.org/docs/01_introducing_selenium.jsp
        
    Return: none
    
    '''
    def __init__(self,file_path, web_drive_name='FireFox', web_drive_wait_time=5):
        
        self.file_path = file_path
        
        self.web_drive_name = web_drive_name
        
        self.web_drive_wait_time = web_drive_wait_time
        
        '''root_path should not be eaditable in public scale'''
        self.root_path = 'https://www.privateschoolreview.com'
    
    '''
    To read states list file into memory. It will be called by other functions.
    
    Return - list: string
        A python list contains states name
    '''
    def State_Name_Reader(self):

        file_path = self.file_path

        states_list = []

        with open(file_path,"r") as fp:  
            line = fp.readline()
            while line:
                line = line.strip().lower()
                states_list.append(line)
                #print(line.strip().lower())
                line = fp.readline()
        fp.close()
        
        return states_list
    
    '''
    To get the county list under certain state
    
    state_path: string
        One component makes up a whole county list request URL
        
    Return - Dict: string, string
        Python dictionary. 
        Key is county name.
        Value is the correspond URL component
    '''
    def County_List(self,state_path):
        
        '''Instance Variables'''
        root_path = self.root_path
        
        '''county list request'''
        request = urllib.request.Request(root_path+state_path)
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8',"ignore")
        soup = BeautifulSoup(html,"lxml")

        county_list = soup.findAll("li", {"class" : "table_row row_click"})

        state_counties = {}
        
        '''Counties under current state'''
        for county in county_list:


            link_arr = county.findAll("a", {"href" : re.compile("^/")})

            padding_link = link_arr[0]['href']

            current_county_name = link_arr[0].contents

            state_counties[current_county_name[0]] = padding_link
            
        return state_counties
    
    '''
    To get private shools info and save it
    
    ps_rows: int
        Indicate current row number for written line in excel file.
        The initial variable will always be 1.(0 is Title)
        Do not touch value inside function, otherwise some data will be overwritten
        
    schools_page: string
        One string variable makes up whole request URL.
        It leads to the school list page.
        
    private_sheet: xlsxwriter.worksheet.Worksheet
        The state worksheet contains private schools info
    '''
    def Private_School_list(self, ps_rows, schools_page, private_sheet):
        
        '''Instance Variables'''
        root_path = self.root_path
        web_drive_name = self.web_drive_name
        web_drive_wait_time = self.web_drive_wait_time
        
        '''Private School request'''
        sub_private_request = urllib.request.Request(root_path+schools_page)
        sub_private_response = urllib.request.urlopen(sub_private_request)
        sub_private_html = sub_private_response.read().decode('utf-8',"ignore")
        sub_private_soup = BeautifulSoup(sub_private_html,"lxml")

        private_schools_list = []

        '''If need to click expand button to see complete list'''
        expand = sub_private_soup.findAll("li", {"id" : "open_show_more_item"})

        '''If expand button is detected, to simulate expand function on website for granting complete schools'''
        if len(expand)!=0:

            '''Set None as default'''
            driver = None

            '''Edit this part if you need more browser support'''
            if self.web_drive_name == 'Chrome':
                driver=webdriver.Chrome()
            else:
                driver=webdriver.Firefox()

            driver.get(root_path+schools_page)

            '''Keep expanding until the list is complete'''
            while len(expand)!=0:
                driver.find_element_by_id('open_show_more_item').click()
                #driver.implicitly_wait(5)
                WebDriverWait(driver, web_drive_wait_time).until_not(expected_conditions.text_to_be_present_in_element((By.ID, 'open_show_more_item'),"Loading..."))

                web_data=driver.page_source

                sub_private_soup=BeautifulSoup(web_data,'lxml')
                expand = sub_private_soup.findAll("li", {"id" : "open_show_more_item"})

            driver.quit()
            del sub_private_html
            del expand

        '''Get school lists'''
        private_schools_list = sub_private_soup.findAll("li", {"class" : "table_row row_click"})

        '''Loop every school'''
        for ps in private_schools_list:

            '''If get the closed schools, quit looping function'''
            if ps.has_attr("id") and ps["id"] == "closed_show_more_item":
                break

            ps_arr = ps.findAll("a", {"class" : "school_links"})

            ps_info = ps_arr[0]

            current_ps_link = ps_info['href']
            #current_ps_name = ps_info.contents[0].contents[0]

            url = root_path + current_ps_link

            '''Some school's link contains root link'''
            if 'www.privateschoolreview.com' in current_ps_link:
                url = current_ps_link

            #print(url)
            '''Details Page'''
            ps_request = urllib.request.Request(url)
            ps_response = urllib.request.urlopen(ps_request)
            ps_html = ps_response.read().decode('utf-8','ignore')
            ps_soup = BeautifulSoup(ps_html,"lxml")


            ps_detail = ps_soup.findAll("div", {"class" : "contentboxinner"})

            '''Name'''
            current_ps_name_arr = ps_soup.findAll("span", {"itemprop" : "name","gjs_id":re.compile(r'\b\d+\b')})
            current_ps_name = current_ps_name_arr[-1].contents[0]

            #print(current_ps_name)
            '''Address'''
            ps_detail_address_arr = ps_detail[0]

            ps_detail_address_street = ps_detail_address_arr.findAll("span", {"itemprop" : "streetAddress"})
            ps_detail_address_county = ps_detail_address_arr.findAll("span", {"itemprop" : "addressLocality"})
            ps_detail_address_state = ps_detail_address_arr.findAll("span", {"itemprop" : "addressRegion"})
            ps_detail_address_zip= ps_detail_address_arr.findAll("span", {"itemprop" : "postalCode"})

            ps_street = ""
            ps_county = ""
            ps_state = ""
            ps_zipcode = ""

            if len(ps_detail_address_street)!=0:
                ps_street = ps_detail_address_street[0].contents[0]

            if len(ps_detail_address_county)!=0:
                ps_county = ps_detail_address_county[0].contents[0]

            if len(ps_detail_address_state)!=0:
                ps_state = ps_detail_address_state[0].contents[0]

            if len(ps_detail_address_zip)!=0:
                ps_zipcode = ps_detail_address_zip[0].contents[0]

            print(url)
            #print(rows)
            #print(ps_detail_address_street)
            #print(ps_detail_address_county)
            #print(ps_detail_address_state)
            #print(ps_detail_address_zip)
            #print()

            ps_address = ps_street + ", " + ps_county +", "+ ps_state +" "+ps_zipcode


            #print(ps_address)

            '''Phone'''
            ps_detail_phone_arr = ps_detail[0]

            ps_detail_phone = ps_detail_phone_arr.findAll("a", {"rel" : "nofollow"})

            ps_phone = ""

            if len(ps_detail_phone) != 0:
                ps_phone = ps_detail_phone[0]['href'].lower().strip('tel:')

            #print(ps_phone)

            '''Web'''
            ps_detail_web_arr = ps_detail[0]

            ps_detail_web = ps_detail_web_arr.findAll("a", {"class" : "website_click"})

            ps_web = ""

            if len(ps_detail_web) != 0:
                ps_web = ps_detail_web[0]['href']

            #print(ps_web)

            #print()

            private_sheet.write(ps_rows, 0, current_ps_name)
            private_sheet.write(ps_rows, 1, ps_address)
            private_sheet.write(ps_rows, 2, ps_phone)
            private_sheet.write(ps_rows, 3, ps_web)
            private_sheet.write(ps_rows, 4, url)
            
            ps_rows += 1

                
    '''
    To get public shools info and save it
    
    ps_rows: int
        Indicate current row number for written line in excel file.
        The initial variable will always be 1.(0 is Title)
        Do not touch value inside function, otherwise some data will be overwritten
        
    schools_page: string
        One string variable makes up whole request URL.
        It leads to the school list page.
        
    public_sheet: xlsxwriter.worksheet.Worksheet
        The state worksheet contains public schools info
    '''
    def Public_School_list(self,pbs_rows,schools_page, public_sheet):
        
        '''Instance Variables'''
        root_path = self.root_path
        web_drive_name = self.web_drive_name
        web_drive_wait_time = self.web_drive_wait_time
    
        '''Public School'''
        sub_public_request = urllib.request.Request(root_path+schools_page+"/public")
        sub_public_response = urllib.request.urlopen(sub_public_request)
        sub_public_html = sub_public_response.read().decode('utf-8','ignore')
        sub_public_soup = BeautifulSoup(sub_public_html,"lxml")

        public_schools_list = []

        expand = sub_public_soup.findAll("li", {"id" : "open_show_more_item"})

        '''If expand button is detected, to simulate expand function on website for granting complete schools'''
        if len(expand)!=0:

            driver = None

            '''Edit this part if you need more browser support'''
            if web_drive_name == 'Chrome':
                driver=webdriver.Chrome()
            else:
                driver=webdriver.Firefox()

            driver.get(root_path+schools_page+"/public")

            '''Keep expanding until the list is complete'''
            while len(expand)!=0:

                driver.find_element_by_id('open_show_more_item').click()
                #driver.implicitly_wait(5)
                WebDriverWait(driver, web_drive_wait_time).until_not(expected_conditions.text_to_be_present_in_element((By.ID, 'open_show_more_item'),"Loading..."))
                web_data=driver.page_source

                sub_public_soup=BeautifulSoup(web_data,'lxml')
                expand = sub_public_soup.findAll("li", {"id" : "open_show_more_item"})

            driver.quit()
            del expand
            del sub_public_html

        '''Get school list'''
        public_schools_list = sub_public_soup.findAll("li", {"class" : "table_row row_click"})



        for pbs in public_schools_list:

            '''If get the closed schools, quit looping function'''
            if pbs.has_attr("id") and pbs["id"] == "closed_show_more_item":
                break

            pbs_arr = pbs.findAll("a", {"class" : "school_links"})

            pbs_info = pbs_arr[0]

            current_pbs_link = pbs_info['href']


            '''Some school's link contains root link'''
            url = current_pbs_link

            #print(url)
            '''Details Page'''
            pbs_request = urllib.request.Request(url)
            pbs_response = urllib.request.urlopen(pbs_request)
            pbs_html = pbs_response.read().decode('utf-8',"ignore")
            pbs_soup = BeautifulSoup(pbs_html,"lxml")


            detail = pbs_soup.findAll("div", {"class" : "contentboxinner"})

            '''Name'''
            current_pbs_name_arr = pbs_soup.findAll("span", {"itemprop" : "name","gjs_id":re.compile(r'\b\d+\b')})
            current_pbs_name = current_pbs_name_arr[-1].contents[0]
            #print(current_pbs_name)
            #print(detail)

            '''Address'''
            detail_address_arr = detail[0]


            street = ""
            county = ""
            state = ""
            zipcode = ""
            #print(detail[0])

            detail_address_street = detail_address_arr.findAll("span", {"itemprop" : "streetAddress"})

            detail_address_county = detail_address_arr.findAll("span", {"itemprop" : "addressLocality"})

            detail_address_state = detail_address_arr.findAll("span", {"itemprop" : "addressRegion"})

            detail_address_zip= detail_address_arr.findAll("span", {"itemprop" : "postalCode"})

            if len(detail_address_street)!=0:
                street = detail_address_street[0].contents[0]

            if len(detail_address_county)!=0:
                county = detail_address_county[0].contents[0]

            if len(detail_address_state)!=0:
                state = detail_address_state[0].contents[0]

            if len(detail_address_zip)!=0:
                zipcode = detail_address_zip[0].contents[0]

            print(url)
            #print(rows)
            #print(detail_address_street)
            #print(detail_address_county)
            #print(detail_address_state)
            #print(detail_address_zip)
            #print()

            address =  street + ", " + county +", "+ state +" "+ zipcode
            #print(address)

            '''Phone'''
            detail_phone_arr = detail[0]

            detail_phone = detail_phone_arr.findAll("a", {"rel" : "nofollow"})

            phone = ""

            if len(detail_phone) != 0:
                phone = detail_phone[0]['href'].lower().strip('tel:')

            #print(phone)

            '''Web'''
            detail_web_arr = detail[0]

            detail_web = detail_web_arr.findAll("a", {"class" : "website_click"})

            web = ""

            if len(detail_web) != 0:
                web = detail_web[0]['href']

            #print(web)

            public_sheet.write(pbs_rows, 0, current_pbs_name)
            public_sheet.write(pbs_rows, 1, address)
            public_sheet.write(pbs_rows, 2, phone)
            public_sheet.write(pbs_rows, 3, web)
            public_sheet.write(pbs_rows, 4, url)

            pbs_rows += 1
    
    '''
    Main function. 
    It crawls data from webpage and save data to excel files: public schools, private schools.
    
    index: int
        The index of member elements in states list. The index will be corresponds to the order in original text file.
        
    '''
    def States_Crawing(self,index):
        
        '''pre-process, combine URL for getting county list under current state'''
        root_path = self.root_path
        
        state_name_list = self.State_Name_Reader()
        
        state_name = ''
        
        if index < len(state_name_list):
            state_name = state_name_list[index]
        else:
            raise Exception('The index is out of list range!')
            
            
        '''Initial Excel file'''
        private_book  = xlsxwriter.Workbook(state_name+'_private_schools.xlsx')
        public_book  = xlsxwriter.Workbook(state_name+'_public_schools.xlsx')

        private_sheet = private_book.add_worksheet(state_name)

        private_sheet.write(0, 0, 'School Name')
        private_sheet.write(0, 1, 'Address')
        private_sheet.write(0, 2, 'Phone')
        private_sheet.write(0, 3, 'School Website')
        private_sheet.write(0, 4, 'Link')

        public_sheet = public_book.add_worksheet(state_name)

        public_sheet.write(0, 0, 'School Name')
        public_sheet.write(0, 1, 'Address')
        public_sheet.write(0, 2, 'Phone')
        public_sheet.write(0, 3, 'School Website')
        public_sheet.write(0, 4, 'Link')
        
        
        state_path = '/'+state_name
        
        print("Chosen State is "+state_name)
        
        '''Initial county list request'''
        state_counties = self.County_List(state_path)

        ps_rows = 1
        pbs_rows = 1

        '''Get school list and get detail infos in current county'''
        for label in state_counties:
            print(label)

            '''All School'''
            schools_page = state_counties[label]
            
            
            self.Private_School_list(ps_rows, schools_page, private_sheet)
            self.Public_School_list(pbs_rows, schools_page, public_sheet)

            
        private_book.close()
        public_book.close()
