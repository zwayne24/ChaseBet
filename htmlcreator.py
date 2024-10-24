import requests
from bs4 import BeautifulSoup
import pandas as pd
import base64
from pathlib import Path

# Function to convert image to base64
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{0}' height='100px' class='img-fluid'>".format(
      img_to_bytes(img_path)
    )
    return img_html

# Scrape standings from ESPN
url = 'https://www.espn.com/nba/standings/_/group/league'
headers = {
    'User-Agent': 'Mozilla/5.0'
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

standings = pd.DataFrame(columns=['Team', 'W', 'L', 'PCT'])

i = 0
team_name_list = []
for team in soup.find_all('tr', class_='Table__TR Table__TR--sm Table__even'):
    if i < 15:
        team_name = team.find('span', class_='hide-mobile').text
        team_name_list.append(team_name)
    if i >= 15 and i < 30:
        wins = team.find('span', class_='stat-cell').text
        losses = team.find_all('span', class_='stat-cell')[1].text
        pct = team.find_all('span', class_='stat-cell')[2].text
        new_row = pd.DataFrame([{'Team': team_name_list[i-15], 'W': wins, 'L': losses, 'PCT': pct}])
        standings = pd.concat([standings, new_row], ignore_index=True)
    i += 1

# Continue with the data extraction...
i = 0
for team in soup.find_all('tr', class_='filled Table__TR Table__TR--sm Table__even'):
    if i < 15:
        team_name = team.find('span', class_='hide-mobile').text
        team_name_list.append(team_name)
    if i >= 15 and i < 30:
        wins = team.find('span', class_='stat-cell').text
        losses = team.find_all('span', class_='stat-cell')[1].text
        pct = team.find_all('span', class_='stat-cell')[2].text
        new_row = pd.DataFrame([{'Team': team_name_list[i], 'W': wins, 'L': losses, 'PCT': pct}])
        standings = pd.concat([standings, new_row], ignore_index=True)
    i += 1


# Define team lists for Chase, Bryce, and Zach
ChasesTeams = ['Phoenix Suns', 'Orlando Magic', 'Oklahoma City Thunder', 'Los Angeles Lakers', 'Minnesota Timberwolves','Houston Rockets', 'Golden State Warriors','Cleveland Cavaliers','Boston Celtics']
ChaseBet = [47.5,47.5,57.5,42.5,51.5,42.5,43.5,48.5,58.5]
# Process standings data
standings['W'] = standings['W'].astype(int)
standings['L'] = standings['L'].astype(int)
standings['PCT'] = standings['PCT'].astype(float)
standings['On Track For'] = standings['PCT'] * 82
standings = standings.sort_values(by='Team', ascending=True)#.drop(columns=['PCT'])

chasesStandings = standings[standings['Team'].isin(ChasesTeams)].reset_index(drop=True)
chasesStandings['O/U'] =  [f'Over {bet}' for bet in ChaseBet]
chasesStandings['Color'] = ['green' if track > bet else 'red' for track, bet in zip(chasesStandings['On Track For'], ChaseBet)]
chasesStandings.index += 1

teamToAbbr = {
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN', 'Charlotte Hornets': 'CHA', 'Chicago Bulls': 'CHI',
    'Cleveland Cavaliers': 'CLE', 'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET', 'Golden State Warriors': 'GS',
    'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND', 'LA Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN', 'New Orleans Pelicans': 'NO', 'New York Knicks': 'NY',
    'Oklahoma City Thunder': 'OKC', 'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHX', 'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SA', 'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS'
}

chaseStandingsMobile = chasesStandings.copy()


chaseStandingsMobile['Team'] = chaseStandingsMobile['Team'].map(teamToAbbr)
chaseStandingsMobile['O/U'] =  [f'Over {bet}' for bet in ChaseBet]
chaseStandingsMobile['Color'] = ['green' if track > bet else 'red' for track, bet in zip(chasesStandings['On Track For'], ChaseBet)]

chaseStandingsMobile = chaseStandingsMobile[['Team', 'W','L','PCT','On Track For','O/U','Color']]

html_table = "<table><thead><tr><th>Team</th><th>W</th><th>L</th><th>PCT</th><th>On Track For</th><th>O/U</th></tr></thead><tbody>"
for i, row in chasesStandings.iterrows():
    html_table += f"<tr><td>{row['Team']}</td><td>{row['W']}</td><td>{row['L']}</td><td>{row['PCT']:.0f}</td>"
    html_table += f"<td style='color: {row['Color']}'>{row['On Track For']:.0f}</td><td>{row['O/U']}</td></tr>"
html_table += "</tbody></table>"

html_table_mobile = "<table><thead><tr><th>Team</th><th>W</th><th>L</th><th>PCT</th><th>On Track For</th><th>O/U</th></tr></thead><tbody>"
for i, row in chaseStandingsMobile.iterrows():
    html_table_mobile += f"<tr><td>{row['Team']}</td><td>{row['W']}</td><td>{row['L']}</td><td>{row['PCT']:.0f}</td>"
    html_table_mobile += f"<td style='color: {row['Color']}'>{row['On Track For']:.0f}</td><td>{row['O/U']}</td></tr>"
html_table_mobile += "</tbody></table>"

# Generate HTML content
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBA Standings</title>
    <style>
    /* Existing styles */
    body {{
        font-family: Arial, sans-serif;
    }}

    h1 {{
        text-align: center;
        color: Green;
        font-size: 50px;
    }}

    table {{
    width: 100%; 
    border-collapse: collapse;
    table-layout: fixed; /* Ensures equal width for all columns */
    }}

    th, td {{
    width: 16.66%; /* 100% divided by 6 columns */
    padding: 10px;
    text-align: center;
    border: 1px solid black;
    }}

    img {{
        display: block;
        margin: 0 auto;
    }}

    .column {{
        float: left;
        width: 33.33%;
        text-align: center;
    }}

    .row:after {{
        content: "";
        display: table;
        clear: both;
    }}

    /* New styles */
    .row {{
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
    }}

    .column {{
        flex: 1;
        padding: 15px;
    }}

    .card {{
        border: 1px solid #ddd;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        background-color: #f9f9f9;
        padding: 20px;
        text-align: center;
    }}

    .card-header {{
        margin-bottom: 15px;
    }}

    .card-body h2 {{
        font-size: 24px;
        color: #333;
        margin: 10px 0;
    }}

    .table-container {{
        margin-top: 15px;
        overflow-x: auto;
    }}
    
    .table-container2 {{
        margin-top: 0px;
        overflow-x: visible;
        font-size: 12px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
    }}

    table, th, td {{
        border: 1px solid #ccc;
        padding: 10px;
    }}

    th {{
        background-color: #f2f2f2;
        color: #333;
        font-weight: bold;
    }}

    td {{
        text-align: center;
    }}
    
    @media screen and (max-width: 600px) {{
        .column {{
            flex: 100%; /* Make each column take up full width */
            padding: 0px;
        }}
        
        .table-container {{
            display: none;
        }}
        
        .table-container2 {{
            display: "block";
        }}
    }}
    
    @media screen and (min-width: 601px) {{
        .table-container2 {{
            display: none;
        }}
    }}
    

</style>

</head>
<body>

<h1>Chase Season-Long Over/Under Party</h1>

<div class="row">
    <div class="column">
        <div class="card">
            <div class="card-header">
                {img_to_html('photos/ChaseCrown.png')}
            </div>
            <div class="card-body">
                <div class="table-container">
                    {html_table}
                </div>
                <div class="table-container2">
                    {html_table_mobile}
                </div>
            </div>
        </div>
    </div>

</div>
<hr/>

</body>
</html>
"""

# Write HTML content to a file
with open('index.html', 'w') as f:
    f.write(html_content)

print("HTML file generated: index.html")
