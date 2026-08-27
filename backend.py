#se importa la libreri para apoyar con la tabla periodica
from mendeleev import element


#diccionario de metales
METALS = {
    "Alkali metals",
    "Alkaline earth metals",
    "Transition metals",
    "Post-transition metals",
    "Lanthanides",
    "Actinides"
}



# ==================== DATOS ESTÁTICOS DE LA TABLA (0 SEGUNDOS DE CARGA) ====================
#porque doña libreria tarda un choooooorrro y no me guta, mejor tener los datos asi XD
#papus colores para papus atomos
DATOS_TABLA = [
    (1, 'H', '#FFFFFF', 1, 1), (2, 'He', '#D9FFFF', 1, 18),
    (3, 'Li', '#CC80FF', 2, 1), (4, 'Be', '#C2FF00', 2, 2), (5, 'B', '#FFB5B5', 2, 13), (6, 'C', '#909090', 2, 14), (7, 'N', '#3050F8', 2, 15), (8, 'O', '#FF0D0D', 2, 16), (9, 'F', '#90E050', 2, 17), (10, 'Ne', '#B3E3F5', 2, 18),
    (11, 'Na', '#AB5CF2', 3, 1), (12, 'Mg', '#8AFF00', 3, 2), (13, 'Al', '#BFA6A6', 3, 13), (14, 'Si', '#F0C8A0', 3, 14), (15, 'P', '#FF8000', 3, 15), (16, 'S', '#FFFF30', 3, 16), (17, 'Cl', '#1FF01F', 3, 17), (18, 'Ar', '#80D1E3', 3, 18),
    (19, 'K', '#8F40D4', 4, 1), (20, 'Ca', '#3DFF00', 4, 2), (21, 'Sc', '#E6E6E6', 4, 3), (22, 'Ti', '#BFC2C7', 4, 4), (23, 'V', '#A6A6AB', 4, 5), (24, 'Cr', '#8A99C7', 4, 6), (25, 'Mn', '#9C7AC7', 4, 7), (26, 'Fe', '#E06633', 4, 8), (27, 'Co', '#F090A0', 4, 9), (28, 'Ni', '#50D050', 4, 10), (29, 'Cu', '#C88033', 4, 11), (30, 'Zn', '#7D80B0', 4, 12), (31, 'Ga', '#C28F8F', 4, 13), (32, 'Ge', '#668F8F', 4, 14), (33, 'As', '#BD80E3', 4, 15), (34, 'Se', '#FFA100', 4, 16), (35, 'Br', '#A62929', 4, 17), (36, 'Kr', '#5CB8D1', 4, 18),
    (37, 'Rb', '#702EB0', 5, 1), (38, 'Sr', '#00FF00', 5, 2), (39, 'Y', '#94FFFF', 5, 3), (40, 'Zr', '#94E0E0', 5, 4), (41, 'Nb', '#73C2C9', 5, 5), (42, 'Mo', '#54B5B5', 5, 6), (43, 'Tc', '#3B9E9E', 5, 7), (44, 'Ru', '#248F8F', 5, 8), (45, 'Rh', '#0A7D8C', 5, 9), (46, 'Pd', '#006985', 5, 10), (47, 'Ag', '#C0C0C0', 5, 11), (48, 'Cd', '#FFD98F', 5, 12), (49, 'In', '#A67573', 5, 13), (50, 'Sn', '#668080', 5, 14), (51, 'Sb', '#9E63B5', 5, 15), (52, 'Te', '#D47A00', 5, 16), (53, 'I', '#940094', 5, 17), (54, 'Xe', '#429EB0', 5, 18),
    (55, 'Cs', '#57178F', 6, 1), (56, 'Ba', '#00C900', 6, 2),
    # Lantánidos (57-71)
    (57, 'La', '#70D4FF', 8, 3), (58, 'Ce', '#FFFFC7', 8, 4), (59, 'Pr', '#D9FFC7', 8, 5), (60, 'Nd', '#C7FFC7', 8, 6), (61, 'Pm', '#A3FFC7', 8, 7), (62, 'Sm', '#8FFFC7', 8, 8), (63, 'Eu', '#61FFC7', 8, 9), (64, 'Gd', '#45FFC7', 8, 10), (65, 'Tb', '#30FFC7', 8, 11), (66, 'Dy', '#1FFFC7', 8, 12), (67, 'Ho', '#00FF9C', 8, 13), (68, 'Er', '#00E675', 8, 14), (69, 'Tm', '#00D452', 8, 15), (70, 'Yb', '#00BF38', 8, 16), (71, 'Lu', '#00AB24', 8, 17),
    (72, 'Hf', '#4DC2FF', 6, 4), (73, 'Ta', '#4DA6FF', 6, 5), (74, 'W', '#2194D6', 6, 6), (75, 'Re', '#267DAB', 6, 7), (76, 'Os', '#266696', 6, 8), (77, 'Ir', '#175487', 6, 9), (78, 'Pt', '#D0D0E0', 6, 10), (79, 'Au', '#FFD123', 6, 11), (80, 'Hg', '#B8B8D0', 6, 12), (81, 'Tl', '#A6544D', 6, 13), (82, 'Pb', '#575961', 6, 14), (83, 'Bi', '#9E4FB5', 6, 15), (84, 'Po', '#AB5C00', 6, 16), (85, 'At', '#754F45', 6, 17), (86, 'Rn', '#428296', 6, 18),
    (87, 'Fr', '#420066', 7, 1), (88, 'Ra', '#007D00', 7, 2),
    # Actínidos (89-103)
    (89, 'Ac', '#70ABFA', 9, 3), (90, 'Th', '#00BAFF', 9, 4), (91, 'Pa', '#00A1FF', 9, 5), (92, 'U', '#008FFF', 9, 6), (93, 'Np', '#0080FF', 9, 7), (94, 'Pu', '#006BFF', 9, 8), (95, 'Am', '#545CF2', 9, 9), (96, 'Cm', '#785CE3', 9, 10), (97, 'Bk', '#8A4FE3', 9, 11), (98, 'Cf', '#A136D4', 9, 12), (99, 'Es', '#B31FD4', 9, 13), (100, 'Fm', '#B31FBA', 9, 14), (101, 'Md', '#B30DA6', 9, 15), (102, 'No', '#BD0D87', 9, 16), (103, 'Lr', '#C70066', 9, 17),
    (104, 'Rf', '#CC0059', 7, 4), (105, 'Db', '#D1004F', 7, 5), (106, 'Sg', '#D90045', 7, 6), (107, 'Bh', '#E00038', 7, 7), (108, 'Hs', '#E6002E', 7, 8), (109, 'Mt', '#EB0026', 7, 9), (110, 'Ds', '#475569', 7, 10), (111, 'Rg', '#475569', 7, 11), (112, 'Cn', '#475569', 7, 12), (113, 'Nh', '#475569', 7, 13), (114, 'Fl', '#475569', 7, 14), (115, 'Mc', '#475569', 7, 15), (116, 'Lv', '#475569', 7, 16), (117, 'Ts', '#475569', 7, 17), (118, 'Og', '#475569', 7, 18)
]

#diccionario para traducciones
ELEMENTS_SPANISH = {
    # 1 - 10
    "hidrógeno": "H", "helio": "He", "litio": "Li", "berilio": "Be", "boro": "B",
    "carbono": "C", "nitrógeno": "N", "oxígeno": "O", "flúor": "F", "neón": "Ne",
    
    # 11 - 20
    "sodio": "Na", "magnesio": "Mg", "aluminio": "Al", "silicio": "Si", "fósforo": "P",
    "azufre": "S", "cloro": "Cl", "argón": "Ar", "potasio": "K", "calcio": "Ca",
    
    # 21 - 30
    "escandio": "Sc", "titanio": "Ti", "vanadio": "V", "cromo": "Cr", "manganeso": "Mn",
    "hierro": "Fe", "cobalto": "Co", "níquel": "Ni", "cobre": "Cu", "zinc": "Zn",
    
    # 31 - 40
    "galio": "Ga", "germanio": "Ge", "arsénico": "As", "selenio": "Se", "bromo": "Br",
    "kriptón": "Kr", "rubidio": "Rb", "estroncio": "Sr", "itrio": "Y", "circonio": "Zr",
    
    # 41 - 50
    "niobio": "Nb", "molibdeno": "Mo", "tecnecio": "Tc", "rutenio": "Ru", "rodio": "Rh",
    "paladio": "Pd", "plata": "Ag", "cadmio": "Cd", "indio": "In", "estaño": "Sn",
    
    # 51 - 60
    "antimonio": "Sb", "telurio": "Te", "yodo": "I", "xenón": "Xe", "cesio": "Cs",
    "bario": "Ba", "lantano": "La", "cerio": "Ce", "praseodimio": "Pr", "neodimio": "Nd",
    
    # 61 - 70
    "prometio": "Pm", "samario": "Sm", "europio": "Eu", "gadolinio": "Gd", "terbio": "Tb",
    "disprosio": "Dy", "holmio": "Ho", "erbio": "Er", "tulio": "Tm", "iterbio": "Yb",
    
    # 71 - 80
    "lutecio": "Lu", "hafnio": "Hf", "tántalo": "Ta", "wolframio": "W", "renio": "Re",
    "osmio": "Os", "iridio": "Ir", "platino": "Pt", "oro": "Au", "mercurio": "Hg",
    
    # 81 - 90
    "talio": "Tl", "plomo": "Pb", "bismuto": "Bi", "polonio": "Po", "astato": "At",
    "radón": "Rn", "francio": "Fr", "radio": "Ra", "actinio": "Ac", "torio": "Th",
    
    # 91 - 100
    "protactinio": "Pa", "uranio": "U", "neptunio": "Np", "plutonio": "Pu", "americio": "Am",
    "curio": "Cm", "berkelio": "Bk", "californio": "Cf", "einstenio": "Es", "fermio": "Fm",
    
    # 101 - 110
    "mendelevio": "Md", "nobelio": "No", "laurencio": "Lr", "rutherfordio": "Rf", "dubnio": "Db",
    "seaborgio": "Sg", "bohrio": "Bh", "hassio": "Hs", "meitnerio": "Mt", "darmstadtio": "Ds",
    
    # 111 - 118
    "roentgenio": "Rg", "copernicio": "Cn", "nihonio": "Nh", "flerovio": "Fl", "moscovio": "Mc",
    "livermorio": "Lv", "teneso": "Ts", "oganesón": "Og"
}

#diccionario de simbolo a español usando el diccionario ya creado porque que flijera escribir todo eso otra ves pero alrevez XD
SIMBOL_SPANISH = {simbolo: nombre for nombre, simbolo in ELEMENTS_SPANISH.items()}


#funcion que recibe una entrada y analisa si es el numero atomico o nombre/simbolo, lo devuelve como un calor legible para la funcion element() de la libreria mendeleev
def cleaninput(elementEntry):
    elementToReturn = elementEntry.strip()
    if elementToReturn.isdigit():
        elementToReturn = int(elementToReturn)
        if elementToReturn <= 118 and elementToReturn >= 1:
            return element(elementToReturn), None
        else:
            return None, "el numero atomico esta fuera de rango de la tabla periodica"
    else:
        elementToReturn = elementToReturn.lower()
        try:
            if elementToReturn in ELEMENTS_SPANISH:
                elementToReturn = ELEMENTS_SPANISH.get(elementToReturn, None)

            return element(elementToReturn.capitalize()), None

        except Exception:
            return None, "simbolo/nombre mal escrito"


def isMetal(element):
    return element.series in METALS

def getTypeLink(element1, element2):
    #apartado de que tipo de enlace es
    #caso uno: no hay enlace proque alguno es gas noble sjjsjsjsjs
    if element1.group_id == 18 or element2.group_id == 18:
        if element1.group_id == 18 and element2.group_id == 18:
            return 1, "no puede haber enlace porque ambos elementos son gases nobles"
        elif element1.group_id == 18:
            return 1, f"no puede haber enlace porque el  {SIMBOL_SPANISH.get(element1.symbol, element1.name)} es un gas noble"
        else:
            return 1, f"no puede haber enlace porque el  {SIMBOL_SPANISH.get(element2.symbol, element2.name)} es un gas noble"

    #caso dos: dos metales, enlace metalico
    elif isMetal(element1) and isMetal(element2):
        return 2, "metálico"

    #caso tres: un metal y un nometal, enlace ionico
    elif isMetal(element1) != isMetal(element2):
        return 3,"iónico"

    #caso cuatro: enlace covalente, no metal y no metal
    elif not isMetal(element1) and not isMetal(element2):
        return 4, "covalente"

    else:
        return None, "no deberia existir"



#funcion para saber que tipo de material es (solo en enlaces covalentes)
def getMaterialType(element1, element2):
    grupoE1 = element1.group_id
    grupoE2 = element2.group_id

    if grupoE1 == 14 and grupoE2 == 14:
        titulo = "Semiconductor Intrínseco (Puro)"
        descripcion = (
            "Red cristalina tetravalente sin impurezas. La conducción eléctrica depende "
            "únicamente de la excitación térmica para liberar pares electrón-hueco."
        )
        return titulo, descripcion

    elif {grupoE1, grupoE2} == {14, 13}:
        titulo = "Semiconductor Extrínseco Tipo P (Aceptor)"
        descripcion = (
            "Dopado con átomos trivalentes (Grupo 13). Se generan huecos libres (cargas positivas) "
            "en la banda de valencia al faltar un electrón para completar los enlaces covalentes."
        )
        return titulo, descripcion

    elif {grupoE1, grupoE2} == {14, 15}:
        titulo = "Semiconductor Extrínseco Tipo N (Donador)"
        descripcion = (
            "Dopado con átomos pentavalentes (Grupo 15). El quinto electrón de valencia queda libre "
            "en la banda de conducción, facilitando el flujo eléctrico por electrones negativos."
        )
        return titulo, descripcion

    else:
        titulo = "Enlace Covalente Estándar"
        descripcion = (
            "No forma una red semiconductora clásica. Los electrones están fuertemente localizados "
            "en los enlaces, comportándose principalmente como un material aislante o molecular."
        )
        return titulo, descripcion

#funcion para obtener configuracion electronica
def getElectronicConfiguration(elemntEntry: element):
    return elemntEntry.ec


#funciones para obtener la valencia, protones, etc
def getProtons(entryElemnt):
    return entryElemnt.protons

def getValence(entryElement):
    # CASO ESPECIAL: Helio (Grupo 18 pero solo tiene 2 e-)
    if entryElement.symbol == 'He':
        return 2

    # Grupo 1 y 2 (incluye Hidrógeno)
    if entryElement.group_id in [1, 2]:
        return entryElement.group_id
    
    # Metales de transición (Grupos 3 al 12)
    elif 3 <= entryElement.group_id <= 12:
        if entryElement.symbol in ['Cr', 'Cu', 'Nb', 'Mo', 'Ru', 'Rh', 'Pd', 'Ag', 'Pt', 'Au']:
            return 1
        return 2
    
    # Bloque p (Grupos 13 al 18: Ne, Ar, Kr, Xe, Rn = 8)
    elif 13 <= entryElement.group_id <= 18:
        return entryElement.group_id - 10
    
    return 2

def getNeutrons(entryElement):
    return entryElement.neutrons

def getName(entryElement):
    return SIMBOL_SPANISH.get(entryElement.symbol, entryElement.name)


#obtener color de el atomo para mas perosonalisacion
MAPA_COLORES = {item[1]: item[2] for item in DATOS_TABLA}

def getColor(simbolo_o_elem):
    sym = simbolo_o_elem.symbol if hasattr(simbolo_o_elem, 'symbol') else str(simbolo_o_elem)
    return MAPA_COLORES.get(sym, "#38bdf8")