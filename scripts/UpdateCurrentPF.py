# Local Includes
import Config
from Shared import *

# Python Includes
import pymysql # sql queries

years_to_update = [] # Can manually seed if necessary

f = open(Config.config["srcroot"] + "scripts/WeekVars.txt", "r")
years_to_update.append(int(f.readline().strip()))
week = int(f.readline().strip()) # Set to None if manually seeding

if week != 1:
    week = (week-1)*7 - 1

def updateCurrentPF(league, year):
    url = f"http://www.fleaflicker.com/api/FetchLeagueScoreboard?sport=NHL&league_id={league}&season={year}"
    if week != None:
        url += f"&scoring_period={week}"

    standings = make_api_call(url)
    for game in standings["games"]:
        matchup_id = game["id"]
        away_id = game["away"]["id"]
        away_score = game["awayScore"]["score"]["formatted"]
        home_id = game["home"]["id"]
        home_score = game["homeScore"]["score"]["formatted"]

        cursor.execute(f"UPDATE Teams set currentWeekPF={away_score}, CurrOpp={home_id}, matchupID={matchup_id} where teamID={away_id} AND year={year}")
        cursor.execute(f"UPDATE Teams set currentWeekPF={home_score}, CurrOpp={away_id}, matchupID={matchup_id} where teamID={home_id} AND year={year}")

db = pymysql.connect(host=Config.config["sql_hostname"], user=Config.config["sql_username"], passwd=Config.config["sql_password"], db=Config.config["sql_dbname"], cursorclass=pymysql.cursors.DictCursor)
cursor = db.cursor()

for year in years_to_update:
    for league in get_leagues_from_database(year):
        updateCurrentPF(league["id"], league["year"])

db.commit()
