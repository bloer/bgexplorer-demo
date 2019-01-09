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
from bgexplorer import create_app as base_app
from bgexplorer.bgmodelbuilder import units
from bgexplorer.bgmodelbuilder.simulationsdb.mongosimsdb import MongoSimsDB
from bgexplorer.bgmodelbuilder.simulationsdb.simdoceval import SpectrumAverage

def query(request):
    """Generate one or more mongodb query object for the provided request.  
    For each query generated, it should be registered to the request via
    `request.addquery`.
    Args:
        request (SimDataRequest): full component hierarchy and radioactive 
                                  emission spec to search for
    Returns:
        None
    """
    #build the default query for a radioactive isotope primary
    query = {
        'volume': request.component.name,
        'primary': request.spec.name,
        'spectrum': None
    }
    #take into account overrides
    MongoSimsDB.modquery(query, request)

    #register the default (possibly modified) query
    request.addquery(query)

    #TODO: handle neutron requests


def livetime(match, hits):
    """Calculate the livetime represented by a set of simulation data. 
    Required argument for MongoSimsDB. 

    Note that `match.emissionrate` can be given a weight when registered by
    `query`, so don't apply any weight here
    
    Args:
        match (SimDataMatch): info requested from model and DB response
        hits (list): List of all documents retrieved from the DB. These may 
                     be partial documents containing only livetime-relevant info
    Returns:
        livetime (float): the total summed livetime represented by the hits
    """
    nprimaries = sum(doc['nprimaries'] for doc in hits)
    #this function shouldn't be called if emissionrate==0
    return nprimaries / match.emissionrate

livetimeprojection = {'nprimaries':True}

    
#Generate tables with the average rate of gamma-induced events 
detector_mass = 800 * units.g
ranges = [ (0.1, 5), (3, 100), (10, 2000) ]
values = {'Gammas, {}-{} keV'.format(*r) : 
          SpectrumAverage('hits.gammas', r[0]*units.keV, r[1]*units.keV,
                          binskey='hits.gammas_bins', binsunit='keV',
                          scale = 1./detector_mass)
          for r in ranges}
values_units = {key:'dru' for key in values}
                          

def create_app(cfgfile='config.default.py'):
    """Create the base Flask bgexplorer app"""
    app = base_app(cfgfile, values=values, values_units=values_units)
    
    #now set up the database connection
    client = pymongo.MongoClient(app.config['SIMDB_URI'])
    db = client[app.config['SIMDB_DATABASE']]
    collection = db[app.config['SIMDB_COLLECTION']]
    
    MongoSimsDB(collection, query, livetime, livetimeprojection, app=app)

    #add some custom views
    modelviewer = app.extensions['ModelViewer']

    @app.template_global()
    def getlivetime(component, primary):
        return sum( sum(match.livetime for match in req.matches 
                        if match.query['primary'] == primary)
                    for req in component.getsimdata(children=False) )
    
    @modelviewer.bp.route('/simlivetime')
    def simlivetime():
        return render_template('simlivetime.html')

    @modelviewer.bp.route('/customview')
    def customview():
        return render_template('customview.html')
    
    return app
