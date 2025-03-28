import math
import requests
import time
import anthropic
import json


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
    'Uncontrolled', #This was 0, but is set as Uncontrolled for the getCurrentPosition function
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

startYear = 1901


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
def getAllOrders(game):
    for phase in game['phases']:

        currentTurn = ''

        if phase['orders'] != []: #On a live game the final turn is blank and throws an error
            formatPreviousTurn(phase, currentTurn)

        elif phase['orders'] == []: #Gathers information on what players need to do on the current turn
            formatCurrentMoves(phase, currentTurn)


def formatCurrentPosition(centerList, unitList):

    '''

    This function takes information about the current board state and reformats it to give the AI agent more
    up-to-date information about the positions of units and status of centers around the board in order
    to ensure the quality of responses from the agent does not decrease. The function returns a string.

    '''

    formattedPosition = 'Current position:\n'

    formattedPosition += 'Controlled Centers:\n'
    for country in countryList:

        formattedPosition += (country + ': ')

        for center in centerList[country]:
            formattedPosition += (center + ', ')

        formattedPosition += '\n'


    formattedPosition += ('\n\nControlled units:\n')
    for country in list(unitList.keys()):

        formattedPosition += (country + ': ')

        for unit in unitList[country]:
            formattedPosition += (unit[0] + ' ' + unit[1] + ', ')

        formattedPosition += '\n'

    formattedPosition += '\n'
    return formattedPosition



def getCurrentPosition(position):

    controlledSupplyCenters = {
        'England': [],
        'France': [],
        'Italy': [],
        'Germany': [],
        'Austria': [],
        'Turkey': [],
        'Russia': [],
        'Uncontrolled': []
    }

    controlledUnits = {
        'England': [],
        'France': [],
        'Italy': [],
        'Germany': [],
        'Austria': [],
        'Turkey': [],
        'Russia': [],
    }


    for center in position['centers']:
        if terrList[center['terrID']] in supplyCenterList:
            controllingPower = '' #The text name of the power in control of a given center

            controllingPower = countryList[center['countryID']]

            controlledSupplyCenters[controllingPower].append(terrList[center['terrID']])

            #Adds the center's text name to the given power's list
            #If uncontrolled is added to the Uncontrolled list


    for unit in position['units']:
        controllingPower = ''   #The text name of the power in control of a given center
        unitType = ''   #Army or Fleet
        occupiedSpace = 0   #TerrID

        controllingPower = countryList[unit['countryID']]
        unitType = unit['unitType']
        occupiedSpace = terrList[unit['terrID']]

        unitInformation = [unitType, occupiedSpace]

        controlledUnits[controllingPower].append(unitInformation)


    return formatCurrentPosition(controlledSupplyCenters, controlledUnits)




wDKey = ''
cookie = {'wD-Key' : wDKey}

games_needing_moves = requests.get(url = 'https://webdiplomacy.net/api.php?route=players/missing_orders', cookies = cookie).json()
print(games_needing_moves)

for i in range(30):


    if (games_needing_moves != []):

        initialSystem = '' #The system prompt for the AI
        with open('Initial_System.txt', 'r') as handle:
            loopText = handle.readlines()

            for line in loopText:
                initialSystem += line

            handle.close()


        for game in games_needing_moves:

            game_turns = []  # List of all previous turns
            following_turn = []  # List containing current turn information

            gameID = game['gameID']
            countryID = game['countryID']
            parameters = {'gameID': gameID, 'countryID': countryID}
            # header = {'Authorization' : 'Bearer ' + apiKey} #When using the wD-Key the header and actual API key are not needed
            dict_from_file = requests.get(url='https://webdiplomacy.net/api.php?route=game/status', params=parameters,
                                          cookies=cookie).json()

            getAllOrders(dict_from_file)

            finalString = ''

            finalString = compileReadableMovesFullGame(game_turns)
            finalString = finalString + getCurrentPosition(dict_from_file['phases'][len(dict_from_file['phases']) - 1]) #THIS IS A TEST CASE
            finalString = finalString + compileReadableFollowingTurn(following_turn)
            print(finalString)

            specificGameSystem = initialSystem.replace('PLAYEDGREATPOWER', countryList[countryID])

            #print(specificGameSystem)

            print(i)
            client = anthropic.Anthropic(
                # defaults to os.environ.get("ANTHROPIC_API_KEY")
                api_key="",
            )
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=.7, #Normally .6
                system=specificGameSystem,
                messages=[
                    {"role": "user", "content": finalString}
                ]
            )

            initialOrderList = json.loads(message.content[0].text)

            postDict = {
                'gameID': gameID,
                'turn': following_turn[2],  # The current turn's number
                'phase': following_turn[1],  # The current turn's type
                'countryID': countryID,
                'orders': [],
                'ready': 'Yes'
            }

            orderList = []

            tempConvoyDict = {}   #This is a bandaid fix for the convoyPath issue and will be used assuming
                                    #There is not, in fact, an API call that can generate it.
                                    #Is a dictionary with convoy paths using the army terrID as the key

            for order in initialOrderList:
                order['terrID'] = terrList.index(order['terrID'])

                if order['toTerrID'] != "":
                    order['toTerrID'] = terrList.index(order['toTerrID'])

                if order['fromTerrID'] != "":
                    order['fromTerrID'] = terrList.index(order['fromTerrID'])

                if order['type'] == 'Convoy': #Part of the bandaid fix
                    order['convoyPath'] = [(order['fromTerrID']), order['terrID']]
                    tempConvoyDict[order['fromTerrID']] = order['convoyPath']


                orderList.append(order)


            for order in initialOrderList: #Part of the bandaid fix; fills in move orders' convoyPath variable
                if order['viaConvoy'] == 'Yes':

                    if order['terrID'] in tempConvoyDict.keys(): #If the army has an associated convoyPath
                        order['convoyPath'] = tempConvoyDict[order['terrID']]


            postDict['orders'] = orderList

            postJSON = json.dumps(postDict)
            #print(postJSON)


            movePost = requests.post(url='https://webdiplomacy.net/api.php?route=game/orders', data=postJSON,
                                     params=parameters, cookies=cookie)

            with open ('ComparePosts.txt', 'a') as handle:
                handle.write(postJSON)
                handle.write('\n')
                handle.write(movePost.text)
                handle.write('\n\n')

            #print(movePost.text)
            #print(movePost.url)
            #print(movePost)

    time.sleep(15)

