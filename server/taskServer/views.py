from datetime import datetime
from django.shortcuts import render
import os
import fnmatch
import DB
import csv
from django.http import HttpResponse

DATABASE_DIRECTORY = '../analysis/data/'

def addTask( request ):

    return render( request, "index.html", {

    })


def showStatistics(request, token = None):


    if token is None:
        return HttpResponse( "Invalid Token" )

    taxId = DB.getStatisticDataByToken( token )

    if taxId is None:
        return HttpResponse( "Invalid Token" )



    #
    #token = request.GET.get( 'token' )
    #if token is None:
    #    return HttpResponse( "Token Empty" )

    #queryDates = handler.getDateRangeFromToken( token )


    dataset = { 'freq':[], 'summed':[] }
    colors = [ "rgba(25,59,48,1)", "rgba(255,149,0,1)", "rgba(76,217,100,1)", "rgba(0,122,255,1)", "rgba(88,86,214,1)" ];
    colorsAlpha = [ "rgba(25,59,48,1)", "rgba(255,149,0,1)", "rgba(76,217,100,1)", "rgba(0,122,255,1)", "rgba(88,86,214,1)" ];

    colorCnt = 0
    for filename in os.listdir(DATABASE_DIRECTORY):
        if fnmatch.fnmatch( filename, '*.csv' ) and len( filename[:-4] ) == 8:
            data = []
            csvfile = open( DATABASE_DIRECTORY+filename , 'rb')  # 1
            for row in csv.reader(csvfile):  # 2
                data.append( float(row[0]) )

            labelDate = filename[:4] + '-' + filename[4:6] + "-" + filename[6:8]

            dataset['summed'].append({
                'labels': labelDate,
                'backgroundColor': colorsAlpha[colorCnt],
                'borderColor': colors[colorCnt],
                'pointBorderColor': colors[colorCnt],
                'pointHoverBackgroundColor': colors[colorCnt],
                'pointHoverBorderColor': colors[colorCnt],
                'data': data
            })

            colorCnt+=1



    for filename in os.listdir(DATABASE_DIRECTORY):
        if fnmatch.fnmatch(filename, 'money.csv'):
            data = []
            csvfile = open(DATABASE_DIRECTORY + filename, 'rb')  # 1
            for row in csv.reader(csvfile):  # 2
                data.append(float(row[0]))

            labelDate = filename

            dataset['freq'].append({
                'labels': labelDate,
                'backgroundColor': colorsAlpha[colorCnt],
                'borderColor': colors[colorCnt],
                'pointBorderColor': colors[colorCnt],
                'pointHoverBackgroundColor': colors[colorCnt],
                'pointHoverBorderColor': colors[colorCnt],
                'data': data
            })
            colorCnt+=1



    return render( request, "displayStatistics.html", {
        'dataset' : dataset
    })

# Create your views here.
