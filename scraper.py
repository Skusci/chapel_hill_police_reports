import scraperwiki    
import re
from splinter import Browser
import datetime
from bs4 import BeautifulSoup
from collections import OrderedDict

starting_page = 'https://www.caahep.org/Students/Find-a-Program.aspx'


def parse_results(html):
    """
    Returns a list of dictionaries that describe the incidents in the given HTML.
    """
    soup = BeautifulSoup(html, "html5lib")
    
    programlist = soup.find('ul', attrs={'id': 'cbp-ntaccordion'})

    programs = []
    for r in programlist.findAll('li', recursive=False):
        ProgramId = r.get('id')[7:];
        City = str(r.find('h5', attrs={'class': 'cbp-nttrigger cbp-first col-md-2 col-sm-3 col-xs-3'}).contents[0].string)
        State = str(r.find('span', attrs={'class': 'StateTitle'}).string)
        Institution = str(r.find('h3', attrs={'class' : 'cbp-nttrigger col-md-4 col-sm-3 col-xs-3'}).string)
        Profession = str(r.find_all('h3', attrs={'class' : 'cbp-nttrigger col-md-3 col-sm-3 col-xs-3'})[0].string)
        Concentration = str(r.find_all('h3', attrs={'class' : 'cbp-nttrigger col-md-3 col-sm-3 col-xs-3'})[1].string)
        
        Address = r.find('div', attrs={'class' : 'program-address col-md-6 col-sm-6 col-xs-6'}).find('p')
        Address1 =  str(Address.contents[0].string)
        Address2 =  str(Address.contents[2].string)
        Address3 =  str(Address.contents[4].string)
        Address4 =  str(Address.contents[6].string)
        Address5 =  str(Address.contents[8].string)

        
        ProgInfo = r.find('div', attrs={'class' : 'program-info col-md-6 col-sm-6 col-xs-6'}).find('p')
        
        
        Offset1 = 1 if (str(ProgInfo.contents[1].string) == "Status") else 0
        OffsetA = 1 if (str(ProgInfo.find_all('a')[0].string) == "Program Outcomes" ) else 0
        
        
        ProgStatus = str(ProgInfo.contents[1+Offset1].string)[2:]
        ProgAccredDate = str(ProgInfo.contents[5+Offset1].string)[2:]
        ProgDegrees = str(ProgInfo.contents[10+Offset1].string)
        
        ProgOutcomes = str(ProgInfo.find_all('a')[0].get('href')) if (OffsetA == 1) else "Unavailable"
        
        if (OffsetA == 1) and (ProgOutcomes[:4] != "http"):
            ProgOutcomes = "http://" + ProgOutcomes
            
        ProgDirector = str(ProgInfo.contents[16+Offset1+2*OffsetA].string)[2:]
        
        
        ProgPhone = str(ProgInfo.find_all('a')[0+OffsetA].find('span').string)
        ProgPhone = ProgPhone[:3] + '.' + ProgPhone[3:6] + '.' + ProgPhone[6:]
        
        ProgEmail = str(ProgInfo.find_all('a')[1+OffsetA].string)
        ProgAward = str(ProgInfo.find_all('a')[2+OffsetA].get('href'))
        
        
        Website = str(r.find('h4', attrs={'class' : 'website'}).contents[0].string)
        
        program = OrderedDict([
            ('ProgramId' , ProgramId),
            ('Institution Name', Institution),
            ('Profession', Profession),
            ('Concentration', Concentration),
            ('City', City),
            ('State', State),    
            ('Address Line 1', Address1),
            ('Address Line 2', Address2),
            ('Address Line 3', Address3),
            ('Address Line 4', Address4),
            ('Address Line 5', Address5),
            ('Program Status', ProgStatus),
            ('Accredation Date', ProgAccredDate),
            ('Degrees' , ProgDegrees),
            ('Program Outcomes', ProgOutcomes), 
            ('Director', ProgDirector),
            ('Phone' ,ProgPhone),
            ('E-Mail' , ProgEmail),
            ('Award Link' , ProgAward),
            ('Website', Website),
        ])
        
        scraperwiki.sqlite.save(['ProgramId'], program)
        programs.append(program)
    return programs


def get_pages():
    """
    Returns the HTML of all pages
    """

    # Optional, but make sure large enough that responsive pages don't
    # hide elements on you...
        
    executable_path = {'executable_path':'/usr/bin/phantomjs'}
    browser = Browser('phantomjs', **executable_path)
    browser.driver.set_window_size(1280, 1024)

    # Open the page you want...
    browser.visit(starting_page)

    for p in range(85, 87):
        browser.execute_script("__doPostBack('p$lt$WebPartZone6$Content$pageplaceholder$p$lt$WebPartZone2$Search$ProgramList$repItems$pager','" + str(p) + "')" )
        print 'Retrieving page %s' % p
        time.sleep(2)
        pages.append(browser.html)
    return pages



print 'Retrieving results'
pages = get_pages()
print 'Parsing %s pages of results' % len(pages)
results = []
for page in pages:
    results.extend(parse_results(page))

print 'Found %s results, saved in scraperwiki' % len(results)


