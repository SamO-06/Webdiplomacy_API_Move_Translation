import positionStatus
import anthropic
import os
import json


'''

Every instance of this class contains information about a game's gameID and respective country ID.
This is to centralize all functions regarding individual games' orders and other functions.

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




class gameInstance:
    def __init__(self, gameID, countryID, initialStatus):
        self.gameID = gameID
        self.countryID = countryID

        if initialStatus == None:
            self.gameStatusDict = positionStatus.initializeGamePositionStatus(gameID, countryID)
        else:
            self.gameStatusDict = initialStatus

    def getMostRecentStatus(self):
        finalTurnKey = list(self.gameStatusDict['status'].keys())[-1]
        return self.gameStatusDict['status'][finalTurnKey]

    def updateSavedGameStatus(self, turn, newStatus):
        self.gameStatusDict['status'][turn] = newStatus
        positionStatus.updateGamePositionStatus(self.gameID, turn, self.gameStatusDict)


    def getNewStatusAnalysis(self, turnData, turnNumber):

        anthropicAPIKey = os.getenv("ANTHROPIC_API_KEY")


        with open("Game_Status_System.txt", 'r') as handle:
            loopText = handle.readlines()
        handle.close()

        gameStatusSystem = ''
        for line in loopText:
            gameStatusSystem += line
        gameStatusSystem = gameStatusSystem.replace('PLAYEDGREATPOWER', countryList[self.countryID])


        statusMessageToPost = ''
        statusMessageToPost += turnData
        statusMessageToPost += '\n' + self.getMostRecentStatus()

        #print(statusMessageToPost)

        client = anthropic.Anthropic(
            api_key=anthropicAPIKey,
        )
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=600,
            temperature=.7,
            system=gameStatusSystem,
            messages=[
                {"role": "user", "content": statusMessageToPost}
            ]
        )
        print('b')
        #print(turnNumber)
        #print(message.content[0].text)

        self.updateSavedGameStatus(turnNumber, message.content[0].text)
        return message.content[0].text

        '''
        Currently should theoretically function to get the bot to give back a position status and update the given game's status.
        What needs to be done is editing main.py to accommodate the use of the new status system and additional testing of
        how effective the system actually is. 
        '''







