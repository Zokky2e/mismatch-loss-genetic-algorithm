class SolarPanel:
    def __init__(
        self, serialnumber, 
        pmpp, uoc, isc, umpp, impp, 
        ff, palettennummer
        ):
        self.serialnumber = serialnumber
        self.pmpp = pmpp
        self.uoc = uoc
        self.isc = isc
        self.umpp = umpp
        self.impp = impp
        self.ff = ff
        self.palettennummer = palettennummer
        self.a = 0.0
        self.i0 = 0.0
        self.ipv = 0.0
        self.upv = 0.0
        self.rs = 0.0
        self.rp = 0.0
        self.i = 0.0
        self.u = 0.0
        self.p = 0.0

    def __repr__(self):
        return (
            f"SolarPanel serialnumber={self.serialnumber}, "
            #f"bezeichnung={self.bezeichnung}, "
            #f"articlenr={self.articlenr}, datum={self.datum}, "
            #f"fertigungsauftrag={self.fertigungsauftrag}," 
            f"pmpp={self.pmpp}, "
            f"umpp={self.umpp}, impp={self.impp},"
            f"uoc={self.uoc}, isc={self.isc}, ff={self.ff}\n"
            f"rs={self.rs}, rp={self.rp}\n"
            #f"palettennummer={self.palettennummer}, "
            #f"lieferung={self.lieferung}," 
            f"ipv={self.ipv}, upv={self.upv}, "
            f"I={self.i}, U={self.u} P={self.p}\n"
        )

