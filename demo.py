"""
@file demo.py
@author B. Loer
@date 2018-11-20

This is an example server using the background explorer framework. 
Fake simulation files are stored in data/ and have the following structure:
{ 'nprimaries': <# of initial radioactive decay particles simulated>,
  'volume'    : <name of the MC volume where primaries were seeded>,
  'primary'  : <name (or isotope) of the primary particle>,
  'spectrum'  : <initial spectrum of primary particles>,
  'hits': { <a dict of spectra for different hit types>
      'gammas': [<list of gamma counts (not normalized to bin width)>],
      'gammas_bins': [<list of gamma bin edges in keV>],
      'neutrons': [<list of neutron counts>],
      'neutrons_bins': [<list of neutron bin edges in keV>],
  }
}

At startup, these files are inserted into a mongodb collection. A separate 
collection is set up for storing bgmodel objects. Some examples are in models/.

This file demonstrates the function pointers that need to be provided to the
mongosimsdb class in order to properly interpret and normalize the data files. 
Also demonstrated is the procedure to add new views to the list of links
pre-provided by background explorer.

"""

import os
import pymongo
import bgexplorer
import numpy as np
from bgexplorer import create_app as base_app
from bgexplorer.bgmodelbuilder import units
from bgexplorer.bgmodelbuilder.simulationsdb.mongosimsdb import MongoSimsDB
from bgexplorer.bgmodelbuilder.simulationsdb.simdoceval import SpectrumAverage
from bgexplorer.bgmodelbuilder.utilities import Isotope
from flask import g, render_template
import logging
log = logging.getLogger(__name__)

def query(request):
    """Generate one or more mongodb query object for the provided request.  
    If only a single query is generated, just return the (modified) `request`
    object. If additional queries are needed (e.g. generating both 
    gamma and neutron primaries), return a list of SimDataMatch objects. 
    Use `request.clone` to generate the additional matches.

    If for some reason a query cannot be generated, e.g. the match is somehow
    ill-formed, either return None to silently ignore, or call 
    `request.addstatus('error')` before returning.  Either way, log a warning
    or error message so it can be diagnosed later!

    Args:
        request (SimDataMatch): full component hierarchy and radioactive 
                                emission spec to search for, with initially
                                empty `query`. 
    Returns:
        matches: original 
    """
    # build the default query for a radioactive isotope primary
    primary = None
    try:
        primary = Isotope(request.spec.name).format("{Z}-{A}")
    except Exception as e: 
        #not sure what kind of exceptions get thrown here...
        log.error("Can not interpret spec name '%s' as isotope!: %s",
                  request.spec.name, e)
        request.addstatus('error')

    query = {
        'volume': request.component.name,
        'primary': primary,
        'spectrum': None
    }
    # take into account overrides
    MongoSimsDB.modquery(query, request)

    # register the default (possibly modified) query
    request.query = query

    # TODO: handle neutron requests
    
    return request

def livetime(match, hits):
    """Calculate the livetime represented by a set of simulation data. 
    Required argument for MongoSimsDB. 

    Note that `match.emissionrate` can be given a weight when registered by
    `query`, so don't apply any weight here
    
    Args:
        match (SimDataMatch): info requested from model and DB response
        hits (list): List of all documents retrieved from the DB. These may 
                     be partial docs containing only livetime-relevant info
    Returns:
        livetime (float): the total summed livetime represented by the hits
    """
    nprimaries = sum(doc['nprimaries'] for doc in hits)
    #this function shouldn't be called if emissionrate==0
    return nprimaries / match.emissionrate


livetimeprojection = {'nprimaries': True}

    
#Generate tables with the average rate of gamma-induced events 
detector_mass = 800 * units.g
ranges = [(0.1, 5), (3, 100), (10, 2000)]
#these spectra are single-keV bins, from 0-3 MeV
bins = np.arange(0, 3001)
values = {'Gammas, {}-{} keV'.format(*r): 
          SpectrumAverage('hits', r[0] * units.keV, r[1] * units.keV,
                          binwidths=False,
                          bin_edges=bins, binsunit=units.keV, 
                          #could use this if bins are provided in entry:
                          #binskey='hits.gammas_bins', 
                          scale=1. / detector_mass)
          for r in ranges}
values_units = {key: 'dru' for key in values}
                          

def create_app(cfgfile='config.default.py'):
    """Create the base Flask bgexplorer app"""
    app = base_app(cfgfile, values=values, values_units=values_units)
    
    #now set up the database connection
    client = pymongo.MongoClient(app.config['SIMDB_URI'])
    db = client[app.config['SIMDB_DATABASE']]
    collection = db[app.config['SIMDB_COLLECTION']]
    
    MongoSimsDB(collection, query, livetime, livetimeprojection, app=app)

    #add some custom views
    modelviewer = app.blueprints['modelviewer']
    custom = app.blueprints['custom']
    simsviewer = app.extensions['SimulationsViewer']
    simsviewer.summarypro = {
                             'id': '$_id',
                             'volume': 1,
                             'primary': 1,
                             'nprimaries': 1,
                             #only works on >3.2
                             #'totalhits': {'$sum':'hits'},
                           }
    simsviewer.summarycolumns = ['volume','primary','nprimaries']

    @app.template_global()
    def getlivetime(component, primary):
        return sum(sum(match.livetime for match in req.matches 
                       if match.query['primary'] == primary)
                   for req in component.getsimdata(children=False))
    
    @modelviewer.route('/simlivetime/')
    def simlivetime():
        return render_template('simlivetime.html')
    
    @custom.route('/customview/')
    def customview():
        return render_template('customview.html')
    

    #need to re-register blueprints after they've been modified!
    app.register_blueprint(modelviewer)
    app.register_blueprint(custom)
        
    return app


if __name__ == '__main__':
    import sys
    app = create_app(sys.argv[1]) if len(sys.argv) > 1 else create_app()
    app.run(host='0.0.0.0')
