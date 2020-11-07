# Author: Isuru Kalhara
# Reference : https://pythonspot.com/flask-web-forms/

import os
import sys

import pyparsing
import rdflib
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, validators

from owlready2 import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

sql_filename = "misc/file.sqlite3"
rdf_filename = "misc/toyota.rdf"


class ReusableForm(Form):
    query = TextField('Query:', validators=[validators.data_required()])

    @app.route("/", methods=['GET', 'POST'])
    def hello():
        global graph
        form = ReusableForm(request.form)
        if form.errors:
            print(form.errors)

        base_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX : <http://www.semanticweb.org/isuru/ontologies/2020/10/toyota_vehicles#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n"""

        output = {}
        query = ''
        filter = False

        if request.method == 'POST':

            if(request.form['but1']=='cars'):
                query = '''SELECT ?Cars ?Price ?MPG ?Year ?Seat 
                WHERE { 
                    ?Cars rdf:type :Cars.
                    ?Cars :hasPriceValue ?Price.
                    ?Cars :hasCombinedMPGValue ?MPG.
                    ?Cars :hasManufacturedYear ?Year.
                    ?Cars :hasSeatingValue ?Seat.
                }'''

            elif(request.form['but1']=='hybrid'):
                query = '''SELECT ?HybridAndFuelCell ?Price ?MPG ?Year ?Seat 
                WHERE { 
                    ?HybridAndFuelCell rdf:type :HybridAndFuelCells.
                    ?HybridAndFuelCell :hasPriceValue ?Price.
                    ?HybridAndFuelCell :hasCombinedMPGValue ?MPG.
                    ?HybridAndFuelCell :hasManufacturedYear ?Year.
                    ?HybridAndFuelCell :hasSeatingValue ?Seat.
                }'''

            elif(request.form['but1']=='crossovers'):
                query = '''SELECT ?Crossovers ?Price ?MPG ?Year ?Seat 
                WHERE { 
                    ?Crossovers rdf:type :Crossovers.
                    ?Crossovers :hasPriceValue ?Price.
                    ?Crossovers :hasCombinedMPGValue ?MPG.
                    ?Crossovers :hasManufacturedYear ?Year.
                    ?Crossovers :hasSeatingValue ?Seat.
                }'''

            elif(request.form['but1']=='suvs'):
                query = '''SELECT ?SUVs ?Price ?MPG ?Year ?Seat 
                WHERE { 
                    ?SUVs rdf:type :SUVs.
                    ?SUVs :hasPriceValue ?Price.
                    ?SUVs :hasCombinedMPGValue ?MPG.
                    ?SUVs :hasManufacturedYear ?Year.
                    ?SUVs :hasSeatingValue ?Seat.
                }'''

            elif(request.form['but1']=='trucks'):
                query = '''SELECT ?Trucks ?Price ?MPG ?Year ?Seat 
                WHERE { 
                    ?Trucks rdf:type :Trucks.
                    ?Trucks :hasPriceValue ?Price.
                    ?Trucks :hasCombinedMPGValue ?MPG.
                    ?Trucks :hasManufacturedYear ?Year.
                    ?Trucks :hasSeatingValue ?Seat.
                }'''

            elif(request.form['but1']=='minivans'):
                query = '''SELECT ?Minivan ?Price ?MPG ?Year ?Seat 
                WHERE { 
                    ?Minivan rdf:type :Minivan.
                    ?Minivan :hasPriceValue ?Price.
                    ?Minivan :hasCombinedMPGValue ?MPG.
                    ?Minivan :hasManufacturedYear ?Year.
                    ?Minivan :hasSeatingValue ?Seat.
                }'''
            elif(request.form['but1']=='all'):
                query = '''SELECT ?Vehicle ?Price ?MPG ?Year ?Seat 
                WHERE {
                    ?Vehicle rdf:type owl:NamedIndividual.
                    ?Vehicle :hasPriceValue ?Price.
                    ?Vehicle :hasCombinedMPGValue ?MPG.
                    ?Vehicle :hasManufacturedYear ?Year.
                    ?Vehicle :hasSeatingValue ?Seat.
                }'''

            elif(request.form['but1']=='four'):
                query = '''SELECT ?FourCylinder ?EngineCapacity ?HorsePower
                WHERE {
                    ?FourCylinder rdf:type :4Cylinder .
                    ?FourCylinder :hasEngineCapacityValue ?EngineCapacity.
                    ?FourCylinder :hasEngineHorsePowerValue ?HorsePower.
                }'''

            elif(request.form['but1']=='six'):
                query = '''SELECT ?SixCylinder ?EngineCapacity ?HorsePower
                WHERE {
                    ?SixCylinder rdf:type :6Cylinder .
                    ?SixCylinder :hasEngineCapacityValue ?EngineCapacity.
                    ?SixCylinder :hasEngineHorsePowerValue ?HorsePower.
                }'''

            elif(request.form['but1']=='eight'):
                query = '''SELECT ?EightCylinder ?EngineCapacity ?HorsePower
                WHERE {
                    ?EightCylinder rdf:type :8Cylinder .
                    ?EightCylinder :hasEngineCapacityValue ?EngineCapacity.
                    ?EightCylinder :hasEngineHorsePowerValue ?HorsePower.
                }'''
                #query = 'SELECT ?EightCylinder  WHERE { ?EightCylinder rdf:type :8Cylinder }'

            else:
                price = request.form['query']
                filter = True
                query = '''SELECT ?Vehicle ?Price
                WHERE {
                    ?Vehicle rdf:type owl:NamedIndividual.
                    ?Vehicle :hasPriceValue ?Price.
                }'''
                print(price)
                print(type(price))
            
            print("\n",type(query))
            print (".......",query,"............")
            cols = query.split('WHERE')[0].split()
            cols = [s.strip('?') for s in cols if s.startswith('?')]

            query = base_query + query

        try:
            results = graph.query(query)
            
            data = []
            for s in results:
                if not any(isinstance(x, rdflib.term.BNode) for x in s):
                    temp = []
                    for x in s:
                        if isinstance(x,rdflib.term.Literal):
                            if(filter):
                                if(x > price):
                                    temp = []
                                    break
                            temp.append(x)
                        else:
                            temp.append(x.replace(x.defrag() + "#", ''))
                    if temp : 
                        data.append(temp)
                    #print([isinstance(x,rdflib.term.URIRef) for x in s])
                    

            output = {'columns': cols,
                      'data': data}

            flash('Results ready!')
        except pyparsing.ParseException:
            print("ERROR: query entered...\n", query)
            flash('Error: Invald Query')

        return render_template('home.html', form=form, title="Toyota", output=output)


if __name__ == "__main__":
    if os.path.isfile(sql_filename):
        os.remove(sql_filename)

    if not os.path.isfile(rdf_filename):
        print(f"RDF file '{rdf_filename}' not found")
        sys.exit(1)

    default_world.set_backend(filename=sql_filename)
    onto = get_ontology(rdf_filename).load()
    graph = default_world.as_rdflib_graph()

    app.run(debug=True)
