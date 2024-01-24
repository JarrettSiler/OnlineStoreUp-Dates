import json #used for getting input from html pages
from flask import request
from flask import Flask, render_template

import os
#import WebScraper #custom class that scrapes OfferUp

import sys
import sqlite3

app = Flask(__name__,template_folder='../templates')

@app.route('/')
def new_Watchlist():
    return render_template('WatchList.html') #change this later, made to create a new database

@app.route('/test', methods=['POST']) #listens for some data coming in from the html file for the url "/test"
def create_new_db():
    output = request.get_json() 
    #print(output) #debugging
    newitem = output['itemToSearch']
    newlocation = output['cityToSearch']
    newitem = newitem.replace(" ", "") #remove all whitespaces
    newlocation = newlocation.replace(" ", "") #remove all whitespaces

    #connection = sqlite3.connect(newitem + newlocation + ".db") #will create file if non-existant, otherwise, will just connect
    #connection.close()

    return output #returns new db to create

if __name__ == "__main__":
    app.run(debug=True)

#def scrape_Marketplace(file_path): #work on this
    