#!/usr/local/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tigarner'
import os
import logging
from jinja2 import Environment, FileSystemLoader
from ftplib import FTP



def create_graph(values):
    '''
    Creates a graph out of the dictionary passed in.
    Dictionary should contain: total, total_compt, sprint_indv, funathon_indv, sprint_team, funathon_team
    with a tuple for each part.
    '''

    #Get Path
    _path = os.path.dirname(os.path.realpath(__file__))

    #Start Logging
    logging.basicConfig(filename=_path + '/grapher.log',level=logging.DEBUG)

    graph_data = [
        ['Event',                   '2013 So Far',              '2012'],
        ['Total Competitors',       values['total_compt'][0],   values['total_compt'][1]],
        ['Sprint Individual',       values['sprint_indv'][0],   values['sprint_indv'][1]],
        ['Funathon Individual',     values['funathon_indv'][0], values['funathon_indv'][1]],
        ['Sprint Relay',            values['sprint_team'][0],   values['sprint_team'][1]],
        ['Funathon Relay',          values['funathon_team'][0],   values['funathon_team'][1]]
    ]

    gauge_data = [
        ['Label', 'Value'],
        ['Total Raised', values['total']]
    ]

    #Load the template and render using calculated values, save to graph.php
    env = Environment(loader=FileSystemLoader(_path))
    template = env.get_template('graph.html')
    graph = open(_path + '/graph.php', 'w+')
    graph.write(template.render(graph_data=graph_data, gauge_data=gauge_data).encode('utf-8'))
    graph.close()

    #Upload the final file to the server
    ftp = FTP('ftp.greenparktriathlon.co.uk', 'greenparktriathlon.co.uk', 'kC!9Eybts')
    ftp.storlines('STOR /public_html/graph.php', open(_path + '/graph.php','r'))


if __name__ == '__main__':
    create_graph(values=
                        {
                            'total':7136,
                            'total_compt': (252,306),
                            'sprint_indv': (117, 76),
                            'funathon_indv': (28, 39),
                            'sprint_team': (29, 44),
                            'funathon_team': (9, 22)
                        }
                        )