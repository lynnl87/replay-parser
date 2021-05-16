import constant
import sys
from parseHelper import ParseHelper
from config import getMysqlConnection
import glob

parseHelp = ParseHelper()
for file in glob.glob("./Processed/*.StormReplay"):
    parseHelp.initProtocols(file)
    details = parseHelp.getDetails()
    protocol = parseHelp.getProtocol()
    playerList = []

    # Hots player id's are 1 based index.
    count = 1
    for x in details['m_playerList']:
        playerList.append( {'name': x['m_name'].decode("utf-8") , 'hero' : x['m_hero'].decode("utf-8") , 'playerID' : count, 'team' : x['m_teamId']})
        count += 1

    periodicExp = []
    if hasattr(protocol, constant.DECODE_TRACKER_EVENTS):
                contents = parseHelp.getTrackerEvents()
                for event in protocol.decode_replay_tracker_events(contents):
                    if (event['_event'] == constant.TRACKER_GAME_STATS and event['m_eventName'] == constant.EVENT_XP_BREAKDOWN):
                        periodicExp.append(event)
                    if (event['_event'] == constant.TRACKER_SCORE_RESULTS):
                        break
                else:
                    event = None

    if (event == None):
        sys.exit(1)

    for totals in event['m_instanceList']:
        count = 0
        eventName = totals['m_name'].decode("utf-8")
        for totalValue in totals['m_values']:
            if not totalValue:
                continue
            playerList[count][eventName] = totalValue[0]['m_value']
            count +=1
        
    #At this point, we have the main event we want to track.
    mydb = getMysqlConnection()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM games WHERE timestamp ='" + parseHelp.filetime_to_dt(details["m_timeUTC"]).strftime('%Y-%m-%d %H:%M:%S') +"'")
    myresult = mycursor.fetchall()
    if (mycursor.rowcount != 0) :
        sql = "INSERT INTO map_data(games_id, Player, Hero, Team, Takedowns, Deaths, TownKills, SoloKill, Assists, MetaExperience, Level, \
                TeamTakedowns, ExperienceContribution, Healing, SiegeDamage, StructureDamage, MinionDamage, HeroDamage, MercCampCaptures, WatchTowerCaptures, SelfHealing, \
                TimeSpentDead, TimeCCdEnemyHeroes, CreepDamage, SummonDamage, Tier1Talent, Tier2Talent, Tier3Talent, Tier4Talent, Tier5Talent, Tier6Talent, Tier7Talent, \
                DamageTaken, DamageSoaked, HighestKillStreak, TeamLevel, ProtectionGivenToAllies, TimeSilencingEnemyHeroes, TimeRootingEnemyHeroes, TimeStunningEnemyHeroes, \
                ClutchHealsPerformed, EscapesPerformed, VengeancesPerformed, TeamfightEscapesPerformed, OutnumberedDeaths, TeamfightHealingDone, TeamfightDamageTaken, \
                TeamfightHeroDamage, OnFireTimeOnFire, EndOfMatchAwardMostTimePushingBoolean, EndOfMatchAwardMostTimeOnPointBoolean, TimeOnPoint, PlaysStarCraft, PlaysDiablo, \
                PlaysOverwatch, PlaysWarCraft, PlaysNexus, PlaysOverwatchOrNexus, PlaysWarrior, PlaysAssassin, PlaysSupport, PlaysSpecialist, PlaysMale, PlaysFemale, \
                TouchByBlightPlague, LessThan4Deaths, LessThan3TownStructuresLost, PhysicalDamage, SpellDamage, Multikill, MinionKills, RegenGlobes, AltarDamageDone, EndOfMatchAwardMVPBoolean) \
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)"
        print(file)
        for player in playerList:
            values = (myresult[0][0], player.get('name'), player.get('hero'), player.get('team'), player.get('Takedowns'), player.get('Deaths'), player.get('TownKills'), player.get('SoloKill'), player.get('Assists'), 
                player.get('MetaExperience'), player.get('Level'), player.get('TeamTakedowns'), player.get('ExperienceContribution'), player.get('Healing'), player.get('SiegeDamage'), 
                player.get('StructureDamage'), player.get('MinionDamage'), player.get('HeroDamage'), player.get('MercCampCaptures'), player.get('WatchTowerCaptures'), player.get('SelfHealing'), 
                player.get('TimeSpentDead'), player.get('TimeCCdEnemyHeroes'), player.get('CreepDamage'), player.get('SummonDamage'), player.get('Tier1Talent'), player.get('Tier2Talent'), 
                player.get('Tier3Talent'), player.get('Tier4Talent'), player.get('Tier5Talent'), player.get('Tier6Talent'), player.get('Tier7Talent'), player.get('DamageTaken'), player.get('DamageSoaked'), 
                player.get('HighestKillStreak'), player.get('TeamLevel'), player.get('ProtectionGivenToAllies'), player.get('TimeSilencingEnemyHeroes'), player.get('TimeRootingEnemyHeroes'), 
                player.get('TimeStunningEnemyHeroes'), player.get('ClutchHealsPerformed'), player.get('EscapesPerformed'), player.get('VengeancesPerformed'), player.get('TeamfightEscapesPerformed'), 
                player.get('OutnumberedDeaths'), player.get('TeamfightHealingDone'), player.get('TeamfightDamageTaken'), player.get('TeamfightHeroDamage'), player.get('OnFireTimeOnFire'), 
                player.get('EndOfMatchAwardMostTimePushingBoolean'), player.get('EndOfMatchAwardMostTimeOnPointBoolean'), player.get('TimeOnPoint'), player.get('PlaysStarCraft'), player.get('PlaysDiablo'), 
                player.get('PlaysOverwatch'), player.get('PlaysWarCraft'), player.get('PlaysNexus'), player.get('PlaysOverwatchOrNexus'), player.get('PlaysWarrior'), player.get('PlaysAssassin'), 
                player.get('PlaysSupport'), player.get('PlaysSpecialist'), player.get('PlaysMale'), player.get('PlaysFemale'), player.get('TouchByBlightPlague'), player.get('LessThan4Deaths'), 
                player.get('LessThan3TownStructuresLost'), player.get('PhysicalDamage'), player.get('SpellDamage'), player.get('Multikill'), player.get('MinionKills'), 
                player.get('RegenGlobes'), 
                player.get('AltarDamageDone'), player.get('EndOfMatchAwardMVPBoolean'))
            print(player.get('DamageSoaked'))
            mycursor.execute(sql, values)
            #mydb.commit()
print("finished")