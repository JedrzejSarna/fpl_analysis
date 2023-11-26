import requests
import pandas as pd
import numpy as np
import json
import pandas as pd
import fuzzywuzzy

class DATASETS:
    def __init__(self):
        self.url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        self.url_for_player= 'https://fantasy.premierleague.com/api/'
        response = requests.get(self.url)
        self.data = json.loads(response.text)

###############   BUILD DATASETS  #####################


    def build_players_dataset(self):
        players_dataset = pd.DataFrame.from_dict(self.data['elements'])
        players_dataset.drop(columns=['chance_of_playing_next_round','chance_of_playing_this_round','code',
                                      'cost_change_event', 'cost_change_event_fall', 'cost_change_start_fall',
                                      'in_dreamteam', 'news', 'news_added', 'photo', 'special', 'squad_number',
                                      'corners_and_indirect_freekicks_text','direct_freekicks_text','penalties_text',
                                      'first_name', 'second_name', 'team_code'], axis=1, inplace=True)
        self.players_dataset = players_dataset


    def build_teams_dataset(self):
        teams_dataset = pd.DataFrame.from_dict(self.data['teams'])
        relevant_columns_description_teams = ['id', 'name', 'short_name', 'strength', 'strength_overall_home', 'strength_overall_away', 
                                            'strength_attack_home', 'strength_attack_away', 'strength_defence_home', 'strength_defence_away']
        #subset for relevant columns
        teams_dataset = teams_dataset[relevant_columns_description_teams]
        teams_dataset.set_index('id', inplace=True)
        self.teams_dataset = teams_dataset


    def build_gameweeks_dataset(self):
        gameweeks_dataset = pd.DataFrame.from_dict(self.data['events'])
        gameweeks_dataset.drop(columns=['data_checked','highest_scoring_entry','deadline_time_epoch','deadline_time_game_offset','is_previous',
                                     'is_next','cup_leagues_created','h2h_ko_matches_created','most_selected'], axis=1, inplace=True)
        gameweeks_dataset.set_index('name', inplace=True)
        self.gameweeks_dataset =  gameweeks_dataset

    
    def build_positions_dataset(self):
        element_types_dataset = pd.DataFrame.from_dict(self.data['element_types'])
        element_types_dataset.drop(columns=['plural_name','plural_name_short','ui_shirt_specific','sub_positions_locked'], inplace=True)
        element_types_dataset.set_index('id', inplace=True)
        self.positions_dataset = element_types_dataset

###############   TRANSFORM DATASETS  #####################
    

    def transform_players_dataset(self):
        # join datasets
        position_names = self.positions_dataset[['singular_name', 'singular_name_short']]
        teams_names = self.teams_dataset[['name','short_name']]
        players_dataset = pd.merge(
            self.players_dataset,
            teams_names,
            left_on='team',
            right_on=teams_names.index,
        ).merge(
            position_names,
            left_on='element_type',
            right_on=position_names.index)
        # rename columns
        players_dataset = players_dataset.rename(columns={'name':'team_name', 'singular_name':'position_name', 'web_name':'player_name',
                                                          'cost_change_start':'price_change_start', 'ep_next':'exp_pts_next', 'ep_this':'exp_pts_this',
                                                          'now_cost':'price', 'influence_rank_type':'influence_rank_pos', 'creativity_rank_type':'creativity_rank_pos',
                                                          'threat_rank_type':'threat_rank_pos', 'ict_index_rank_type':'ict_index_rank_pos',
                                                          'corners_and_indirect_freekicks_order':'corners_order', 'now_cost_rank':'price_rank',
                                                          'now_cost_rank_type':'price_rank_pos', 'form_rank_type':'form_rank_pos',
                                                          'points_per_game_rank_type':'points_per_game_rank_pos', 'selected_rank_type':'selected_rank_pos',
                                                          'short_name':'team_name_short', 'singular_name_short':'position_name_short', 'id':'player_id'})
        players_dataset = players_dataset.drop(columns=['element_type', 'team'])
        players_dataset.sort_index(inplace=True)
        first_column = players_dataset.pop('player_name')
        players_dataset.insert(0, 'player_name', first_column)
        self.players_dataset = players_dataset


###############   SPECIFIC DATASETS  #####################


    def df_fplpoints_per_club(self):
        fpl_points_per_club = self.players_dataset.groupby('team_name')['total_points'].sum()
        return fpl_points_per_club


    def df_fplpoints_per_position(self):
        played_already = self.players_dataset[self.players_dataset['minutes'] >= 1]
        fpl_points_per_position = played_already.groupby('position_name')['total_points'].agg(['sum', 'mean', 'count']).reindex(['Goalkeeper', 'Defender', 'Midfielder', 'Forward'])
        return fpl_points_per_position


    def df_goals_vs_xg(self):
        self.players_dataset['expected_goals'] = self.players_dataset['expected_goals'].astype(float)
        xG_per_club = self.players_dataset.groupby('team_name')['expected_goals'].sum()
        G_per_club = self.players_dataset.groupby('team_name')['goals_scored'].sum()
        df_goals_vs_xg = pd.concat([xG_per_club, G_per_club], axis=1)
        return df_goals_vs_xg
    

    def df_goals_against_vs_xga(self):
        gk_df = self.players_dataset[(self.players_dataset['position_name'] == 'Goalkeeper') & (self.players_dataset['minutes'] >=1 )]
        gk_df['expected_goals_conceded'] = gk_df['expected_goals_conceded'].astype(float)
        xGa_per_club = gk_df.groupby('team_name')['expected_goals_conceded'].sum()
        Ga_per_club = gk_df.groupby('team_name')['goals_conceded'].sum()
        df_goals_ag_vs_xga = pd.concat([xGa_per_club, Ga_per_club], axis=1)
        return df_goals_ag_vs_xga


    def df_fplpoints_split(self):
        total_pts = self.players_dataset['total_points'].sum()
        #positive points
        goal_pts=sum(self.players_dataset.groupby('position_name')['goals_scored'].sum()*[6,4,6,5])
        assist_pts = self.players_dataset['assists'].sum()*3
        penalty_save_pts = self.players_dataset[self.players_dataset['position_name'] == 'Goalkeeper']['penalties_saved'].sum()*5
        bps_pts = self.players_dataset['bonus'].sum()
        cs_pts = sum(self.players_dataset.groupby('position_name')['clean_sheets'].sum()*[4,0,4,1])
        start_pts = self.players_dataset['starts'].sum()*2
        saves_pts = round(self.players_dataset['saves'].sum()/3)
        sub_pts = len(self.players_dataset[(self.players_dataset['starts']==0) & (self.players_dataset['minutes'] > 0)])
        #negative points
        penalty_miss_pts = self.players_dataset['penalties_missed'].sum()*(-2)
        yc_pts = self.players_dataset['yellow_cards'].sum()*(-1)
        rc_pts = self.players_dataset['red_cards'].sum()*(-3)
        og_pts = self.players_dataset['own_goals'].sum()*(-2)
        small_pts = penalty_save_pts + penalty_miss_pts + og_pts

        points = [goal_pts, assist_pts, bps_pts, start_pts, sub_pts, cs_pts, saves_pts, yc_pts, rc_pts, small_pts]
        points = sorted(points, reverse = True)
        categories = ['> 60 minutes', 'Goals', 'Clean Sheets', 'Assists', 'Bonus points', '< 60 minutes', 'Saves', 'Penalty saves \n Penalty misses \n Own goals', 'Red cards', 'Yellow cards']
        percentages = [round(value / total_pts , 4) * 100 for value in points]
        df_categories_percentage = pd.DataFrame({"Action" : categories, "Percentage (%)" : percentages})
        return df_categories_percentage


###############   PLAYERS DATASET  #####################

    def get_player_id(self, player):
        '''get player id for a given player based on full name'''
        from fuzzywuzzy import fuzz, process
        name = process.extractOne(player, self.players_dataset['player_name'])
        player_id = self.players_dataset.loc[self.players_dataset['player_name'].isin(name), 'player_id'].values[0]
        return player_id

    def get_player_json(self, player):
        '''get json file of player'''
        json_file = requests.get(self.url_for_player + 'element-summary/' + str(self.get_player_id(player)) + '/').json()
        return json_file


    def df_player_season(self, player):
        '''get all season info for a given player based on full name'''
        df_player_season = pd.json_normalize(self.get_player_json(player)['history'])
        df_player_season.drop(columns=['element', 'fixture', 'round'], inplace=True)
        temp_dict= dict(zip(self.teams_dataset.index,self.teams_dataset['name']))
        df_player_season['opponent_team'] = df_player_season['opponent_team'].map(temp_dict)
        return df_player_season
    
    def df_player_past_seasons(self, player):
        '''get all past seasons info for a given player based on full name'''
        df_player_past_seasons = pd.json_normalize(self.get_player_json(player)['history_past'])
        df_player_past_seasons.drop(columns=['element_code'], inplace=True)
        return df_player_past_seasons
    
    def df_player_upcom_fixtures(self, player):
        '''get all remaining fixtures info for a given player based on full name'''
        df_player_fixtures = pd.json_normalize(self.get_player_json(player)['fixtures'])
        df_player_fixtures.drop(columns=['id', 'code', 'team_h_score', 'team_a_score', 'event', 'finished', 'minutes', 'provisional_start_time'], inplace = True)
        temp_dict= dict(zip(self.teams_dataset.index, self.teams_dataset['name']))
        df_player_fixtures['team_h'] = df_player_fixtures['team_h'].map(temp_dict)
        df_player_fixtures['team_a'] = df_player_fixtures['team_a'].map(temp_dict)
        first_column = df_player_fixtures.pop('event_name')
        df_player_fixtures.insert(0, 'event_name', first_column)
        return df_player_fixtures

###############  SPECIFIC PLAYERS DATASET  #####################


    def df_best_player_per_team_pts(self):
        max_pts_index = self.players_dataset.groupby('team_name')['total_points'].idxmax()
        df_best_pts = self.players_dataset.loc[max_pts_index, ['player_name', 'total_points']]
        temp_dict={}
        for player in df_best_pts['player_name']:
            temp_dict[player] = np.cumsum(list(self.df_player_season(player)['total_points']))
        df_player_pts = pd.DataFrame(temp_dict)
        df_player_pts.index = range(1, df_player_pts.shape[0] + 1)
        return df_player_pts
    
    def df_top5_player_pts(self):
        max_pts_index = self.players_dataset.groupby('team_name')['total_points'].idxmax()
        df_best_pts = self.players_dataset.loc[max_pts_index, ['player_name', 'total_points']]
        df_top5_pts = df_best_pts.nlargest(5, 'total_points')
        temp_dict={}
        for player in df_top5_pts['player_name']:
            temp_dict[player] = np.cumsum(list(self.df_player_season(player)['total_points']))
        df_player_pts = pd.DataFrame(temp_dict)
        df_player_pts.index = range(1, df_player_pts.shape[0] + 1)
        return df_player_pts
    
    def df_top5_defender_pts(self):
        max_pts_index = self.players_dataset[self.players_dataset['position_name']=='Defender'].groupby('team_name')['total_points'].idxmax()
        df_best_pts = self.players_dataset.loc[max_pts_index, ['player_name', 'total_points']]
        df_top5_pts = df_best_pts.nlargest(5, 'total_points')
        temp_dict={}
        for player in df_top5_pts['player_name']:
            temp_dict[player] = np.cumsum(list(self.df_player_season(player)['total_points']))
        df_player_pts = pd.DataFrame(temp_dict)
        df_player_pts.index = range(1, df_player_pts.shape[0] + 1)
        return df_player_pts
    

    def df_top5_midfielder_pts(self):
        max_pts_index = self.players_dataset[self.players_dataset['position_name']=='Midfielder'].groupby('team_name')['total_points'].idxmax()
        df_best_pts = self.players_dataset.loc[max_pts_index, ['player_name', 'total_points']]
        df_top5_pts = df_best_pts.nlargest(5, 'total_points')
        temp_dict={}
        for player in df_top5_pts['player_name']:
            temp_dict[player] = np.cumsum(list(self.df_player_season(player)['total_points']))
        df_player_pts = pd.DataFrame(temp_dict)
        df_player_pts.index = range(1, df_player_pts.shape[0] + 1)
        return df_player_pts
    

    def df_top5_forward_pts(self):
        max_pts_index = self.players_dataset[self.players_dataset['position_name']=='Forward'].groupby('team_name')['total_points'].idxmax()
        df_best_pts = self.players_dataset.loc[max_pts_index, ['player_name', 'total_points']]
        df_top5_pts = df_best_pts.nlargest(5, 'total_points')
        temp_dict={}
        for player in df_top5_pts['player_name']:
            temp_dict[player] = np.cumsum(list(self.df_player_season(player)['total_points']))
        df_player_pts = pd.DataFrame(temp_dict)
        df_player_pts.index = range(1, df_player_pts.shape[0] + 1)
        return df_player_pts