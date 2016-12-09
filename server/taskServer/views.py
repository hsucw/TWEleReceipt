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

    state = DB.getStatisticDataByToken( token )

    status = state['status']
    data = state['data']


    if status == 'error':
        return HttpResponse( data )
    elif status == 'pending':
        return HttpResponse( 'Your request is pending' )

    taxId = state['taxId']


    #
    #token = request.GET.get( 'token' )
    #if token is None:
    #    return HttpResponse( "Token Empty" )

    #queryDates = handler.getDateRangeFromToken( token )


    dataset = { 'freq':[], 'summed':[] }
    colors = [ "rgba(25,59,48,1)", "rgba(255,149,0,1)", "rgba(76,217,100,1)", "rgba(0,122,255,1)", "rgba(88,86,214,1)" ];
    colorsAlpha = [ "rgba(25,59,48,1)", "rgba(255,149,0,1)", "rgba(76,217,100,1)", "rgba(0,122,255,1)", "rgba(88,86,214,1)" ];

    colorCnt = 0

    targetPath = DATABASE_DIRECTORY + taxId + '/'

    for filename in os.listdir(targetPath):

        for matchFileName in data:


            if filename.__contains__( matchFileName ):

                type = None

                if filename.__contains__( 'freq' ):
                    type = 'freq'
                elif filename.__contains__( 'norm' ):
                    type = 'norm'
                else :
                    continue


                data = []
                csvfile = open( targetPath+filename , 'rb')  # 1
                for row in csv.reader(csvfile):  # 2
                    data.append( float(row[0]) )

                labelDate = filename[:4] + '-' + filename[4:6] + "-" + filename[6:8]

                dataset[type].append({
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
