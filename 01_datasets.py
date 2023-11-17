import requests
import pandas as pd
import numpy as np
import json
import pandas as pd

class DATASETS:
    def __init__(self):
        self.url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        response = requests.get(self.url)
        self.data = json.loads(response.text)

    def build_player_dataset(self):
        # Create pandas DataFrame from JSON player data
        player_dataset = pd.DataFrame.from_dict(self.data['elements'])
        #based on this the relevant columns are
        relevant_columns_description={
            'cost_change_start':'price change since start',
            'dreamteam_count':'nr of times in dreamteam',
            'element_type':'position in game',
            'event_points':'points in last gameweek',
            'first_name':'first name',
            'form':'form',
            'in_dreamteam':'whether in current dreamteam',
            'now_cost':'current price *10',
            'points_per_game': 'points per game',
            'second_name': 'second name',
            'selected_by_percent': 'selected by percent',
            'team':'team nr based on alphabetical order',
            #'team_code':'team code ???',
            'total_points': 'total points',
            'transfers_in': 'total transfers in',
            'transfers_in_event': 'transfers in this gameweek',
            'transfers_out': 'total transfers out',
            'transfers_out_event': 'transfers out this gameweek',
            'value_form':'form / value rounded',
            'value_season':'total points / value rounded',
            'minutes':'minutes',
            'goals_scored': 'goals scored',
            'assists': 'assists',
            'clean_sheets': 'clean sheets',
            'goals_conceded': 'goals conceded',
            'own_goals': 'own goals',
            'penalties_saved': 'penalties saved',
            'penalties_missed': 'penalties missed',
            'yellow_cards': 'yellow cards',
            'red_cards': 'red cards',
            'saves' : 'saves',
            'bonus':'total bonus points (fpl points)',
            'bps':'total bonus points',
            'influence':'total influence metric',
            'creativity':'total creativity metric',
            'threat':'total threat metric',
            'ict_index':'total ict index',
            'starts':'starts',
            'expected_goals':'total expected goals',
            'expected_assists':'total expected assists',
            'expected_goal_involvements':'total expected goal involvements',
            'expected_goals_conceded':'total expected goals conceded',
            'influence_rank':'rank for influence across all positions',
            #'influence_rank_type':'something with position???',
            'creativity_rank':'rank for creativity across all positions',
            #'creativity_rank_type':'something with position???',
            'threat_rank':'rank for threat across all positions',
            #'threat_rank_type':'something with position???',
            'ict_index_rank':'rank for ict index across all positions',
            #'ict_index_rank_type':'something with position???',
            'corners_and_indirect_freekicks_order':'corners and indirect freekicks order, not complete',
            'direct_freekicks_order':'direct freekicks order, not complete',
            'penalties_order':'penalties order, not complete',
            'expected_goals_per_90':'expected goals per_90',
            'saves_per_90':'saves per 90',
            'expected_assists_per_90':'expected assists per 90',
            'expected_goal_involvements_per_90':'expected goal involvements per 90',
            'expected_goals_conceded_per_90':'expected goals conceded per 90',
            'goals_conceded_per_90':'goals conceded per 90',
            'now_cost_rank':'rank for price across all positions',
            #'now_cost_rank_type':'something with position???',
            'form_rank':'rank for form across all positions',
            #'form_rank_type':'something with position???',
            'points_per_game_rank':'rank for points across all positions',
            #'points_per_game_rank_type':'something with position???',
            'selected_rank':'rank for selected across all positions',
            #'selected_rank_type':'something with position???',
            #'starts_per_90':'???',
            'clean_sheets_per_90':'amount of minutes on pitch with clean sheet / amount of minutes on pitch',
            'id':'id'
        }
        remaining_columns = list(set(player_dataset.columns).difference(relevant_columns_description.keys()))
        player_dataset.drop(remaining_columns, axis=1, inplace=True)
        self.player_dataset = player_dataset




    def build_team_dataset(self):
        teams_dataset = pd.DataFrame.from_dict(self.data['teams'])
        relevant_columns_description_teams = ['id', 'name', 'short_name', 'strength', 'strength_overall_home', 'strength_overall_away', \
                                            'strength_attack_home', 'strength_attack_away', 'strength_defence_home', 'strength_defence_away']
        #subset for relevant columns
        teams_dataset = teams_dataset[relevant_columns_description_teams]
        self.teams_dataset = teams_dataset




    def build_events_dataset(self):
        events_dataset = pd.DataFrame.from_dict(self.data['events'])
        self.events_dataset =  events_dataset
    




    def transform_player_dataset(self):
        element_types_dataset = pd.DataFrame.from_dict(self.data['element_types'])
        # join player positions
        self.final_dataset = self.player_dataset.merge(
            self.teams_dataset,
            left_on='team',
            right_on='id',
            suffixes =['_player','_team']
        ).merge(
            element_types_dataset,
            left_on='element_type',
            right_on='id')
        # rename columns
        self.final_dataset = self.final_dataset.rename(columns={'name':'team_name', 'singular_name':'position_name', 'id': 'id_position'})
        self.final_dataset = self.final_dataset.drop(columns=['element_type', 'sub_positions_locked', 'element_count', 'ui_shirt_specific', 'plural_name', 'plural_name_short'])
        self.final_dataset = self.final_dataset



    def df_fplpoints_per_club(self):
        fpl_points_per_club = self.final_dataset.groupby('team_name')['total_points'].sum()
        return fpl_points_per_club


    def df_fplpoints_per_position(self):
        played_already = self.final_dataset[self.final_dataset['minutes'] >= 1]
        fpl_points_per_position = played_already.groupby('position_name')['total_points'].agg(['sum', 'mean', 'count']).reindex(['Goalkeeper', 'Defender', 'Midfielder', 'Forward'])
        return fpl_points_per_position


    def df_goals_vs_xg(self):
        self.final_dataset['expected_goals'] = self.final_dataset['expected_goals'].astype(float)
        xG_per_club = self.final_dataset.groupby('team_name')['expected_goals'].sum()
        G_per_club = self.final_dataset.groupby('team_name')['goals_scored'].sum()
        df_goals_vs_xg = pd.concat([xG_per_club, G_per_club], axis=1)
        return df_goals_vs_xg
    

    def df_goals_against_vs_xga(self):
        gk_df = self.final_dataset[(self.final_dataset['position_name'] == 'Goalkeeper') & (self.final_dataset['minutes'] >=1 )]
        gk_df['expected_goals_conceded'] = gk_df['expected_goals_conceded'].astype(float)
        xGa_per_club = gk_df.groupby('team_name')['expected_goals_conceded'].sum()
        Ga_per_club = gk_df.groupby('team_name')['goals_conceded'].sum()
        df_goals_ag_vs_xga = pd.concat([xGa_per_club, Ga_per_club], axis=1)
        return df_goals_ag_vs_xga


    def df_fplpoints_split(self):
        total_pts = self.final_dataset['total_points'].sum()
        #positive points
        goal_pts=sum(self.final_dataset.groupby('position_name')['goals_scored'].sum()*[6,4,6,5])
        assist_pts = self.final_dataset['assists'].sum()*3
        penalty_save_pts = self.final_dataset[self.final_dataset['position_name'] == 'Goalkeeper']['penalties_saved'].sum()*5
        bps_pts = self.final_dataset['bonus'].sum()
        cs_pts = sum(self.final_dataset.groupby('position_name')['clean_sheets'].sum()*[4,0,4,1])
        start_pts = self.final_dataset['starts'].sum()*2
        saves_pts = round(self.final_dataset['saves'].sum()/3)
        sub_pts = len(self.final_dataset[(self.final_dataset['starts']==0) & (self.final_dataset['minutes'] > 0)])
        #negative points
        penalty_miss_pts = self.final_dataset['penalties_missed'].sum()*(-2)
        yc_pts = self.final_dataset['yellow_cards'].sum()*(-1)
        rc_pts = self.final_dataset['red_cards'].sum()*(-3)
        og_pts = self.final_dataset['own_goals'].sum()*(-2)
        small_pts = penalty_save_pts + penalty_miss_pts + og_pts

        points = [goal_pts, assist_pts, bps_pts, start_pts, sub_pts, cs_pts, saves_pts, yc_pts, rc_pts, small_pts]
        points = sorted(points, reverse = True)
        categories = ['> 60 minutes', 'Goals', 'Clean Sheets', 'Assists', 'Bonus points', '< 60 minutes', 'Saves', 'Penalty saves \n Penalty misses \n Own goals', 'Red cards', 'Yellow cards']
        percentages = [round(value / total_pts , 4) * 100 for value in points]
        df_categories_percentage = pd.DataFrame({"Action" : categories, "Percentage (%)" : percentages})
        return df_categories_percentage


###############   TO BE CONTINUED   #####################

    base_url = 'https://fantasy.premierleague.com/api/'

    def get_player_id(player):
        '''get player id for a given player based on full name'''

        from fuzzywuzzy import fuzz, process

        first_name, second_name = player.split()
        first_name = process.extractOne(first_name, player_dataset['first_name'])[0]
        second_name = process.extractOne(second_name, player_dataset['second_name'])[0]

        player_id = final_dataset.loc[(final_dataset['first_name'].isin([first_name])) & (final_dataset['second_name'].isin([second_name])), 'id_player'].values[0]

        return player_id





    def get_gameweek_history(player):
        '''get all gameweek info for a given player based on full name'''

        player_id = get_player_id(player)

        r = requests.get(
                base_url + 'element-summary/' + str(player_id) + '/').json()
        
        df = pd.json_normalize(r['history'])
        
        return df





    def get_season_history(player):
        '''get all past season info for a given player based on full name'''

        player_id = get_player_id(player)

        r = requests.get(
                base_url + 'element-summary/' + str(player_id) + '/').json()
        
        df = pd.json_normalize(r['history_past'])
        
        return df