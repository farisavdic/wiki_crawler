# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from requests.utils import quote
import networkx as nx
import os.path
import matplotlib.pyplot as plt
from random import sample

"""
Created on Tue Feb  9 13:52:10 2021
Ein Webcrawler, der Wikipedia-Einträge indexieren soll, sodass diese im 
Nachhinein auf strukturelle und inhaltliche Besonderheiten untersucht werden 
können.
@author: Faris Avdic
"""


class Webcrawler:
    """
    Eine Klasse, die einen Webcrawler implementiert. Der Webcrawler startet
    die Indexierung und führt diverse Tests aus.

    Attribute
    ---------
    graph: networkx.DiGraph
        Der Graph, der bei der Indexierung erstellt wird.

    Methoden
    --------
    initializeGraph()
        initialisiert das Attribut graph
    finishGraph()
        speichert den Graphen als xml-Datei im GraphML-Format
    resetGraph()
        setzt den Graphen zurück
    start(url,layers)
        startet eine Indexierung von url mit layers Ebenen
    getRandomURL()
        gibt die URL zu einem zufälligen Wikipedia-Artikel zurück
    createGraph(layers)
        ruft start() auf, fängt evtl. auftretende Fehler ab
    drawGraph()
        zeichnet den Graphen
    saveGraphImage()
        speichert das Bild des Graphen als png-Datei
    testNodeIncrease(runs,layers)
        Führt den Test aus Kapitel 5.1 der Seminararbeit durch
    testShortestPath()
        Führt den Test aus Kapitel 5.3 der Seminararbeit durch
    testCycles()
        Führt den Test aus Kapitel 5.2 der Seminararbeit durch
    """

    def __init__(self):
        """
        Konstruktor der Klasse Webcrawler.

        Rückgabe
        --------
        None
        """
        self.graph = self.initializeGraph()

    def initializeGraph(self):
        """
        Initialisiert das Attribut graph des Webcrawlers. Wenn eine
        Datei "graph.xml" existiert, wird diese eingelesen und dem Attribut
        zugeordnet.
        Existiert die Datei nicht, wird dem Attribut ein neues Objekt der
        Klasse networkx.DiGraph zugeordnet.

        Rückgabe
        --------
        tempGraph : networkx.DiGraph
            Gerichteter Graph
        """
        if os.path.isfile("graph.xml"):
            tempGraph = nx.read_graphml("graph.xml")
            print("Graph exists and is read")
        else:
            tempGraph = nx.DiGraph()
            print("Graph doesn't exist and has been created")
        print("Initialized.")
        return tempGraph

    def finishGraph(self):
        """
        Schleißt die Arbeit am Graphen ab, indem die Anzahl der Knoten über
        die Konsole ausgegeben wird und der Graph im GraphML-Format
        als xml-Datei gespeichert wird.

        Returns
        -------
        None
        """
        print("The graph consists of " + str(
            self.graph.number_of_nodes()) + " nodes.")
        nx.write_graphml(self.graph, "graph.xml")
        print("Finished.")

    def resetGraph(self):
        """
        Setzt den Graphen zurück, indem die Datei "graph.xml" gelöscht wird.

        Rückgabe
        --------
        None
        """
        try:
            os.remove("graph.xml")
            print("Graph reset successful.")
        except Exception as e:
            print("Graph reset failed.")
            print(e)

    def start(self, url, layers):
        """
        Startet die Indexierung.
        Parameter
        ---------
        url : str
            Die URL des Eintrags, bei dem die Indexierung beginnen soll.
        layers : int
            Anzahl der Ebenen, in denen die Indexierung durchgeführt werden soll.
            layers = 0 -> Nur die Links, die im Start-Eintrag gefunden werden,
                werden indexiert.
            layers = 1 -> Start-Eintrag, direkt verlinkte Einträge und alle
                dort gefunden Links werden indexiert.

        Rückgabe
        --------
        res : list
            Vielfach verschachtelte Liste, die alle gefundenen Einträge
            beinhaltet.
            In Baumstruktur umwandelbar.
        """
        startEntry = Eintrag(url, url, self)
        print("Start at: " + startEntry.title)
        res = startEntry.index(layers, self)
        print("Finished")
        return res

    def getRandomURL(self):
        """
        Gibt die URL zu einem zufälligen Wikipedia-Eintrag zurück.
        Die Funktion nutzt die "Zufälliger Artikel"-Funktion von Wikipedia.

        Rückgabe
        --------
        url : str
        URL zu einem zufälligen Wikipedia-Eintrag
        """
        res = requests.get(
            "https://de.wikipedia.org/wiki/Spezial:Zuf%C3%A4llige_Seite").text
        soup = BeautifulSoup(res, 'html.parser')
        title = soup.find('title').text
        newTitle = title.replace(' – Wikipedia', '')
        urlText = quote(newTitle, safe='')
        url = "http://de.wikipedia.org/wiki/" + urlText
        return url

    def createGraph(self, layers):
        """
        Startet eine Indexierung über layers Ebenen.
        Ruft nur start() auf, schließt Methode aber in eine
        try-except-Anweisung ein, was ermöglicht, dass das Programm auch bei
        Fehlermeldungen normal beendet werden kann und nicht der gesamte
        Fortschritt der Indexierung verloren geht.

        Parameters
        ----------
        layers : int
            Anzahl der Untersuchungsebenen bei der Indexierung

        Rückgabe
        --------
        None
        """

        try:
            self.start(self.getRandomURL(), layers)
            print("SUCCESSFULLY FINISHED RUN.")
        except Exception as e:
            print("AN ERROR HAS OCCURED.")
            print(e)

    def drawGraph(self):
        """
        Zeichnet ein Bild des Graphen mit dem "random"-Layout.
        Bild wird im "Plots"-Fenster von Spyder angezeigt.

        Rückgabe
        --------
        None
        """
        print("Generating layout.")
        pos = nx.random_layout(self.graph)
        print("Finished generating layout.")
        print("Drawing graph.")
        nx.draw(self.graph, pos, node_size=1, width=0.1,
                node_color="#A0CBE2", with_labels=False, arrowsize=1)
        print("Finished drawing graph.")

    def saveGraphImage(self):
        """
        Speichert das Bild des Graphen als png-Datei.

        Rückgabe
        --------
        None
        """
        print("Saving image to file.")
        plt.savefig("graph.png", dpi=2000)
        print("Finished saving image to file.")

    def testNodeIncrease(self, runs, layers):
        """
        Untersucht den Graph auf sein Wachstumsverhalten bei steigender
        Anzahl von Untersuchungsebenen.
        Die Indexierung startet von einem Artikel ausgehend mit nur einen
        Durchsuchungsebene. Nach diesem ersten Durchlauf wird von jedem der
        Endknoten des Graphen (Grad 1) eine neue Indexierug über eine
        Durchsuchungsebene gestartet. Der Prozess wird so lange wiederholt,
        bis insgesamt layers Ebenen durchsucht wurden.
        Die Anzahl der Knoten, aus denen der Graph besteht wird nach jeder
        Iteration in einer Textdatei gespeichert und über die Konsole
        ausgegeben.

        Parameter
        ---------
        runs : int
            Anzahl der Wiederholungen des Versuchs
        layers : int
            Anzahl der maximalen Durchsuchungsebenen bei der Indexierung

        Rückgabe
        --------
        None
        """
        self.resetGraph()
        for i in range(runs):
            url = self.getRandomURL()
            self.start(url, 0)
            string = str(i) + ".0: " + str(self.graph.number_of_nodes()) + "\n"
            print(string)
            with open("testNodeIncrease.txt", "a") as file:
                file.write(string)
            for c in range(layers):
                nodeList = self.graph.nodes()
                endList = []
                for n in nodeList:
                    if self.graph.degree(n) == 1:
                        endList.append(n)
                for e in endList:
                    self.start(e, 0)
                string = str(i) + "." + str(c) + ": " + str(
                    self.graph.number_of_nodes())
                print(string)
                with open("testNodeIncrease.txt", "a") as file:
                    file.write(string)

    def testShortestPath(self):
        """
        Erstellt eine ungerichtete Kopie des Graphen aus dem Attribut
        graph.
        Sucht den kürzesten Weg zwischen zwei zufälligen Knoten im
        ungerichteten Graphen.
        Speichert jeden einzelnen Knoten des Pfades in einer Textdatei und
        gibt den Pfad über die Konsole aus.

        Rückgabe
        --------
        None
        """
        uGraph = nx.to_undirected(self.graph)
        randomNodes = sample(uGraph.nodes(), 2)
        randomNode1 = str(randomNodes[0])
        randomNode2 = str(randomNodes[1])
        print("rand1: " + randomNode1)
        print("rand2: " + randomNode2)
        try:
            shortestPath = nx.shortest_path(uGraph, randomNode1, randomNode2)
            with open("paths.txt", "a") as file:
                for i in shortestPath:
                    print(i)
                    file.write(i + "\n")
                file.write("--------------------------")
        except Exception as e:
            print(e)

    def testCycles(self):
        """
        Macht aus einem gerichteten Graphen einen ungerichteten und sucht
        alle Zyklen im Graphen heraus.
        Gibt Anzahl der gefundenen Zyklen über die Konsole aus.

        Rückgabe
        --------
        int
            Anzahl der Zyklen im Graphen
        """
        uGraph = self.graph.to_undirected()
        cycleList = list(nx.cycle_basis(uGraph))
        print(len(cycleList))
        return len(cycleList)


class Eintrag:
    """
    Eine Klasse, die einen Wikipedia-Eintrag mit allen wichtigen Informationen
    repräsentiert.

    Attribute
    ---------
    url : str
        Die URL des Wikipedia-Eintrags als String.
        Wird verwendet um Einträge eindeutig zu identifizieren.
    source : str
        Die URL des Eintrags, in dem der Hyperlink zum aktuellen Eintrag
        gefunden wurde.
    html : str
        Der HTML-Code des Wikipedia-Eintrags.
    text : str
        Der Text auf der Wikipedia-Seite.
    title : str
        Der Titel des Wikipedia-Eintrags.
    links : list
        Eine Liste mit allen Hyperlinks, die im HTML-Code des Eintrags
        gefunden wurden.
        Die Liste beinhaltet nur die Links, die auch zu anderen
        Wikipedia-Einträgen führen.
        Diskussions- und Spezialseiten werden vorher herausgefiltert.
    leaves : list
        Eine Liste mit anderen Objekten der Klasse Eintrag.
        Speichert alle Einträge, zu denen Hyperlinks im Code des aktuellen
        Eintrags führen.
    crawler : Webcrawler
        Der Webcrawler, der die aktuelle Indexierung ausführt.
        Attribut nötig, um dem Graphen Knoten hinzufügen zu können.

    Methoden
    --------
    index(layers, crawler)
        Rekursive Methode, die Wikipedia-Einträge indexiert.
    getLinks()
        Sucht alle Links im HTML-Code des Eintrags und filtert unerwünschte
        Links heraus.
    getHTMLCode()
        Gibt den HTML-Code des Eintrags zurück.
    getText()
        Gibt den Text des Wikipedia-Eintrags zurück.
    getTitle()
        Gibt den Titel des Wikipedia-Eintrags zurück.
    addToGraph(crawler)
        Fügt den Eintrag zum Graphen hinzu.
    """
    def __init__(self, url, source, crawler):
        """
        Konstruktor der Klasse Eintrag.

        Parameter
        ---------
        url : str
            Die URL des Wikipedia-Eintrags, der vom Objekt repräsentiert
            werden soll.
        source : str
            Die URL des Wikipedia-Eintrags, in dem der Link zum aktuellen
            Eintrag gefunden wurde.
        crawler : Webcrawler
            Objekt des Webcrawlers, der die aktuelle Indexierung ausführt.
            Parameter notwendig, um dem Graphen Knoten hinzufügen zu können.
        """
        self.url = url
        self.source = source
        self.html = self.getHTMLCode()
        self.text = self.getText()
        self.title = self.getTitle()
        print("Reached " + self.title) # ermöglicht Beobachtung des Programms in Echtzeit über die Konsolenausgabe
        self.links = []
        self.leaves = [] # speichert Referenzen auf andere Einträge
        self.crawler = crawler
        self.addToGraph(crawler)

    def __repr__(self):
        return self.url

    def index(self, layers, crawler):
        """
        Rekursive Methode, die Wikipedia-Einträge indexiert.

        Parameter
        ---------
        layers : int
            Zählvariable, die die Anzahl der übrigen, noch zu indexierenden,
            Ebenen speichert.
            Wird bei jedem rekursiven Durchlauf um 1 verkleinert.
        crawler : Webcrawler
            Objekt des Webcrawlers, der die Indexierung ausführt.
            Parameter notwendig, um Knoten dem Graphen hinzufügen zu können.

        Rückgabe
        --------
        self.leaves : list
            Gibt den Attributwert der Instanzvariable leaves zurück.
        """
        if layers < 0:
            return self
        else:
            self.links = self.getLinks()
            for l in self.links:
                nextE = Eintrag(l, self, crawler)
                self.leaves.append(nextE.index(layers - 1, self.crawler))
            return self.leaves

    def getLinks(self):
        """
        Findet alle Links im Artikel und filtert unerwünschte heraus.
        Unerwünscht sind alle Links, die nicht zu anderen Wikipedia-Einträgen,
        sondern zu bestimmten Spezialseiten führen.

        Rückgabe
        --------
        list
            Eine Liste, die alle erwünschten Links beinhaltet.
        """
        soup = BeautifulSoup(self.html, "html.parser")
        allLinks = soup.findAll('a', href=True)
        hrefs = [l["href"] for l in allLinks]
        links = []
        for l in hrefs:
            if (not "https://" in str(l) and not "http://" in str(l) and
                    not str(l)[0] == '#'):
                sp = str(l).split('/')
                sp.pop(0)
                try:
                    if sp[0] == "wiki":
                        tg = sp[1].split(':')
                        exc = ["Wikipedia", "Portal", "Spezial", "Kategorie",
                               "Datei", "Hilfe", "Diskussion"]
                        if tg[0] not in exc:
                            links.append(l)
                except Exception:
                    # häufiger Fehler, wenn bei einem Eintrag keine Links gefunden
                    # werden. Führte zu Programmabbruch. Fehler wird abgefangen.
                    return []
        result = []
        for l in links:
            # baut URL aus Wikipedia-internen Links
            flink = "http://de.wikipedia.org" + str(l)
            if flink not in result:
                result.append(flink)
        result.pop() #entfernt Link zu sich selbst
        return result

    def addToGraph(self, crawler):
        """
        Fügt den Eintrag als Knoten zum networkX-Graph hinzu.
        Fügt Kante von source-Eintrag zu aktuellem Eintrag zum
        networkX-Graph hinzu.

        Eine Überprüfung auf doppelte Knoten ist nicht nötig, da networkX
        diese automatisch überschreibt.
        Da im Knoten nur die URL gespeichert wird, ist die Überschreibung mit
        identischen Werten kein Problem.
        WICHTIG: Kanten bleiben Bestehen, auch wenn der Knoten überschrieben
        wird.

        Parameter
        ---------
        crawler : Webcrawler
            Der Webcrawler, der die aktuelle Indexierung ausführt.
            Parameter nötig, um dem Graphen Knoten hinzufügen zu können.

        Rückgabe
        --------
        None
        """
        crawler.graph.add_node(self.url)
        crawler.graph.add_edge(self.source, self.url)

    def getHTMLCode(self):
        """
        Gibt den HTML-Code des aktuellen Eintrags als String zurück.

        Rückgabe
        --------
        str
            vollständiger HTML-Code des Eintrags
        """
        res = requests.get(self.url)
        return res.text

    def getText(self):
        """
        Gibt den Verfassertext des Wikipedia-Eintrags als String zurück.

        Rückgabe
        --------
        str
            Verfassertext des aktuellen Wikipedia-Eintrags
        """
        soup = BeautifulSoup(self.html, 'html.parser')
        return soup.get_text()

    def getTitle(self):
        """
        Gibt den Titel des aktuellen Wikipedia-Eintrags als String zurück.

        Rückgabe
        --------
        str
            Titel des Eintrags
        """
        soup = BeautifulSoup(self.html, 'html.parser')
        ft = soup.find("title").text
        t = ft.split(' ')
        t.pop()
        t.pop()
        return ' '.join(t)

crawler = Webcrawler()

crawler.createGraph(0)

crawler.drawGraph()
crawler.saveGraphImage()

crawler.testNodeIncrease(1, 2) # VORSICHT: LÖSCHT AKTUELL GESPEICHERTEN GRAPHEN
crawler.testCycles()
crawler.testShortestPath()

crawler.finishGraph()

