import csv
from SolarPanel import SolarPanel

def exportPanels(solarPanels: list[SolarPanel], output_location):
    with open(output_location, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Serialnummer', 'Bezeichnung', 'ArticleNr.', 
                    'Datum', 'Fertigungsauftrag', 'PMPP', 'UOC', 'ISC', 'UMPP', 
                    'IMPP', 'FF', 'Palettennummer', 'Lieferung']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for panel in solarPanels:
            writer.writerow({
                'Serialnummer': panel.serialnumber,
                'Bezeichnung': panel.bezeichnung,
                'ArticleNr.': panel.articlenr,
                'Datum': panel.datum,
                'Fertigungsauftrag': panel.fertigungsauftrag,
                'PMPP': panel.pmpp,
                'UOC': panel.uoc,
                'ISC': panel.isc,
                'UMPP': panel.umpp,
                'IMPP': panel.impp,
                'FF': panel.ff,
                'Palettennummer': panel.palettennummer,
                'Lieferung': panel.lieferung
            })

    return 1

