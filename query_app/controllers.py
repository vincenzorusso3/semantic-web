#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON, XML


"""Routes for app."""
from functools import partial
from itertools import chain

from bs4 import BeautifulSoup
from flask import render_template, request, flash
from requests import post, codes

from .forms import SPARQLform
from .flask_app import app
from .models import Graph, NAMESPACES

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask import Markup


sparqlW = SPARQLWrapper("http://127.0.0.1:3030/Musei/query")
sparqlWInsert = SPARQLWrapper("http://127.0.0.1:3030/Musei/update")
graph = Graph()

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyD7LqLf5epwdL_UCS6xynHH5tjTuIuioqc"

# Initialize the extension
GoogleMaps(app)



@app.template_filter('namespace')
def abbreviate(data):
	if data is None:
		return ""
	for abbr, ns in NAMESPACES.items():
		if str(ns) in data:
			n = data.replace(str(ns), "{}:".format(abbr))
			return '<a href="{url}" title="{n}">{n}</a>'.format(url=data, n=n)
	return data


@app.route("/", methods=["GET"])
def home_page():
	"""Render the home page."""
	return render_template("home.html",
						   namespaces=NAMESPACES,
						   form=SPARQLform())

@app.route("/insert_opera", methods=["POST"])
def rs3():
	if request.form['insert_opera']=="Inserisci opera":
			nome_opera = request.form['opera']
			nome_autore = request.form['autore']
			nome_museo = request.form['museo']
			pittura_scultura = request.form.get('radiob')
			if pittura_scultura is None:
				pittura_scultura = 0
		
			ask = """
			PREFIX geonames: <https://www.geonames.org/ontology#>
			PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
			PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
			PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
			PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
			PREFIX owl: <http://www.w3.org/2002/07/owl#>
			PREFIX dbo: <http://dbpedia.org/resource/>
			ASK {
				?artista kb:nomeAutore """
			ask2= """\""""
			ask3 = """.}"""
			query = ask + ask2 + nome_autore + ask2 + ask3
			sparqlW.setQuery(query) 
			sparqlW.method = 'POST'
			resultQuery = sparqlW.query().convert()
			sparqlW.setReturnFormat(JSON)
			results = sparqlW.query().convert()

			if pittura_scultura != 0:

				if results["boolean"]:
					ask = """
					PREFIX geonames: <https://www.geonames.org/ontology#>
					PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
					PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
					PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
					PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
					PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
					PREFIX owl: <http://www.w3.org/2002/07/owl#>
					PREFIX dbo: <http://dbpedia.org/resource/>
					ASK {
						?museo geonames:name """
					ask2= """\""""
					ask3 = """.}"""
					query = ask + ask2 + nome_museo + ask2 + ask3
					sparqlW.setQuery(query) 
					sparqlW.method = 'POST'
					resultQuery = sparqlW.query().convert()
					sparqlW.setReturnFormat(JSON)
					results = sparqlW.query().convert()
					print(results)

					if results["boolean"]:
						query1 = """
						PREFIX geonames: <https://www.geonames.org/ontology#>
						PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
						PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
						PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
						PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
						PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
						PREFIX owl: <http://www.w3.org/2002/07/owl#>
						PREFIX dbo: <http://dbpedia.org/resource/>
						INSERT DATA{
						dbo:"""

						pittura_scultura = int(pittura_scultura)
						if pittura_scultura == 1:
							dipinto_scultura = "Dipinto"
							queryDipingeScolpisce = """ kb:dipinge dbo:"""
						elif pittura_scultura == 2:
							dipinto_scultura = "Scultura"
							queryDipingeScolpisce = """ kb:scolpisce dbo:"""


						query2 = """ rdfs:type kb:"""
						queryVirgola = """;"""
						query4 = """kb:haAutore dbo:"""
						query5 = """kb:conservata dbo:"""
						query6 = """kb:nomeOpera """
						queryApice = """\""""
						query7 = """.\n"""
						queryPunto = """. """
						queryKB = """dbo:"""
						query10 = """ kb:conserva dbo:"""
						query11 = """}"""
						nome_opera_trattino = nome_opera.replace(" ", "_")
						nome_museo_trattino = nome_museo.replace(" ", "_")
						nome_autore_trattino = nome_autore.replace(" ", "_")
						print(nome_opera_trattino)

						query =	query1 + nome_opera_trattino + query2 + dipinto_scultura + queryVirgola + query4 + nome_autore_trattino + queryVirgola + query5 + nome_museo_trattino + queryVirgola + query6 + queryApice + nome_opera + queryApice + query7 + queryKB + nome_autore_trattino + queryDipingeScolpisce + nome_opera_trattino + queryPunto + queryKB + nome_museo_trattino + query10 + nome_opera_trattino + queryPunto + query11
						
						"""Bacio_di_Giuda rdfs:type kb:Dipinto;
							kb:haAutore kb:Giotto;
							kb:conservata kb:Louvre;
							kb:nomeOpera "Bacio di Giuda".
						
						kb:Giotto kb:dipinge kb:Bacio_di_Giuda.
						kb:Louvre kb:conserva kb:Bacio_di_Giuda.
						}"""

						sparqlWInsert.setQuery(query) 
						sparqlWInsert.method = 'POST'
						sparqlWInsert.query()

						flash('Opera inserita correttamente', 'success')
						return render_template("result_insert.html",
									namespaces=NAMESPACES,
									form=SPARQLform()
									)

					else:
						flash('Museo non esistente', 'error')
						return render_template("result_insert.html",
									namespaces=NAMESPACES,
									form=SPARQLform()
									)
						
				else:
					flash('Autore non esistente', 'error')
					return render_template("result_insert.html",
									namespaces=NAMESPACES,
									form=SPARQLform()
									)

			else:
					flash('Indica il tipo di opera', 'error')
					return render_template("result_insert.html",
									namespaces=NAMESPACES,
									form=SPARQLform()
									)						


@app.route("/insert", methods=["POST"])
def rs2():
	if request.form['insert_autore']=="Inserisci autore":
		print("ciao pippo")
		form = SPARQLform()
		pittore = request.form.get('radiob1')
		scultore = request.form.get('radiob2')

		if pittore is None:
				pittore = 0
		pittore = int(pittore)

		if scultore is None:
			scultore = 0
		scultore = int(scultore)
		
		if scultore == 1 or pittore == 1:

			if pittore == 1 and scultore == 0:

				nomeAutore = request.form['nome_autore']
				nomeAutoreTrattino = nomeAutore.replace(" ", "_")
				query1 = """
				PREFIX geonames: <https://www.geonames.org/ontology#>
				PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
				PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
				PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
				PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
				PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
				PREFIX owl: <http://www.w3.org/2002/07/owl#>
				PREFIX dbo: <http://dbpedia.org/resource/>
				INSERT DATA{
				dbo:"""


				query2=""" rdfs:type kb:Pittore"""
				
				query4= """, owl:NamedIndividual; kb:nomeAutore \""""
				query3="""\".}"""    
				query = query1 + nomeAutoreTrattino + query2 + query4 + nomeAutore + query3
				print(query)
				sparqlWInsert.setQuery(query) 
				sparqlWInsert.method = 'POST'
				sparqlWInsert.query()
				flash('Autore inserito correttamente', 'success')
				return render_template("result_insert.html",
									namespaces=NAMESPACES,
									form=SPARQLform()
									)

			elif pittore == 0 and scultore == 1:

				nomeAutore = request.form['nome_autore']
				nomeAutoreTrattino = nomeAutore.replace(" ", "_")
				query1 = """
				PREFIX geonames: <https://www.geonames.org/ontology#>
				PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
				PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
				PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
				PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
				PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
				PREFIX owl: <http://www.w3.org/2002/07/owl#>
				PREFIX dbo: <http://dbpedia.org/resource/>
				INSERT DATA{
				dbo:"""


				query2=""" rdfs:type kb:Scultore"""
				
				query4= """, owl:NamedIndividual; kb:nomeAutore \""""
				query3="""\".}"""    
				query = query1 + nomeAutoreTrattino + query2 + query4 + nomeAutore + query3
				print(query)
				sparqlWInsert.setQuery(query) 
				sparqlWInsert.method = 'POST'
				sparqlWInsert.query()
				flash('Autore inserito correttamente', 'success')
				return render_template("result_insert.html",
									namespaces=NAMESPACES,
									form=SPARQLform()
									)

			elif pittore == 1 and scultore == 1:

				nomeAutore = request.form['nome_autore']
				nomeAutoreTrattino = nomeAutore.replace(" ", "_")
				query1 = """
				PREFIX geonames: <https://www.geonames.org/ontology#>
				PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
				PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
				PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
				PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
				PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
				PREFIX owl: <http://www.w3.org/2002/07/owl#>
				PREFIX dbo: <http://dbpedia.org/resource/>
				INSERT DATA{
				dbo:"""


				query2=""" rdfs:type kb:Scultore, kb:Pittore"""
				
				query4= """, owl:NamedIndividual; kb:nomeAutore \""""
				query3="""\".}"""    
				query = query1 + nomeAutoreTrattino + query2 + query4 + nomeAutore + query3
				print(query)
				sparqlWInsert.setQuery(query) 
				sparqlWInsert.method = 'POST'
				sparqlWInsert.query()

				flash('Autore inserito correttamente', 'success')
				return render_template("result_insert.html",
									namespaces=NAMESPACES,
									form=SPARQLform()
									)

			

		else:
			flash('Indica il tipo di artista', 'error')
			return render_template("result_insert.html",
									namespaces=NAMESPACES,
									form=SPARQLform()
									)		

	



@app.route("/", methods=["POST"])
def rs():
	if request.form['action']=="Query me":
		form = SPARQLform()
		query = request.form.get('query')
		sparqlW.setQuery(query)
		sparqlW.setReturnFormat(JSON)
		resultQuery = sparqlW.query().convert()
		results={}
		headers=[]
		headers.append("autore")
		headers.append("tizio")
		i = 0

		for result in resultQuery["results"]["bindings"]:
			print(result["autore"]["value"])
			results[str(i)]=(result["autore"]["value"])
			i += 1


		return render_template("result.html",
							namespaces=NAMESPACES,
							form=SPARQLform(),
							results=results,
							headers=headers
							)

	elif request.form['action']=="Ricerca Museo":

		"""Render the query result."""
		form = SPARQLform()
		museo = request.form.get('query')
		query1 = """
		PREFIX geonames: <https://www.geonames.org/ontology#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
		PREFIX dbo: <http://dbpedia.org/resource/>
		SELECT *
		WHERE{
			?museo geonames:name """
		query2 = "\""
		query3 = "\" ;"
		query4 = "geonames:lat ?latitude ;"
		query5 = "geonames:long ?longitude .}"
		query = query1 + query2 + museo + query3 + query4 + query5
		print(query)
		sparqlW.setQuery(query)
		sparqlW.setReturnFormat(JSON)
		resultQuery = sparqlW.query().convert()
		results={}
		headers=[]
		headers.append("museo")
		i = 0
		lat = 0
		lon = 0
		for result in resultQuery["results"]["bindings"]:
			print(result["museo"]["value"])
			results[str(i)]=(result["museo"]["value"])
			lat = result["latitude"]["value"]
			lon = result["longitude"]["value"]
			i += 1

		#############MAPS##########
			# creating a map in the view
		mymap = Map(
			identifier="view-side",
			lat=lat,
			lng=lon,
			markers=[(lat, lon)]
		)
		sndmap = Map(
			identifier="sndmap",
			lat=lat,
			lng=lon,
			markers=[
			{
				'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
				'lat': lat,
				'lng': lon,
				'infobox': "<b>Hello World</b>"
			},
			{
				'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
				'lat': lat,
				'lng': lon,
				'infobox': "<b>Hello World from other place</b>"
			}
			]
		)
		#############################
		print(lat)
		return render_template("map.html",
							namespaces=NAMESPACES,
							form=SPARQLform(),
							results=results,
							headers=headers,
							mymap=mymap,
							sndmap=sndmap,
							lat=lat,
							lon=lon
							)

	elif request.form['action']=="Ricerca autori in una determinata città":
		"""Render the query result."""
		form = SPARQLform()
		museo = request.form.get('query')
		query1 = """
		PREFIX geonames: <https://www.geonames.org/ontology#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
		PREFIX dbo: <http://dbpedia.org/resource/>
		SELECT DISTINCT ?autore
			WHERE{
			?musei geonames:locatedIn dbo:""" 
		query2 = "."
		query3 = "?opere kb:conservata ?musei . \n?opere kb:haAutore ?autore .}"
		query = query1 + museo + query2 + query3
		sparqlW.setQuery(query)
		sparqlW.setReturnFormat(JSON)
		resultQuery = sparqlW.query().convert()
		results={}
		headers=[]
		headers.append("autore")
		i = 0

		for result in resultQuery["results"]["bindings"]:
			print(result["autore"]["value"])
			results[str(i)]=(result["autore"]["value"])
			i += 1

		return render_template("result.html",
							namespaces=NAMESPACES,
							form=SPARQLform(),
							results=results,
							headers=headers
							)

	elif request.form['action']=="Ricerca elementi in una determinata città":
		"""Render the query result."""
		form = SPARQLform()
		museo = request.form.get('query')
		query1 = """
		PREFIX geonames: <https://www.geonames.org/ontology#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
		PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
		PREFIX dbo: <http://dbpedia.org/resource/>

		DESCRIBE ?opere
			WHERE {
				dbo:""" 
		query2 = " kb:ospita ?museo ."
		query3 = "?museo kb:conserva ?opere . }"
		query = query1 + museo + query2 + query3
		sparqlW.setQuery(query)
		sparqlW.setReturnFormat(JSON)
		resultQuery = sparqlW.query().convert()
		results={}
		headers=[]
		headers.append("istanze")
		i = 0

		resultQuery = resultQuery.serialize(format="turtle").decode("utf-8")

		#postString = resultQuery.split("\n",2)[2]

		text = resultQuery
		print(text)
		value = Markup(text)

		return render_template("result_string.html",
							namespaces=NAMESPACES,
							form=SPARQLform(),
							results=value,
							headers=headers
							)

	elif request.form['action']=="Ricerca autori esclusivi di un museo":
		"""Render the query result."""
		form = SPARQLform()
		museo = request.form.get('query')
		query1 = """
		PREFIX geonames: <https://www.geonames.org/ontology#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
		PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
		PREFIX owl: <http://www.w3.org/2002/07/owl#>
		PREFIX dbo: <http://dbpedia.org/resource/>
		PREFIX db: <http://dbpedia.org/>

		SELECT DISTINCT * WHERE {
		
		?museo kb:conserva ?opera .
		?museo geonames:name \""""
		
		query2 = """\" . ?opera kb:haAutore ?autore .
			FILTER NOT EXISTS{
				?museo2 kb:conserva ?opera2 .
				?opera2 kb:haAutore ?autore .
			FILTER (?museo2 != ?museo)
		} }"""
		query = query1 + museo + query2
		print(query)
		sparqlW.setQuery(query)
		sparqlW.setReturnFormat(JSON)
		resultQuery = sparqlW.query().convert()
		results={}
		headers=[]
		headers.append("autore")
		headers.append("opera")
		i = 0

		for result in resultQuery["results"]["bindings"]:
			results[str(i)]=[(result["autore"]["value"]), (result["opera"]["value"])]
			i += 1

		return render_template("result_2_column.html",
							namespaces=NAMESPACES,
							form=SPARQLform(),
							results=results,
							headers=headers
							)

	elif request.form['action']=="Distribuzione delle opere di un autore nei musei":
		"""Render the query result."""
		form = SPARQLform()
		autore = request.form.get('query')
		nome_autore_trattino = autore.replace(" ", "_")
		query1 = """
		PREFIX geonames: <https://www.geonames.org/ontology#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
		PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
		PREFIX owl: <http://www.w3.org/2002/07/owl#>
		PREFIX dbo: <http://dbpedia.org/resource/>
		PREFIX db: <http://dbpedia.org/>


		SELECT (SAMPLE(?museo) AS ?Museo) (COUNT(?opera) as ?NOpere)
		WHERE {
		{ dbo:"""
		
		query2 = """ kb:dipinge ?opera .
					?museo kb:conserva ?opera .
					}
					UNION
					{dbo:"""
		query3 = """ kb:scolpisce ?opera .
					?museo kb:conserva ?opera .
					}
					}
					GROUP BY ?museo
					ORDER BY ASC(?museo) """
		query = query1 + nome_autore_trattino + query2 + nome_autore_trattino + query3
		print(query)
		sparqlW.setQuery(query)
		sparqlW.setReturnFormat(JSON)
		resultQuery = sparqlW.query().convert()
		results={}
		headers=[]
		headers.append("Museo")
		headers.append("#Opere")
		i = 0
		print (resultQuery)
		for result in resultQuery["results"]["bindings"]:
			results[str(i)]=[(result["Museo"]["value"]), (result["NOpere"]["value"])]
			i += 1

		return render_template("result_2_column.html",
							namespaces=NAMESPACES,
							form=SPARQLform(),
							results=results,
							headers=headers
							)

	elif request.form['action']=="Musei ed opere di tutte le città":
		"""Render the query result."""
		form = SPARQLform()
		autore = request.form.get('query')
		nome_autore_trattino = autore.replace(" ", "_")
		query1 = """
		PREFIX geonames: <https://www.geonames.org/ontology#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX kb: <http://www.semanticweb.org/andrea/ontologies/2021/4/Musei#>
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
		PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
		PREFIX owl: <http://www.w3.org/2002/07/owl#>
		PREFIX dbo: <http://dbpedia.org/resource/>
		PREFIX db: <http://dbpedia.org/>


		CONSTRUCT{ 
		?citta kb:ospita _:v .
		_:v kb:museo ?museo .
		_:v kb:opera ?opere .
		}
		WHERE
		{
			{ ?citta kb:ospita ?museo } .
			{ ?museo kb:conserva ?opere } .
		}
		"""
		query = query1
		print(query)
		sparqlW.setQuery(query)
		sparqlW.setReturnFormat(JSON)
		resultQuery = sparqlW.query().convert()
		results={}
		headers=[]
		headers.append("istanze")
		i = 0


		resultQuery = resultQuery.serialize(format="turtle").decode("utf-8")

		#postString = resultQuery.split("\n",2)[2]

		text = resultQuery
		print(text)
		value = Markup(text)

		return render_template("result_string.html",
							namespaces=NAMESPACES,
							form=SPARQLform(),
							results=value,
							headers=headers
							)



def sparql_validate(query):
	prefix = "PREFIX {}: <{}>".format
	prefixes = "\n".join((prefix(ns, uri) for ns, uri in NAMESPACES.items()))
	query = prefixes + "\n\n" + query
	resp = post("http://sparql.org/validate/query", data=dict(query=query))
	if resp.status_code == codes.ok:
		soup = BeautifulSoup(resp.content.decode('utf-8'), "html.parser")
		pres = soup.find_all('pre')
		for p in pres:
			flash(p)
	else:
		flash("Unable to access query validation service.")
