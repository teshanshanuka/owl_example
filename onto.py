# Author: Teshan Liyanage <teshanl@zone24x7.com>

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
rdf_filename = "misc/car.rdf"


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
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n"""

        output = {}
        query = ''

        if request.method == 'POST':
            query = request.form['query']

            cols = query.split('WHERE')[0].split()
            cols = [s.strip('?') for s in cols if s.startswith('?')]

            query = base_query + query

        try:
            results = graph.query(query)
            data = []
            for s in results:
                if not any(isinstance(x, rdflib.term.BNode) for x in s):
                    data.append([x.replace(x.defrag() + "#", '') for x in s])

            output = {'columns': cols,
                      'data': data}

            flash('Results ready!')
        except pyparsing.ParseException:
            print("ERROR: query entered...\n", query)
            flash('Error: Invald Query')

        return render_template('home.html', form=form, title="Car", output=output)


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
