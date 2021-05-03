from subprocess import PIPE, run
import ast
import mysql.connector
import datetime
import time 
import glob, os

EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as MS file time
map_id = -1;
game_id = -1;

def out(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return ast.literal_eval(result.stdout)
    
def filetime_to_dt(s):
    return datetime.datetime.fromtimestamp((s - 116444736000000000) // 10000000)
    
def version_dict_to_str(dict):
    return str(dict["m_build"]) + "." + str(dict["m_major"]) + "." + str(dict["m_minor"])+ "." + str(dict["m_revision"])

mydb = mysql.connector.connect(
  host="localhost",
  user="phpmyadmin",
  password="bbcj5616",
  database="hots",
  auth_plugin='mysql_native_password'
)

os.chdir("./Replays/")
for file in glob.glob("*.StormReplay"):
    try:
        header = out("python3 -m heroprotocol --header \"" + str(file) + "\"")
        details = out("python3 -m heroprotocol --details \"" + str(file) + "\"")
        version = version_dict_to_str(header["m_version"])
        
        #lets check if the map name exist yet
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM maps WHERE map_name =\"" + details["m_title"].decode("utf-8") +"\"");
        myresult = mycursor.fetchall()
        if (mycursor.rowcount == 0) :
            print("map didn't exist")
            mycursor = mydb.cursor()
            sql = "INSERT INTO maps (map_name) VALUES (%s)"
            value = details["m_title"].decode("utf-8")
            mycursor.execute(sql, (value,))
            mydb.commit()
            map_id = mycursor.lastrowid;
        else:
            map_id = myresult[0][0];
            
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM games WHERE timestamp ='" + filetime_to_dt(details["m_timeUTC"]).strftime('%Y-%m-%d %H:%M:%S') +"'");
        myresult = mycursor.fetchall()

        # we only want to insert the game if we haven't before.
        if (mycursor.rowcount == 0) :
            mycursor = mydb.cursor()
            sql = "INSERT INTO games (timestamp, time_offset, map_id, version) VALUES (%s, %s, %s, %s)"
            val = (filetime_to_dt(details["m_timeUTC"]).strftime('%Y-%m-%d %H:%M:%S'), details["m_timeLocalOffset"], map_id, version)
            mycursor.execute(sql, val)
            mydb.commit()
            game_id = mycursor.lastrowid;
            for  player in details["m_playerList"] :
                    mycursor = mydb.cursor()
                    sql = "INSERT INTO replay_data (games_id, player, hero, team, win) VALUES (%s, %s, %s, %s, %s)"
                    val = (game_id,  player['m_name'].decode("utf-8"), player['m_hero'].decode("utf-8"), player['m_teamId'], player['m_result'])
                    mycursor.execute(sql, val)
                    mydb.commit()
        else:
            game_id = myresult[0][0];
        
        os.rename(file, "../Processed/" + file);
    except ValueError:
        print("Value error");