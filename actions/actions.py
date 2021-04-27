# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction, ActionExecuted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
import requests
import csv
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
#
#
#class ActionHelloWorld(Action):

    #def name(self) -> Text:
        #return "action_hello_world"

    #def run(self, dispatcher: CollectingDispatcher,
            #tracker: Tracker,
            #domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       #city = tracker.get_slot('slot_city')
       #dispatcher.utter_message(text="Hello World!")
        #return []


min_rating = 0
min_cost = 0
max_cost = 0
def rating_min_max(rating_str):
    if rating_str == "3 and above":
        min_rating = 3
    elif rating_str == "4 and above":
        min_rating = 4
    elif rating_str =="5 and above":
        min_rating = 5
    else:
        min_rating = 0
    return min_rating

def cost_min_max(cost_str):
    if cost_str == "Super Budget Friendly":
        min_cost = 0
        max_cost = 400
    elif cost_str == "Budget Friendly":
        min_cost = 400
        max_cost = 700
    elif cost_str == "Luxury Budget":
        min_cost = 700
        max_cost = 1200
    elif cost_str == "Super Luxury Budget":
        min_cost = 1200
        max_cost = -99
    else:
        min_cost = 0
        max_cost = -99
    return min_cost,max_cost

def top_matching_string(str, arr):
    d = {}
    max = 0
    max_name =""
    for i in arr:
        sim = fuzz.token_sort_ratio(str,i)
        d[i] = sim
        if sim>=max:
            max = sim
            max_name = i
    d = [(k,v) for k,v in sorted(d.items(), key=lambda x: x[1], reverse=True) if v > 0.5][0:4]
    d_name = [k for k, v in d]
    d_sim = [v for k, v in d]
    return d_name,d_sim

def create_dynamic_button(lst,slot, intent):
    buttons = []
    for i in lst:
        n = '/'+intent+'{"'+slot+'": "'+i+'"}'
        buttons.append({'title': i, 'payload': '{}'.format(n)})
    n1 = '/'+intent+'{"'+slot+'": "'+"None"+'"}'
    buttons.append({'title': "None of these", 'payload': '{}'.format(n1)})
    return buttons

def create_dynamic_button_cuisine_subcat(lst,slot, intent):
    buttons = []
    for i in lst:
        n = '/'+intent+'{"'+slot+'": "'+i+'"}'
        buttons.append({'title': i, 'payload': '{}'.format(n)})
    n1 = '/'+intent+'{"'+slot+'": "'+"None"+'"}'
    buttons.append({'title': "Others", 'payload': '{}'.format(n1)})
    return buttons


def none_correction(str):
    if str == "None":
        return 0
    else:
        return 1


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "actions_get_restaurants"

    #def create_filters(city, cuisine,cost,rating):
        #if

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

                city = tracker.get_slot('slot_city_dym')
                cuisine = tracker.get_slot('slot_cuisine')
                cost = tracker.get_slot('slot_cost')
                rating = tracker.get_slot('slot_rating')
                cuisine_sub_category = tracker.get_slot('slot_cuisine_subcategory')
                min_cost,max_cost = cost_min_max(cost)
                data = pd.read_csv('/Users/trishakrishnan/Desktop/Great Learning Course/Capstone Project/RASA Trial/ZomatoFinal7.csv', lineterminator = '\n')
                data2 = data[
                (data['City']==city)
                &
                (data['Aggregate rating']>=rating_min_max(rating))
                &
                (data['Average Cost for two']>=min_cost) &
                (
                ((max_cost>=0) & (data['Average Cost for two']<max_cost)) | (max_cost<0)
                ) &
                ((none_correction(cuisine)>0) & data['Main_Cuisines'].str.contains(cuisine, na = False)) &
                (none_correction(cuisine_sub_category) & data['Sub_Cuisines'].str.contains(cuisine_sub_category, na = False))

                ]
                data3 = data2.sort_values('Votes', ascending = False).head()
                response1 = """Following are the recommended restaurants for you - """
                dispatcher.utter_message(response1)

                response =""
                i=1
                for index, row in data3.iterrows():
                    response = response + str(i)+". " + str(row['Restaurant Name']) + "\n"
                    #response = response + str(index)+". " + str(row['Restaurant Name']) + ' in ' + str(row['Address']) + ' has been rated ' + str(row['Aggregate rating'])+ "\n"
                    i = i+1
                dispatcher.utter_message(response)
                #dispatcher.utter_message("You can view other suggested restaurants here - ")
                return [FollowupAction('utter_continue_ind')]





    class set_city_slot(Action):

        def name(self) -> Text:
            return "action_city_input"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
           #city = e['value'] for e in tracker.latest_message['entities'] if e['entity'] == 'slot_city'
           #city = tracker.get_latest_entity_values('slot_city')
                city = ""
                city = tracker.get_slot('slot_city')
                #city = tracker.get_slot('slot_city')
           ## Apply fuzzy match
           ## Filter from dataset
                data = pd.read_csv('/Users/trishakrishnan/Desktop/Great Learning Course/Capstone Project/RASA Trial/ZomatoFinal7.csv', lineterminator = '\n')
                city_opt,sim = top_matching_string(city,data['City'].unique())
           #print(city)
           #dispatcher.utter_message(str(sim[0]))
                #buttons = [{'title': 'yes', 'payload': "Yes"}, {'title': 'no', 'payload': "No"}]
           #dispatcher.utter_message(sim[0])
                if sim[0] == 100:
                    return [SlotSet('slot_city_dym',city_opt[0]), FollowupAction('utter_cuisine')]
                else :
                    dispatcher.utter_button_message("We couldn't find an exact match for your search. Did you mean (Select closest option)- ",create_dynamic_button(city_opt,'slot_city_dym','choose_city_dym'))
                    return []


class set_city_slot_dym(Action):

    def name(self) -> Text:
        return "action_city_next_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

       city = tracker.get_slot("slot_city_dym")
       if city == 'None':
           name = 'utter_city'
           dispatcher.utter_message("Looks like we couldn't find the right match for your input. Could you please re-enter your city preference")
       else:
           name = 'utter_cuisine'
           dispatcher.utter_message("We service that city! Would like to ask you a couple more questions to give you the best recommendation")
       ## Apply fuzzy match
       ## Filter from dataset


       return [FollowupAction(name)]


    class set_cuisine_slot(Action):

        def name(self) -> Text:
            return "action_cuisine_subcategory_input"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

                city = tracker.get_slot('slot_city_dym')
                cuisine = tracker.get_slot('slot_cuisine')

                d = {"Indian": ["North Indian","South Indian","East Indian","West Indian"],
                "Asian": ["Chinese","Japanese","Thai"],
                "European": ["Italian","French"],
                "American": ["North American","South American"] }

                if (cuisine == "Any/Others"):
                    return [SlotSet('slot_cuisine_subcategory',"None"), FollowupAction('utter_cost')]

                else:
                    dispatcher.utter_button_message("Please select a cuisine subcategory- ",create_dynamic_button_cuisine_subcat(d[cuisine],'slot_cuisine_subcategory','choose_cuisine_subcategory'))
                    return []


    class set_cont_direction(Action):

        def name(self) -> Text:
            return "actions_cont_direction"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

           ind = tracker.get_slot("slot_cont_ind")
           if ind == 'Yes':
               name = 'utter_greet_city'
               dispatcher.utter_message("Great! Please answer a few questions to search for another restaurant")
           else:
               name = 'utter_feedback'
               dispatcher.utter_message("Thank you for searching for restaurants with Foodie. We would really appreciate your feedback")
               dispatcher.utter_message(image = 'https://d2slcw3kip6qmk.cloudfront.net/marketing/blog/2019Q1/giving-feedback/how-to-give-feedback-header@2x.png')
           return [FollowupAction(name)]
           ## Apply fuzzy match
           ## Filter from dataset
