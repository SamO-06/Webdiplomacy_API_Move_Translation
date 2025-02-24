import math
import requests
import time
import anthropic
import json


wDKey = ''
gameID = 1374267
countryID = '4'
parameters = {'gameID' : gameID, 'countryID' : countryID}
#header = {'Authorization' : 'Bearer ' + apiKey} #When using the wD-Key the header and actual API key are not needed
cookie = {'wD-Key' : wDKey}
dict_from_file = requests.get(url = 'https://webdiplomacy.net/api.php?route=game/status', params = parameters, cookies = cookie).json()


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
    "NWG",
    "NTH",
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
    "TYS",
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
    "SPA (SC)",
    "STP (NC)",
    "STP (SC)",
    "BUL (NC)",
    "BUL (SC)"
]

supplyCenterList = [
    "EDI",
    "LVP",
    "LON",
    "POR",
    "SPA",
    "TUN",
    "NAP",
    "ROM",
    "VEN",
    "GRE",
    "SER",
    "BUL",
    "RUM",
    "CON",
    "SMY",
    "ANK",
    "SEV",
    "WAR",
    "MOS",
    "STP",
    "SWE",
    "NWY",
    "DEN",
    "KIE",
    "BER",
    "MUN",
    "HOL",
    "BEL",
    "BRE",
    "PAR",
    "MAR",
    "VIE",
    "TRI",
    "BUD",
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

startYear = 1901
game_turns = [] #List of all previous game turns
following_turn = [] #List containing current turn information


#Unit Move Orders
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
    #print(order['toTerrID'])
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


#Unit Build Orders
def buildOrder(order):
    buildType = order['type']
    buildOrderSpace = terrList[order['terrID']]

    formattedMove = (buildType + ' ' + buildOrderSpace)

    return formattedMove


#Unit Retreat Orders
def retreatOrder(order):
    unitType = order['unitType']
    occupiedTerritory = terrList[order['terrID']]
    retreatTargetTerritory = terrList[order['toTerrID']]
    moveSucceeds = moveSuccessDict[order['success']]

    formattedMove = unitType + ' ' + occupiedTerritory
    if (order['type'] == 'Disband'):
        formattedMove = formattedMove + ' disband'

    else:
        formattedMove = formattedMove + ' retreat to ' + retreatTargetTerritory + moveSucceeds

    return formattedMove



#Compile functions to compile and return the requested readable move data
def compileReadableMovesSingleTurn(turnData):
    readableTurnData = turnData[len(turnData) - 1] + ' ' + '\n' #Current turn (Ex: Autumn 1902 Retreats)

    for i in range(7):

        if turnData[0][countryLoopList[i]] != []:
            readableTurnData = readableTurnData + countryLoopList[i] + ': ' #COUNTRYNAME:
            #print(turnData)
            for unit in turnData[0][countryLoopList[i]]:
                readableTurnData = readableTurnData + unit + ', ' #UNITDATA,

            readableTurnData = readableTurnData + '\n' # New line to split between countries

    return readableTurnData

def compileReadableMovesFullGame(gameData):
    readableData = ''
    for turn in gameData:
        readableData = readableData + compileReadableMovesSingleTurn(turn)
        readableData += '\n'

    return readableData

def compileReadableFollowingTurn(followingData):
    readableTurnData = followingData[len(followingData) - 2] + '\n'  # Current turn (Ex: Autumn 1902 Retreats)
    readableTurnData += 'Current phase required moves:\n'

    for i in range(7):
        if followingData[0][countryLoopList[i]] != []:
            readableTurnData = readableTurnData + countryLoopList[i] + ': ' #COUNTRYNAME:

            for unit in followingData[0][countryLoopList[i]]:
                readableTurnData = readableTurnData + unit  #UNITDATA, (This could also be build information)

            readableTurnData = readableTurnData + '\n' # New line to split between countries

    return readableTurnData



#Formats the original JSON data into lists of readable move data
def formatPreviousTurn(phase, currentTurn):
    turnType = phase['orders'][0]['phase']  # Diplomacy, Builds, Retreats

    gameYear = seasonsDict[phase['orders'][0]['turn'] % 2] + ' '
    gameYear = gameYear + str(startYear + int(math.floor(phase['orders'][0]['turn'] / 2.0)))
    gameYear = gameYear + ' ' + turnType

    game_turns.append([])
    currentTurn = game_turns[len(game_turns) - 1]

    currentTurn.append({
        'England': [],
        'France': [],
        'Italy': [],
        'Germany': [],
        'Austria': [],
        'Turkey': [],
        'Russia': []
    })

    if turnType == 'Diplomacy':
        for order in phase['orders']:
            currentCountry = countryList[order['countryID']]
            orderType = order['type']

            if orderType == 'Hold':
                currentTurn[0][currentCountry].append(holdOrder(order))

            if orderType == 'Move':
                currentTurn[0][currentCountry].append(moveOrder(order))

            if orderType == 'Support Move':
                currentTurn[0][currentCountry].append(supportMoveOrder(order))

            if orderType == 'Support Hold':
                currentTurn[0][currentCountry].append(supportHoldOrder(order))

            if orderType == 'Convoy':
                currentTurn[0][currentCountry].append(convoyOrder(order))

    elif turnType == 'Retreats':
        for order in phase['orders']:
            currentCountry = countryList[order['countryID']]

            currentTurn[0][currentCountry].append(retreatOrder(order))

    elif turnType == 'Builds':
        for order in phase['orders']:
            currentCountry = countryList[order['countryID']]

            currentTurn[0][currentCountry].append(buildOrder(order))

    currentTurn.append(gameYear)

def formatCurrentMoves(phase, currentTurn):
    followingTurnType = phase['phase']
    following_turn_number = phase['turn']

    previousTurn = dict_from_file['phases'][len(dict_from_file['phases']) - 1]

    followingTurnOrders = {
        'England': [],
        'France': [],
        'Italy': [],
        'Germany': [],
        'Austria': [],
        'Turkey': [],
        'Russia': []
    }

    if (followingTurnType == 'Diplomacy'):
        for unit in previousTurn['units']:
            currentCountry = countryList[unit['countryID']]

            unitType = unit['unitType']
            unitSpace = terrList[unit['terrID']]

            currentUnitFinal = unitType + ' ' + unitSpace + ', '
            followingTurnOrders[currentCountry].append(currentUnitFinal)

    elif (followingTurnType == 'Retreats'):

        for unit in previousTurn['units']:

            if (unit['retreating'] == 'Yes'):
                currentCountry = countryList[unit['countryID']]

                unitType = unit['unitType']
                unitSpace = terrList[unit['terrID']]

                currentUnitFinal = unitType + ' ' + unitSpace + ' needs to retreat, '
                followingTurnOrders[currentCountry].append(currentUnitFinal)

    elif (followingTurnType == 'Builds'):

        countryCenterCount = [0, 0, 0, 0, 0, 0, 0, 0]  # First value is a placeholder
        countryUnitCount = [0, 0, 0, 0, 0, 0, 0, 0]  # First value is a placeholder

        for center in previousTurn['centers']:
            if terrList[center['terrID']] in supplyCenterList:
                countryCenterCount[center['countryID']] += 1

        for unit in previousTurn['units']:
            countryUnitCount[unit['countryID']] += 1

        for i in range(7):

            if (countryCenterCount[i + 1] - countryUnitCount[i + 1] < 0):  # If a player has more units than centers
                followingTurnOrders[countryList[i + 1]].append(
                    'Must destroy ' + str(countryCenterCount[i + 1] - countryUnitCount[i + 1]) + ' units')

            elif (countryCenterCount[i + 1] - countryUnitCount[i + 1] > 0):  # If a player has more centers than units
                followingTurnOrders[countryList[i + 1]].append(
                    'Can build ' + str(
                        countryCenterCount[i + 1] - countryUnitCount[i + 1]) + ' units on their home centers')

    following_turn.append(followingTurnOrders)
    following_turn.append(followingTurnType)
    following_turn.append(following_turn_number)


def formatPreviousAndCurrentMoves(game_turns, following_turn):
    formattedString = compileReadableMovesSingleTurn(game_turns[len(game_turns) - 1]) + '\n'
    formattedString += compileReadableFollowingTurn(following_turn)

    return formattedString


#Takes and formats all information about the game until the current point
def getAllOrders():
    for phase in dict_from_file['phases']:

        currentTurn = ''

        if phase['orders'] != []: #On a live game the final turn is blank and throws an error
            formatPreviousTurn(phase, currentTurn)

        elif phase['orders'] == []: #Gathers information on what players need to do on the current turn
            formatCurrentMoves(phase, currentTurn)



getAllOrders()

finalString = ''
finalString = compileReadableMovesFullGame(game_turns)
finalString = finalString + compileReadableFollowingTurn(following_turn)


initialSystem = ''
with open('Initial_System.txt', 'r') as handle:
    loopText = handle.readlines()

    for line in loopText:
        initialSystem += line

    handle.close()


client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="",
)
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    temperature= .6,
    system = initialSystem,
    messages=[
        {"role": "user", "content": finalString}
    ]
)

initialOrderList = json.loads(message.content[0].text)

postDict = {
    'gameID' : gameID,
    'turn' : following_turn[2], #The current turn's number
    'phase' : following_turn[1], #The current turn's type
    'countryID' : countryID,
    'orders' : [],
    'ready' : 'Yes'
}



orderList = []

for order in initialOrderList:
    order['terrID'] = terrList.index(order['terrID'])

    if order['toTerrID'] != "":
        order['toTerrID'] = terrList.index(order['toTerrID'])

    if order['fromTerrID'] != "":
        order['fromTerrID'] = terrList.index(order['fromTerrID'])

    orderList.append(order)

postDict['orders'] = orderList

postJSON = json.dumps(postDict)
print(postJSON)

movePost = requests.post(url = 'https://webdiplomacy.net/api.php?route=game/orders', data = postJSON, params=parameters, cookies = cookie)

print(movePost.url)
print(movePost)
print(movePost.text)
