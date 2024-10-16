import csv
from SolarPanel import SolarPanel

def exportPanels(solarPanels: list[SolarPanel], output_location):
    with open(output_location, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Serialnummer', 'PMPP', 'UOC', 'ISC', 'UMPP', 
                    'IMPP', 'FF', 'Palettennummer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for panel in solarPanels:
            writer.writerow({
                'Serialnummer': panel.serialnumber,
                'PMPP': panel.pmpp,
                'UOC': panel.uoc,
                'ISC': panel.isc,
                'UMPP': panel.umpp,
                'IMPP': panel.impp,
                'FF': panel.ff,
                'Palettennummer': panel.palettennummer,
            })
    return 1

