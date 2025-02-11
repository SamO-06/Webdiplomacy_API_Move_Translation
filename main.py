import json
import math

#https://webdiplomacy.net/api.php?route=game/status&gameID=1337481&countryID=2

with open('MovesCopied.txt','r') as filein:
    dict_from_file = json.load(filein)

#dict['phases'][GAMETURN]['orders']
print(dict_from_file['phases'][0]['orders'])

'''

phases
    each game turn has a new entry (diplomacy, builds, retreats)
        units
        orders
        centers

'''

terrList = [
    0,
    "CLY",
    "EDI",
    "LVP",
    "YOR",
    "WAL",
    "LON",
    "POR",
    "SPA",
    "NAF",
    "TUN",
    "NAP",
    "ROM",
    "TUS",
    "PIE",
    "VEN",
    "APU",
    "GRE",
    "ALB",
    "SER",
    "BUL",
    "RUM",
    "CON",
    "SMY",
    "ANK",
    "ARM",
    "SYR",
    "SEV",
    "UKR",
    "WAR",
    "LVN",
    "MOS",
    "STP",
    "FIN",
    "SWE",
    "NWY",
    "DEN",
    "KIE",
    "BER",
    "PRU",
    "SIL",
    "MUN",
    "RUH",
    "HOL",
    "BEL",
    "PIC",
    "BRE",
    "PAR",
    "BUR",
    "MAR",
    "GAS",
    "BAR",
    "NTH",
    "NWG",
    "SKA",
    "HEL",
    "BAL",
    "BOT",
    "NAO",
    "IRI",
    "ENG",
    "MAO",
    "WES",
    "LYO",
    "TYR",
    "ION",
    "ADR",
    "AEG",
    "EAS",
    "BLA",
    "TYR",
    "BOH",
    "VIE",
    "TRI",
    "BUD",
    "GAL",
    "SPA (NC)",
    "SPA (NC)",
    "STP (SC)",
    "BUL (NC)",
    "BUL (SC)"
]

countryList = [
    0,
    'England',
    'France',
    'Italy',
    'Germany',
    'Austria',
    'Turkey',
    'Russia'
]

countryLoopList = [
    'England',
    'France',
    'Italy',
    'Germany',
    'Austria',
    'Turkey',
    'Russia'
]

moveSuccessDict = {'No' : ' (fails)', 'Yes' : ' (succeeds)'}

seasonsDict = ['Spring', 'Autumn']
convoyDict = {'Yes' : ' via convoy ', 'No' : ''}
dislodgedDict = {'Yes'}

def holdOrder(order):
    unitType = order['unitType']
    occupiedTerritory = terrList[order['terrID']]
    moveSucceeds = moveSuccessDict[order['success']]
    dislodged = order['dislodged']

    formattedMove = (unitType + ' ' + occupiedTerritory + ' ' + 'hold' + moveSucceeds)

    return formattedMove

def moveOrder(order):
    unitType = order['unitType']
    occupiedTerritory = terrList[order['terrID']]
    moveTargetTerritory = terrList[order['toTerrID']]
    moveSucceeds = moveSuccessDict[order['success']]
    viaConvoy = convoyDict[order['viaConvoy']]


    formattedMove = (unitType + ' ' + occupiedTerritory + ' - ' + moveTargetTerritory + viaConvoy + moveSucceeds)

    return formattedMove

def supportMoveOrder(order):
    unitType = order['unitType']
    occupiedTerritory = terrList[order['terrID']]
    supportedUnitTargetSpace = terrList[order['toTerrID']]
    supportedUnitOccupiedSpace = terrList[order['fromTerrID']]
    moveSucceeds = moveSuccessDict[order['success']]

    formattedMove = (unitType + ' ' + occupiedTerritory + ' S ' + supportedUnitOccupiedSpace + ' - ' + supportedUnitTargetSpace + moveSucceeds)

    return formattedMove

def supportHoldOrder(order):
    unitType = order['unitType']
    occupiedTerritory = terrList[order['terrID']]
    supportedUnitOccupiedSpace = terrList[order['fromTerrID']]
    moveSucceeds = moveSuccessDict[order['success']]

    formattedMove = (unitType + ' ' + occupiedTerritory + ' S ' + supportedUnitOccupiedSpace + ' Hold' + moveSucceeds)

    return formattedMove

def convoyOrder(order):
    unitType = order['unitType']
    occupiedTerritory = terrList[order['terrID']]
    convoyedUnitTargetSpace = terrList[order['toTerrID']]
    convoyedUnitOccupiedSpace = terrList[order['fromTerrID']]
    moveSucceeds = moveSuccessDict[order['success']]

    formattedMove = (unitType + ' ' + occupiedTerritory + ' C ' + convoyedUnitOccupiedSpace + ' - ' + convoyedUnitTargetSpace + moveSucceeds)

    return formattedMove


def compileReadableMovesSingleTurn(turnData):
    readableTurnData = turnData[len(turnData) - 1] + '\n'

    for i in range(7):

        readableTurnData = readableTurnData + countryLoopList[i] + ': '
        for unit in turnData[countryLoopList[i]]:
            readableTurnData = readableTurnData + unit + ', '

        readableTurnData = readableTurnData + '\n'

    return readableTurnData


def compileReadableMovesFullGame(gameData):
    readableData = ''
    for turn in gameData:
        readableData = readableData + compileReadableMovesSingleTurn(turn)

    return readableData


startYear = 1901
game_turns = []

for phase in dict_from_file['phases']:

    currentTurn = ''

    gameYear = seasonsDict[phase['orders'][1]['turn'] % 2] + ' '
    gameYear = gameYear + str(startYear + int(math.floor(phase['orders'][1]['turn'] / 2.0)))

    game_turns.append([])
    currentTurn = game_turns[len(game_turns) - 1]

    currentTurn.append({
        'England' : [],
        'France' : [],
        'Italy' : [],
        'Germany' : [],
        'Austria' : [],
        'Turkey' : [],
        'Russia' : []
        })

    for order in phase['orders']:
        currentCountry = countryList[order['countryID']]
        orderType = order['type']

        if orderType == 'Hold':
            currentTurn[currentCountry].append(holdOrder(order))

        if orderType == 'Move':
            currentTurn[currentCountry].append(moveOrder(order))

        if orderType == 'Support Move':
            currentTurn[currentCountry].append(supportMoveOrder(order))

        if orderType == 'Support Hold':
            currentTurn[currentCountry].append(supportHoldOrder(order))

        if orderType == 'Convoy':
            currentTurn[currentCountry].append(convoyOrder(order))

    currentTurn.append(gameYear)






with open('MovesFormated.txt', 'w') as formattedFile:
    finalString = ''

    for item in game_turns:
        for line in item:
            finalString += line

        finalString += '\n'

    formattedFile.write(finalString)

