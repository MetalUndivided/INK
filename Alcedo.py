class NegativePressureException(Exception):
    pass

class rtwell:
    
    def __init__(self, data: dict):
        self.name = data["name"]
        self.fluid = data["fluid"]
        self.a = data["a"]
        self.b = data["b"]
        
    def rateab(self, pres: str, pwf: str) -> float:
        
        pres = float(pres)
        pwf = float(pwf)
        a = float(self.a)
        b = float(self.b)
        
        return (-a + (a ** 2 + 4 * b * (pres ** 2 - pwf ** 2)) ** .5) / (2 * b)
    
    def bhpab(self, pres: str, rate: str) -> float:
        
        pres = float(pres)
        rate = float(rate)
        a = float(self.a)
        b = float(self.b)
        
        bhp = (pres ** 2 - b * rate ** 2 - a * rate) ** 0.5
        
        if type(bhp) is complex:
            raise NegativePressureException
        
        return bhp
        
    def yield_cvd(self, kind: str, pres: str, fluid: str=None) -> float:
    
        ## intended units:
        ## pres - bars
        ## returned yield - g/m3
        
        if fluid is None:
            fluid = self.fluid
        pres = float(pres)
        
        if fluid == "Ya":
        
            pres_rel = pres / 254
            
            if kind == "C5+":
                return (-1.0671 * pres_rel ** 4 + 1.0012 * pres_rel ** 3 + 1.7735 * pres_rel ** 2 - .9831 * pres_rel + 0.2744) * 185
            elif kind == "C3+C4":
                return (2.5397 * pres_rel ** 4 - 7.8391 * pres_rel ** 3 + 8.5582 * pres_rel ** 2 - 3.6087 * pres_rel + 1.3517) * 100.6
            else:
                raise Exception("Wrong kind type specified, supported kinds are 'C5+', 'C3+C4'")

        elif fluid == "Ma":
        
            pres_rel = pres / 259
            
            if kind == "C5+":
                pass   ## вставить ретроградную для мраково С5+
            elif kind == "C3+C4":
                pass   ## вставить ретроградную для мраково С3+С4
            else:
                raise Exception("Wrong kind type specified, supported kinds are 'C5+', 'C3+C4'")    
            
            raise Exception("This fluid is yet to be implemented")     ## убрать когда будут ретроградные для мраково
