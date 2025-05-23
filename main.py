import math
import requests
import time
import anthropic
import json
import orderTranslation
import positionStatus
import diplomacyGameInstance
import os

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
    'Uncontrolled',
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

countryNoteDict = {}
with open('CountryNotes.json') as countryNotes:
    countryNoteDict = json.load(countryNotes)


moveSuccessDict = {'No' : ' (fails)', 'Yes' : ' (succeeds)'}

seasonsDict = ['Spring', 'Autumn']
convoyDict = {'Yes' : ' via convoy ', 'No' : ''}

startYear = 1901



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

    if len(gameData) > 4:
        for i in range(4):
            readableData = readableData + compileReadableMovesSingleTurn(gameData[len(gameData) - (4 - i)])
            readableData += '\n'

    else:
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
def formatPreviousTurn(phase):
    turnType = phase['orders'][0]['phase']  # Diplomacy, Builds, Retreats

    gameYear = seasonsDict[phase['orders'][0]['turn'] % 2] + ' '
    gameYear = gameYear + str(startYear + int(math.floor(phase['orders'][0]['turn'] / 2.0)))
    gameYear = gameYear + ' ' + turnType

    game_turns.append([])
    turnBeingFormatted = game_turns[len(game_turns) - 1]

    turnBeingFormatted.append({
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
                turnBeingFormatted[0][currentCountry].append(orderTranslation.holdOrder(order))

            if orderType == 'Move':
                turnBeingFormatted[0][currentCountry].append(orderTranslation.moveOrder(order))

            if orderType == 'Support Move':
                turnBeingFormatted[0][currentCountry].append(orderTranslation.supportMoveOrder(order))

            if orderType == 'Support Hold':
                turnBeingFormatted[0][currentCountry].append(orderTranslation.supportHoldOrder(order))

            if orderType == 'Convoy':
                turnBeingFormatted[0][currentCountry].append(orderTranslation.convoyOrder(order))

    elif turnType == 'Retreats':
        for order in phase['orders']:
            currentCountry = countryList[order['countryID']]

            turnBeingFormatted[0][currentCountry].append(orderTranslation.retreatOrder(order))

    elif turnType == 'Builds':
        for order in phase['orders']:
            currentCountry = countryList[order['countryID']]

            turnBeingFormatted[0][currentCountry].append(orderTranslation.buildOrder(order))

    turnBeingFormatted.append(gameYear)

def formatCurrentMoves(phase, previousTurn):
    followingTurnType = phase['phase']
    following_turn_number = phase['turn']

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
def formatAllGameTurnData(game):
    #Populates the game_turns and following_turn lists
    for i in range(len(game['phases'])):
        phase = game['phases'][i]

        if phase['orders'] != []: #On a live game the final turn is blank and throws an error
            formatPreviousTurn(phase)

        elif phase['orders'] == []: #Gathers information on what players need to do on the current turn
            formatCurrentMoves(phase, game['phases'][i]) #passes information about current phase and the previous phase's data
                                                #This was i-1 previously. Not sure why it changed (29/4)


            '''
            Currently is bugged regarding detecting whether a game has already been saved in the past or not, causing
            the new statuses to just be saved as "The game is in it's starting position." every time.
            '''


wDKey = os.getenv("wDKey")
cookie = {'wD-Key' : wDKey}

anthropicAPIKey = os.getenv("ANTHROPIC_API_KEY")


startupPositionStatuses = positionStatus.initializeGamesOnStartup()
gameInstanceDict = startupPositionStatuses[0]
initializedGameIDList = startupPositionStatuses[1]

for i in range(100):

    games_needing_moves = requests.get(url='https://webdiplomacy.net/api.php?route=players/missing_orders',
                                       cookies=cookie).json()

    if (games_needing_moves != []):

        initialSystem = '' #The system prompt for the AI
        with open('Initial_System.txt', 'r') as handle:
            loopText = handle.readlines()

            for line in loopText:
                initialSystem += line

            handle.close()


        for game in games_needing_moves:

            gameID = game['gameID']
            countryID = game['countryID']

            if gameID not in initializedGameIDList:
                gameInstanceDict[gameID] = diplomacyGameInstance.gameInstance(gameID, countryID, None)
                initializedGameIDList.append(gameID)

            currentGameInstance = gameInstanceDict[gameID]

            #This calls the WebDiplomacy API to get information regarding the given gameID's position
            parameters = {'gameID': gameID, 'countryID': countryID}
            # header = {'Authorization' : 'Bearer ' + apiKey} #When using the wD-Key the header and actual API key are not needed
            rawGameStrJSONData = requests.get(url='https://webdiplomacy.net/api.php?route=game/status', params=parameters,
                                          cookies=cookie).json()


            game_turns = []  # List of all previous turns
            following_turn = []  # List containing current turn information

            formatAllGameTurnData(rawGameStrJSONData) #Populates the above two lists


            if following_turn[2] != 0: #If it is not the game's first turn
                currentGameInstance.getNewStatusAnalysis(formatPreviousAndCurrentMoves(game_turns, following_turn), following_turn[2])
                #currentGameInstance.getNewStatusAnalysis(compileReadableFollowingTurn(following_turn), following_turn[2])

            finalPostToAIString = ''
            finalPostToAIString = compileReadableMovesFullGame(game_turns)
            finalPostToAIString = finalPostToAIString + compileReadableFollowingTurn(following_turn) + "\n"

            finalPostToAIString = finalPostToAIString + positionStatus.getCurrentPosition(
                rawGameStrJSONData['phases'][len(rawGameStrJSONData['phases']) - 1])

            finalPostToAIString = finalPostToAIString + currentGameInstance.getMostRecentStatus()
            finalPostToAIString = finalPostToAIString + "\n" + countryNoteDict[countryList[countryID]]
            print(finalPostToAIString)

            specificGameSystem = initialSystem.replace('PLAYEDGREATPOWER', countryList[countryID])
            specificGameSystem = specificGameSystem.replace('COUNTRYSPECIFICNOTE', countryNoteDict[countryList[countryID]])


            #print(specificGameSystem)

            client = anthropic.Anthropic(
                # defaults to os.environ.get("ANTHROPIC_API_KEY")
                api_key = anthropicAPIKey,
            )
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=.7,
                system=specificGameSystem,
                messages=[
                    {"role": "user", "content": finalPostToAIString}
                ]
            )
            print('a')

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

            tempConvoyDict = {}  # This is a bandaid fix for the convoyPath issue and will be used assuming
            # There is not, in fact, an API call that can generate it.
            # Is a dictionary with convoy paths using the army terrID as the key

            for order in initialOrderList:
                order['terrID'] = terrList.index(order['terrID'])

                if order['toTerrID'] != "":
                    order['toTerrID'] = terrList.index(order['toTerrID'])

                if order['fromTerrID'] != "":
                    order['fromTerrID'] = terrList.index(order['fromTerrID'])

                if order['type'] == 'Convoy':  # Part of the bandaid fix
                    order['convoyPath'] = [(order['fromTerrID']), order['terrID']]
                    tempConvoyDict[order['fromTerrID']] = order['convoyPath']

                orderList.append(order)

            for order in initialOrderList:  # Part of the bandaid fix; fills in move orders' convoyPath variable
                if order['viaConvoy'] == 'Yes':

                    if order['terrID'] in tempConvoyDict.keys():  # If the army has an associated convoyPath
                        order['convoyPath'] = tempConvoyDict[order['terrID']]


            postDict['orders'] = orderList

            postJSON = json.dumps(postDict)


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
