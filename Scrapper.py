def clean_string(dirty_string):
    cleaned_string = ' '.join(dirty_string.split())
    return re.sub('\s+',' ',cleaned_string)
def add_element(dict, key, value):
    if key not in dict:
        dict[key] = value
    #dict[key].append(value)
def get_sec(time_str):
    """Get seconds from time."""
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)
def is_int(v):
    try:
        integer=int(v)
    except ValueError:
        return 0
    return integer

df_events_list = pd.DataFrame(columns = ('date','url','event_name'))

for i in range(5):
    stat_site = str('http://ufcstats.com/statistics/events/completed')
    if i == 0:
        r=requests.get(stat_site)
    else:
        r=requests.get(stat_site+'?page='+str(i))
    events_list_soup = BeautifulSoup(r.text,'html.parser')
    for fight_night in events_list_soup.find_all('i',attrs={'class':'b-statistics__table-content'}):
        event_row = {'url':fight_night.a['href'],
                'date':clean_string(fight_night.span.text),
                'event_name':clean_string(fight_night.a.text)}
    df_events_list = df_events_list.append(event_row,ignore_index = True)


rows = []
#for i in range(5):
### WHICH URL STAT PAGE AM I IN?
#if i == 0:
r=requests.get('http://ufcstats.com/statistics/events/completed')
fightnights_list_soup = BeautifulSoup(r.text,'html.parser')
# else:
#     r=requests.get('http://ufcstats.com/statistics/events/completed?page='+str(i))
#     fightnights_list_soup = BeautifulSoup(r.text,'html.parser')
    
# GOING INTO INDIVIDUAL FIGHT NIGHTS TO GET LIST OF FIGHTS        
for fight_night in fightnights_list_soup.find_all('i',attrs={'class':'b-statistics__table-content'}):
    event_date = datetime.date(datetime.strptime(clean_string(fight_night.span.text), '%B %d, %Y'))
    if event_date >= datetime.date(datetime.today()):
        continue 
    fightnight_url = fight_night.a['href']
    fightnight_name = clean_string(fight_night.a.text)
    fight_night_r=requests.get(fight_night.a['href'])
    fightnight_soup = BeautifulSoup(fight_night_r.text,'html.parser')
    
    
# INDIVIDUAL FIGHT URL, WEIGHT CLASS, METHOD OF WINNING 
    for fight in fightnight_soup.find_all('tr',attrs={'class':'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'}):
        fight_url = fight.a['href']
        print(fight_url)
        fight_r=requests.get(fight.a['href'])
        fight_soup = BeautifulSoup(fight_r.text,'html.parser')
        weight_class = clean_string(fight_soup.find('i',attrs={'class':'b-fight-details__fight-title'}).text)[:-5]
        finish_method = clean_string(fight_soup.find('i', class_='b-fight-details__text-item_first').text).split(': ')
        #optional - other details of the fight
        #for detail_child in fight_soup.find('i', class_='b-fight-details__text-item_first').find_next_siblings():
        #    detail = clean_string(detail_child.text).split(': ')
        #    print(detail)
        #    print(detail[0]+' column\n'+detail[1]+' value')
        #    print('xxxx')
        #for detail in fight_soup.find('p', class_ ='b-fight-details__text').findChildren():
        #    print(detail)
        finish_details = clean_string(fight_soup.find('p', class_ ='b-fight-details__text').find_next_sibling().text).split(': ')
        
# WHO WON?           
        for score in fight_soup.find('div', class_='b-fight-details__person').i:
            if clean_string(score) == 'L':
                winner = 'BLUE'
            elif clean_string(score) == 'NC':
                winner = 'NOCONTEST'
            elif clean_string(score) == 'W':
                winner = 'RED'
            else:
                winner = 'NA'
        fighter_RED_BLUE = 0
        print('result details ok')        
# FIGHTER DETAILS           
        for fighter in fight_soup.find_all('h3', class_ = 'b-fight-details__person-name'):
            fighter_r = requests.get(fighter.a['href'])
            fighter_soup = BeautifulSoup(fighter_r.text,'html.parser')
            if fighter_RED_BLUE == 0:
                red_fighter = clean_string(fighter.text)
                for physical_char in fighter_soup.find_all('li', class_='b-list__box-list-item b-list__box-list-item_type_block',limit = 5): #, class_="b-list__box-list
                    physical = clean_string(physical_char.text).split(': ')
                    physical[0] = physical[0].upper()
                    if physical[0] == 'HEIGHT':
                        feet, inches = physical[1][:-1].split("\' ")
                        red_height = int(feet)*30.48+int(inches)*2.54
                    if physical[0] == 'WEIGHT':
                        continue
                    if physical[0] == 'REACH':
                        red_reach = int(physical[1][:2])*2.54
                    if physical[0] == 'DOB':
                        red_age = 2022 - int(physical[1][-4:])
            else:
                blue_fighter = clean_string(fighter.text)
                for physical_char in fighter_soup.find_all('li', class_='b-list__box-list-item b-list__box-list-item_type_block',limit = 5): #, class_="b-list__box-list
                    physical = clean_string(physical_char.text).split(': ')
                    physical[0] = physical[0].upper()
                    if physical[0] == 'HEIGHT':
                        feet, inches = physical[1][:-1].split("\' ")
                        blue_height = int(feet)*30.48+int(inches)*2.54
                    if physical[0] == 'WEIGHT':
                        continue
                    if physical[0] == 'REACH':
                        blue_reach = int(physical[1][:2])*2.54
                    if physical[0] == 'DOB':
                        blue_age = 2022 - int(physical[1][-4:])
            fighter_RED_BLUE = 1
            
# EVENT AND FIGHTER DETAILS                
        event_row = {'FIGHTNIGHT_URL':fightnight_url,
        'EVENT_DATE':event_date,
        'FIGHTNIGHT_NAME':fightnight_name,
        'FIGHT_URL':fight_url,
        'WEIGHT_CLASS': weight_class,
        'FINISH_METHOD': finish_method[1],
        #'FINISH_DETAIL': finish_details[1],
        'WINNER': winner,
        'RED_FIGHTER':red_fighter,
        'RED_HEIGHT':red_height,
        'RED_REACH_CM':red_reach,
        'RED_AGE':red_age,
        'BLUE_FIGHTER':blue_fighter,
        'BLUE_HEIGHT':blue_height,
        'BLUE_REACH_CM':blue_reach,
        'BLUE_AGE':blue_age,
        }
        final_row = {}
        print('event details ok')
# FIGHT DETAILS     
        for table in fight_soup.find_all('table'):
            print('_______________________________________')
            round_no = 0
            columns = []
            fight_details = {}
            
            for column in table.find_all('th'):
                column_name = re.sub(('\. | '),'_',
                                    re.sub('\.','',    
                                            re.sub('%', 'PERC',column.text.strip().upper()
                                        )
                                    )
                                )
                column_name = re.sub('_STR','_STRIKE',column_name)
                columns.append(column_name)
            #print(columns, 'check')
            if 'ROUND_' in columns[len(columns)-1]:
                round_no = columns[len(columns)-1][-1:]
                columns = head_columns
                loop_round = 1
            col_index = 0
            order=0
            head_columns = columns
            
            if round_no == 0:
                for data in table.find_all('p'):
                    #print('zzzz')
                    #print(col_index)
                    if order%2==0:   
        
                        detail = ['RED_'+columns[col_index],clean_string(data.text)]
                        #print(detail)
                    else:
                        detail = ['BLUE_'+columns[col_index],clean_string(data.text)]
                        #print(detail)
                        col_index = col_index + 1
                    add_element(fight_details,detail[0],detail[1])
                    #print('xxxx')
                    order = order + 1
                    
            else:
          #      while round_no != 0:
                    #print(round_no)
                    col_index = 0
                    for data in table.find_all('p'):
                        #print('zzzz')
                        if order%2==0:   
        
                            detail = ['RED_RD'+str(loop_round)+'_'+columns[col_index],clean_string(data.text)]
                            #print(detail)
                        else:
                            detail = ['BLUE_RD'+str(loop_round)+'_'+columns[col_index], clean_string(data.text)]
                            #print(detail)
                            if col_index == len(columns)-1:
                                col_index = 0
                                loop_round = loop_round + 1
                            else:
                                col_index = col_index + 1
                        #print('xxxx')
                        add_element(fight_details,detail[0],str(detail[1]))
                        
                        order = order + 1
            #print(fight_details)              
            of_dict = {}
            to_delete = []
            for key in fight_details:
                value = fight_details[key]
                if 'FIGHTER' in key:
                    #print(key)
                    to_delete.append(key)
                elif ':' in value:
                    fight_details[key] = get_sec(value)
                elif 'of' in value:
                    splitted_string = value.split(' of ')
                    successful_column = key+'_SUCCESSFUL'
                    add_element(of_dict,successful_column,str(splitted_string[0]))
                    #print(fight_details[key])
                    to_delete.append(key)
                    #print(of_dict[successful_column])
                elif '---' in value:
                    fight_details[key] = 'NA'
                else:
                    pass
                  
## FINAL DICT APPENDED TO DATAFRAME          
            fight_details = {**fight_details,**of_dict}
            for deleted in to_delete:
                del fight_details[deleted]
            final_row = {**final_row,**fight_details}
        event_row = {**event_row, **final_row}
        rows.append(event_row)
df = pd.DataFrame(rows)
df.head()