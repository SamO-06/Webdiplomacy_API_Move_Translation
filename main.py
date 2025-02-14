import json
import math
import requests

#1111967 - 1

wDKey = ''
parameters = {'gameID' : 1349962, 'countryID' : '3'}
#header = {'Authorization' : 'Bearer ' + apiKey} #When using the wD-Key the header and actual API key are not needed
cookie = {'wD-Key' : wDKey}
dict_from_file = requests.get(url = 'https://webdiplomacy.net/api.php?route=game/status', params=parameters, cookies = cookie).json()

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
    "SPA (SC)",
    "STP (NC)",
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
    readableTurnData = followingData[len(followingData) - 1] + ' ' + '\n'  # Current turn (Ex: Autumn 1902 Retreats)
    readableTurnData += 'Current phase required moves:\n'

    for i in range(7):
        if followingData[0][countryLoopList[i]] != []:
            readableTurnData = readableTurnData + countryLoopList[i] + ': ' #COUNTRYNAME:

            for unit in followingData[0][countryLoopList[i]]:
                readableTurnData = readableTurnData + unit  #UNITDATA, (This could also be build information)

            readableTurnData = readableTurnData + '\n' # New line to split between countries

    return readableTurnData




startYear = 1901
game_turns = [] #List of all previous game turns
following_turn = [] #List containing current turn information

for phase in dict_from_file['phases']:

    currentTurn = ''

    if phase['orders'] != []: #On a live game the final turn is blank and throws an error

        turnType = phase['orders'][0]['phase'] #Diplomacy, Builds, Retreats

        gameYear = seasonsDict[phase['orders'][0]['turn'] % 2] + ' '
        gameYear = gameYear + str(startYear + int(math.floor(phase['orders'][0]['turn'] / 2.0)))
        gameYear = gameYear + ' ' + turnType

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


    elif phase['orders'] == []: #Gathers information on what players need to do on the current turn
        followingTurnType = phase['phase']

        previousTurn = dict_from_file['phases'][len(dict_from_file['phases']) - 2]

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

            countryCenterCount = [0, 0, 0, 0, 0, 0, 0, 0] #First value is a placeholder
            countryUnitCount = [0, 0, 0, 0, 0, 0, 0, 0] #First value is a placeholder

            for center in previousTurn['centers']:
                countryCenterCount[center['countryID']] += 1

            for unit in previousTurn['units']:
                countryUnitCount[unit['countryID']] += 1

            for i in range(7):

                if (countryCenterCount[i + 1] - countryUnitCount[i + 1] < 0): #If a player has more units than centers
                    followingTurnOrders[countryList[i + 1]].append('Must disband ' + str(countryCenterCount[i + 1] - countryUnitCount[i + 1]) + ' units')

                elif (countryCenterCount[i + 1] - countryUnitCount[i + 1] > 0): #If a player has more centers than units
                    followingTurnOrders[countryList[i + 1]].append(
                        'Can build ' + str(countryCenterCount[i + 1] - countryUnitCount[i + 1]) + ' units on their home centers')

            print(countryCenterCount)
            print(countryUnitCount)

        following_turn.append(followingTurnOrders)
        following_turn.append(followingTurnType)







with open('MovesFormated.txt', 'w') as formattedFile:
    finalString = ''

    finalString = compileReadableMovesFullGame(game_turns)
    finalString = finalString + compileReadableFollowingTurn(following_turn)

    formattedFile.write(finalString)

