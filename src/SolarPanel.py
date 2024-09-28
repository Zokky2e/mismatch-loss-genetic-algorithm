class SolarPanel:
    def __init__(
        self, serialnumber, 
        bezeichnung, articlenr, 
        datum, fertigungsauftrag, 
        pmpp, uoc, isc, umpp, impp, 
        ff, palettennummer, lieferung
        ):
        self.serialnumber = serialnumber
        self.bezeichnung = bezeichnung
        self.articlenr = articlenr
        self.datum = datum
        self.fertigungsauftrag = fertigungsauftrag
        self.pmpp = pmpp
        self.uoc = uoc
        self.isc = isc
        self.umpp = umpp
        self.impp = impp
        self.ff = ff
        self.palettennummer = palettennummer
        self.lieferung = lieferung
        self.a = 0
        self.i0 = 0
        self.ipv = 0
        self.rs = 0
        self.rp = 0

    def __repr__(self):
        return (
            f"SolarPanel(serialnumber={self.serialnumber}, bezeichnung={self.bezeichnung}, "
            f"articlenr={self.articlenr}, datum={self.datum}, "
            f"fertigungsauftrag={self.fertigungsauftrag}, pmpp={self.pmpp}, "
            f"uoc={self.uoc}, isc={self.isc}, umpp={self.umpp}, "
            f"impp={self.impp}, ff={self.ff}, palettennummer={self.palettennummer}, "
            f"lieferung={self.lieferung})"
        )

